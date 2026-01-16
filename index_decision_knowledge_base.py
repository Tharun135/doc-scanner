#!/usr/bin/env python3
"""
Index Decision-Focused Knowledge Base to ChromaDB
Loads the 223 decision chunks from data/knowledge_base.json into your existing ChromaDB.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    print("❌ ChromaDB not installed. Run: pip install chromadb")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️  sentence-transformers not installed. Using ChromaDB's default embeddings.")
    EMBEDDINGS_AVAILABLE = False

from app.decision_chunk import DecisionChunk


class DecisionKnowledgeBaseIndexer:
    """Indexes decision chunks to ChromaDB vector store."""
    
    def __init__(
        self, 
        db_path: str = "./chroma_db",
        collection_name: str = "docscanner_knowledge",
        kb_file: str = "data/knowledge_base.json"
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.kb_file = kb_file
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    def load_knowledge_base(self) -> Dict:
        """Load the decision knowledge base JSON."""
        print(f"\n📂 Loading knowledge base from {self.kb_file}...")
        
        if not Path(self.kb_file).exists():
            print(f"❌ Knowledge base file not found: {self.kb_file}")
            print(f"   Run: python build_knowledge_base.py")
            sys.exit(1)
        
        with open(self.kb_file, 'r', encoding='utf-8') as f:
            kb = json.load(f)
        
        print(f"✅ Loaded {len(kb['chunks'])} chunks")
        print(f"   Generated: {kb['metadata']['generated_at']}")
        
        return kb
    
    def connect_to_chromadb(self):
        """Connect to existing ChromaDB instance."""
        print(f"\n🔌 Connecting to ChromaDB at {self.db_path}...")
        
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            print(f"✅ Connected to ChromaDB")
            
            # List existing collections
            existing_collections = self.client.list_collections()
            print(f"   Existing collections: {[c.name for c in existing_collections]}")
            
            # Get the main collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                existing_count = self.collection.count()
                print(f"✅ Found existing collection '{self.collection_name}' with {existing_count} documents")
                print(f"   Will append decision chunks (use --replace to recreate collection)")
                    
            except ValueError:
                # Collection doesn't exist
                print(f"📝 Creating new collection '{self.collection_name}'...")
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "DocScanner Decision-Focused Knowledge Base"}
                )
                print(f"✅ Created collection")
                
        except Exception as e:
            print(f"❌ Failed to connect to ChromaDB: {e}")
            sys.exit(1)
    
    def init_embedding_model(self):
        """Initialize embedding model if available."""
        if not EMBEDDINGS_AVAILABLE:
            print("\n⚠️  Using ChromaDB's default embeddings (sentence-transformers not installed)")
            return
        
        print(f"\n🧠 Loading embedding model...")
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print(f"✅ Loaded sentence-transformers model")
        except Exception as e:
            print(f"⚠️  Failed to load embedding model: {e}")
            print(f"   Will use ChromaDB's default embeddings")
            self.embedding_model = None
    
    def index_chunks(self, chunks_data: List[Dict]) -> int:
        """Index all chunks to ChromaDB."""
        print(f"\n📥 Indexing {len(chunks_data)} chunks to ChromaDB...")
        
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        # Check which chunks already exist
        try:
            existing_ids = set(self.collection.get()['ids'])
            print(f"   Found {len(existing_ids)} existing documents")
        except:
            existing_ids = set()
        
        # Batch processing for efficiency
        batch_size = 100
        
        for i in range(0, len(chunks_data), batch_size):
            batch = chunks_data[i:i + batch_size]
            
            batch_docs = []
            batch_metadatas = []
            batch_ids = []
            
            for chunk_data in batch:
                try:
                    # Convert to DecisionChunk for validation
                    chunk = DecisionChunk(**chunk_data)
                    
                    # Skip if already indexed
                    if chunk.id in existing_ids:
                        skipped_count += 1
                        continue
                    
                    # Get embedding text (question + answer)
                    embedding_text = chunk.get_embedding_text()
                    
                    # Get metadata for filtering
                    metadata = chunk.get_metadata_for_filtering()
                    
                    batch_docs.append(embedding_text)
                    batch_metadatas.append(metadata)
                    batch_ids.append(chunk.id)
                    
                except Exception as e:
                    error_count += 1
                    print(f"   ⚠️  Error processing chunk: {e}")
                    continue
            
            # Add batch to collection
            if batch_docs:
                try:
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metadatas,
                        ids=batch_ids
                    )
                    indexed_count += len(batch_docs)
                    
                    # Progress indicator
                    print(f"   Progress: {min(i + batch_size, len(chunks_data))}/{len(chunks_data)} chunks processed...", end='\r')
                    
                except Exception as e:
                    error_count += len(batch_docs)
                    print(f"\n   ❌ Error indexing batch: {e}")
        
        print()  # New line after progress
        return indexed_count, skipped_count, error_count
    
    def verify_indexing(self):
        """Verify that chunks were indexed correctly."""
        print(f"\n🔍 Verifying indexing...")
        
        try:
            total_count = self.collection.count()
            print(f"✅ Collection now has {total_count} total documents")
            
            # Test a sample query
            print(f"\n🧪 Testing sample query: 'passive voice detection'...")
            results = self.collection.query(
                query_texts=["passive voice detection"],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                print(f"✅ Query returned {len(results['documents'][0])} results")
                print(f"\n   Top result preview:")
                print(f"   {results['documents'][0][0][:150]}...")
                
                if results['metadatas'] and results['metadatas'][0]:
                    print(f"\n   Metadata:")
                    for key, value in results['metadatas'][0][0].items():
                        print(f"     {key}: {value}")
            else:
                print(f"⚠️  Query returned no results")
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
    
    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("📚 DECISION KNOWLEDGE BASE INDEXER")
        print("=" * 60)
        
        # Load knowledge base
        kb = self.load_knowledge_base()
        
        # Connect to ChromaDB
        self.connect_to_chromadb()
        
        # Initialize embeddings (optional)
        self.init_embedding_model()
        
        # Index chunks
        indexed, skipped, errors = self.index_chunks(kb['chunks'])
        
        # Verify
        self.verify_indexing()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INDEXING COMPLETE")
        print("=" * 60)
        print(f"   ✅ Indexed: {indexed} new chunks")
        print(f"   ⏭️  Skipped: {skipped} existing chunks")
        print(f"   ❌ Errors: {errors} chunks")
        print(f"   📦 Total in collection: {self.collection.count()} documents")
        print()
        print(f"💡 Next steps:")
        print(f"   1. Refresh your RAG dashboard - should show {self.collection.count()} chunks")
        print(f"   2. Test search: python evaluate_knowledge_base.py")
        print(f"   3. Integrate decision logging: see EXECUTION_CHECKLIST.md")
        print()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Index decision-focused knowledge base to ChromaDB"
    )
    parser.add_argument(
        '--db-path',
        default='./chroma_db',
        help='Path to ChromaDB database (default: ./chroma_db)'
    )
    parser.add_argument(
        '--collection',
        default='docscanner_knowledge',
        help='Collection name (default: docscanner_knowledge)'
    )
    parser.add_argument(
        '--kb-file',
        default='data/knowledge_base.json',
        help='Knowledge base JSON file (default: data/knowledge_base.json)'
    )
    
    args = parser.parse_args()
    
    indexer = DecisionKnowledgeBaseIndexer(
        db_path=args.db_path,
        collection_name=args.collection,
        kb_file=args.kb_file
    )
    
    indexer.run()


if __name__ == "__main__":
    main()
