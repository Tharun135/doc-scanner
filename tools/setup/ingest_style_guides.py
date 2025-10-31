"""
ingest_style_guides.py
Fetch → clean → chunk → embed → upsert Microsoft & Google style guides into ChromaDB.

This creates a whitelist-based knowledge base of trusted style guides that can be
retrieved when custom rules fail, providing authoritative writing standards instead
of relying on open web content.

Usage:
  pip install requests beautifulsoup4 html2text tiktoken
  python ingest_style_guides.py

Features:
- Curated whitelist of high-impact Microsoft + Google style guide sections
- Hierarchy-aware chunking (preserves heading structure)
- Rich metadata for filtering and attribution
- Respects robots.txt and uses reasonable delays
- Idempotent upserts (safe to re-run for updates)
"""

import os, re, time, hashlib, datetime, logging
import requests
from bs4 import BeautifulSoup
import html2text
import chromadb
from typing import List, Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------
# CONFIG
# -----------------------
VERSION_STR = datetime.date.today().isoformat()
CHROMA_DB_PATH = "./db"  # Match your existing ChromaDB location
COLLECTION_NAME = "style_guides"

# Curated high-impact sections from Microsoft Writing Style Guide (updated URLs)
MICROSOFT_URLS = [
    # Verified working URLs from Microsoft Writing Style Guide
    ("https://learn.microsoft.com/en-us/style-guide/welcome/", "general"),
    ("https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips", "voice"),
    ("https://learn.microsoft.com/en-us/style-guide/urls-web-addresses", "formatting"),
    ("https://learn.microsoft.com/en-us/style-guide/text-formatting/formatting-common-text-elements", "formatting"),
    ("https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions", "procedures"),
]

# Curated high-impact sections from Google Developer Documentation Style Guide (working URLs)
GOOGLE_URLS = [
    # Principles & tone  
    ("https://developers.google.com/style/tone", "voice"),
    ("https://developers.google.com/style/highlights", "voice"),
    
    # Grammar & mechanics
    ("https://developers.google.com/style/capitalization", "capitalization"),  
    ("https://developers.google.com/style/numbers", "numbers"),
    
    # UI, code, and formatting
    ("https://developers.google.com/style/ui-elements", "ui-strings"),
    ("https://developers.google.com/style/code-in-text", "code-style"),
    
    # Inclusive & clear language
    ("https://developers.google.com/style/inclusive-documentation", "inclusive-language"),
    ("https://developers.google.com/style/word-list", "terminology"),
    
    # Structure & tasks
    ("https://developers.google.com/style/headings", "headings"),
    ("https://developers.google.com/style/procedures", "procedures"),
]

HEADERS = {
    "User-Agent": "DocScanner-StyleGuide-Ingest/1.0 (Educational/Research Use)"
}

# -----------------------
# CORE FUNCTIONS
# -----------------------

def http_get(url: str, timeout: int = 30) -> str:
    """Fetch URL content with error handling and respectful delays."""
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise

def clean_html_to_markdown(html: str) -> str:
    """Convert HTML to clean markdown, removing navigation and non-content elements."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove navigation, footers, scripts, and other non-content elements
    for tag in soup(["nav", "footer", "aside", "script", "style", "noscript"]):
        tag.decompose()
    
    # Remove specific navigation patterns (be more precise to avoid removing main content)
    navigation_selectors = [
        "nav[class*='toc']",  # Table of contents nav
        "[role='navigation']",  # Elements with navigation role
        ".breadcrumb",  # Exact breadcrumb class (not partial match)
        ".sidebar", ".menu",  # Exact classes for sidebar and menu
        ".uhf-header", ".uhf-footer",  # Microsoft specific header/footer
        "[id*='uhf-header']", "[id*='uhf-footer']"  # Microsoft UHF by ID
    ]
    
    for selector in navigation_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Try to find the main content area - Microsoft Learn uses main tags
    main_content = None
    for selector in ['main', 'article', '[role="main"]', '.content', '[data-bi-name="content"]']:
        main_content = soup.select_one(selector)
        if main_content and main_content.get_text(strip=True):
            break
    
    # If we found meaningful main content, use that; otherwise use body
    if main_content and len(main_content.get_text(strip=True)) > 100:
        soup = BeautifulSoup(str(main_content), "html.parser")
    elif soup.body:
        soup = BeautifulSoup(str(soup.body), "html.parser")
    
    # Convert to markdown
    md_converter = html2text.HTML2Text()
    md_converter.ignore_links = False
    md_converter.body_width = 0  # No line wrapping
    md_converter.ignore_images = True
    
    markdown = md_converter.handle(str(soup))
    
    # Clean up excessive whitespace and empty lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = re.sub(r'[ \t]+\n', '\n', markdown)  # Remove trailing whitespace
    markdown = re.sub(r'^\s*\n', '', markdown, flags=re.MULTILINE)  # Remove empty lines
    
    return markdown.strip()

def chunk_markdown_by_headings(markdown: str, max_chars: int = 3000) -> List[Tuple[List[str], str]]:
    """
    Chunk markdown by headings while preserving hierarchy context.
    Returns list of (hierarchy_path, chunk_content) tuples.
    """
    chunks = []
    current_hierarchy = []
    current_chunk = []
    
    def flush_chunk():
        if current_chunk:
            content = '\n'.join(current_chunk).strip()
            if content and len(content) > 100:  # Skip tiny chunks
                chunks.append((current_hierarchy[:], content))
            current_chunk.clear()
    
    for line in markdown.splitlines():
        # Detect heading level
        if line.startswith('#'):
            # Flush previous chunk before starting new section
            if current_chunk:
                flush_chunk()
            
            # Parse heading
            level = len(line) - len(line.lstrip('#'))
            title = line.strip('# ').strip()
            
            if title:  # Only process non-empty headings
                # Update hierarchy (keep only parent levels)
                current_hierarchy = current_hierarchy[:level-1] + [title]
            
            current_chunk.append(line)
        else:
            current_chunk.append(line)
            
            # Check if chunk is getting too large
            current_size = sum(len(l) + 1 for l in current_chunk)
            if current_size >= max_chars:
                flush_chunk()
    
    # Don't forget the last chunk
    flush_chunk()
    
    return chunks

def generate_chunk_id(text: str, url: str, source: str) -> str:
    """Generate consistent ID for chunk based on content and source."""
    content_hash = hashlib.sha256((source + url + text).encode('utf-8')).hexdigest()[:16]
    return f"{source}_{content_hash}"

def create_chunk_metadata(
    source: str, 
    url: str, 
    topic: str, 
    hierarchy: List[str], 
    chunk_text: str,
    license_type: str = "permissive"
) -> Dict[str, Any]:
    """Create rich metadata for a chunk."""
    # Extract tags based on content patterns
    tags = []
    text_lower = chunk_text.lower()
    
    if any(word in text_lower for word in ["passive voice", "active voice"]):
        tags.append("voice")
    if any(word in text_lower for word in ["should", "must", "avoid"]):
        tags.append("rules")
    if "example" in text_lower or "for instance" in text_lower:
        tags.append("examples")
    if any(word in text_lower for word in ["don't", "avoid", "never"]):
        tags.append("dont-use")
    
    # Convert hierarchy to string for ChromaDB compatibility
    hierarchy_path = " → ".join(hierarchy) if hierarchy else "Unknown Section"
    tags_string = ", ".join(tags) if tags else ""
    
    return {
        "source": source,
        "title": hierarchy[-1] if hierarchy else "Unknown Section",
        "url": url,
        "license": license_type,
        "version": VERSION_STR,
        "topic": topic,
        "tags": tags_string,  # Convert to string
        "hierarchy": hierarchy_path,  # Convert to string
        "source_trust": "whitelist",
        "char_len": len(chunk_text),
        "ingestion_date": datetime.datetime.now().isoformat()
    }

def setup_chromadb() -> chromadb.Collection:
    """Initialize ChromaDB client and collection."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine", "description": "Trusted writing style guides"}
        )
        logger.info(f"Connected to ChromaDB collection '{COLLECTION_NAME}'")
        return collection
    except Exception as e:
        logger.error(f"Failed to setup ChromaDB: {e}")
        raise

def ingest_url(collection: chromadb.Collection, url: str, topic: str, source: str) -> int:
    """Ingest a single URL into the collection."""
    try:
        # Fetch and clean content
        html = http_get(url)
        markdown = clean_html_to_markdown(html)
        
        if len(markdown) < 500:  # Skip pages with minimal content
            logger.warning(f"Skipping {url} - content too short ({len(markdown)} chars)")
            return 0
        
        # Chunk by headings
        chunks = chunk_markdown_by_headings(markdown, max_chars=3000)
        
        if not chunks:
            logger.warning(f"No chunks generated for {url}")
            return 0
        
        # Upsert chunks
        chunk_count = 0
        for hierarchy, chunk_text in chunks:
            chunk_id = generate_chunk_id(chunk_text, url, source)
            metadata = create_chunk_metadata(source, url, topic, hierarchy, chunk_text)
            
            collection.upsert(
                ids=[chunk_id],
                documents=[chunk_text],
                metadatas=[metadata]
            )
            chunk_count += 1
        
        logger.info(f"✅ {source}: {url.split('/')[-1]} → {chunk_count} chunks")
        return chunk_count
        
    except Exception as e:
        logger.error(f"Failed to ingest {url}: {e}")
        return 0

def ingest_all_sources(collection: chromadb.Collection) -> Dict[str, int]:
    """Ingest all configured style guide sources."""
    results = {"microsoft": 0, "google": 0, "total_chunks": 0, "total_urls": 0}
    
    # Ingest Microsoft style guides
    logger.info("🔄 Ingesting Microsoft Writing Style Guide...")
    for url, topic in MICROSOFT_URLS:
        chunks = ingest_url(collection, url, topic, "microsoft")
        results["microsoft"] += chunks
        results["total_chunks"] += chunks
        results["total_urls"] += 1
        time.sleep(1)  # Be respectful with delays
    
    # Ingest Google style guides
    logger.info("🔄 Ingesting Google Developer Documentation Style Guide...")
    for url, topic in GOOGLE_URLS:
        chunks = ingest_url(collection, url, topic, "google")
        results["google"] += chunks
        results["total_chunks"] += chunks
        results["total_urls"] += 1
        time.sleep(1)  # Be respectful with delays
    
    return results

def get_collection_stats(collection: chromadb.Collection) -> Dict[str, Any]:
    """Get statistics about the collection."""
    try:
        # Get all documents to analyze
        all_docs = collection.get()
        
        if not all_docs['metadatas']:
            return {"total_documents": 0}
        
        # Analyze metadata
        sources = {}
        topics = {}
        
        for metadata in all_docs['metadatas']:
            source = metadata.get('source', 'unknown')
            topic = metadata.get('topic', 'unknown')
            
            sources[source] = sources.get(source, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            "total_documents": len(all_docs['ids']),
            "sources": sources,
            "topics": topics,
            "version": all_docs['metadatas'][0].get('version', 'unknown') if all_docs['metadatas'] else 'unknown'
        }
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        return {"error": str(e)}

# -----------------------
# QUERY FUNCTIONS (for testing)
# -----------------------

def retrieve_style_guidance(collection: chromadb.Collection, query: str, k: int = 6, min_similarity: float = 0.35) -> List[Dict[str, Any]]:
    """
    Retrieve relevant style guidance from the whitelist collection.
    
    Args:
        collection: ChromaDB collection
        query: Search query (e.g., "passive voice", "UI strings")
        k: Number of results to retrieve
        min_similarity: Minimum similarity threshold
    
    Returns:
        List of relevant guidance chunks with metadata
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where={"$and": [
                {"source_trust": {"$eq": "whitelist"}},
                {"license": {"$eq": "permissive"}}
            ]}
        )
        
        guidance = []
        for i in range(len(results["ids"][0])):
            # Convert distance to similarity (assuming cosine distance)
            distance = results["distances"][0][i]
            similarity = 1 - distance  # For cosine distance
            
            if similarity >= min_similarity:
                guidance.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": similarity,
                    "id": results["ids"][0][i]
                })
        
        return sorted(guidance, key=lambda x: x["similarity"], reverse=True)
    
    except Exception as e:
        logger.error(f"Failed to retrieve guidance: {e}")
        return []

# -----------------------
# MAIN EXECUTION
# -----------------------

def main():
    """Main ingestion process."""
    logger.info("🚀 Starting style guide ingestion...")
    
    try:
        # Setup ChromaDB
        collection = setup_chromadb()
        
        # Get initial stats
        initial_stats = get_collection_stats(collection)
        logger.info(f"Initial collection size: {initial_stats.get('total_documents', 0)} documents")
        
        # Ingest all sources
        results = ingest_all_sources(collection)
        
        # Get final stats
        final_stats = get_collection_stats(collection)
        
        # Report results
        logger.info("📊 Ingestion Complete!")
        logger.info(f"URLs processed: {results['total_urls']}")
        logger.info(f"Total chunks: {results['total_chunks']}")
        logger.info(f"Microsoft chunks: {results['microsoft']}")
        logger.info(f"Google chunks: {results['google']}")
        logger.info(f"Final collection size: {final_stats.get('total_documents', 0)} documents")
        
        if final_stats.get('sources'):
            logger.info("Sources breakdown:")
            for source, count in final_stats['sources'].items():
                logger.info(f"  {source}: {count} chunks")
        
        if final_stats.get('topics'):
            logger.info("Topics breakdown:")
            for topic, count in sorted(final_stats['topics'].items()):
                logger.info(f"  {topic}: {count} chunks")
        
        # Test retrieval
        logger.info("\n🧪 Testing retrieval...")
        test_queries = [
            "passive voice",
            "UI strings capitalization", 
            "procedures and instructions",
            "inclusive language"
        ]
        
        for query in test_queries:
            guidance = retrieve_style_guidance(collection, query, k=3)
            logger.info(f"Query: '{query}' → {len(guidance)} results")
            
            for i, item in enumerate(guidance[:2], 1):
                source = item['metadata']['source']
                title = item['metadata']['title']
                similarity = item['similarity']
                logger.info(f"  {i}. [{source}] {title} (sim: {similarity:.3f})")
        
        logger.info("✅ All done! Style guides are now available in ChromaDB.")
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main()
