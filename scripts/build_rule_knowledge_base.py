#!/usr/bin/env python3
"""
Rule Knowledge Base Builder
Converts all rule files to text chunks with embeddings and stores in ChromaDB.
"""

import os
import sys
import re
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import google.generativeai as genai
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_chroma import Chroma
    from langchain.schema import Document
    from dotenv import load_dotenv
    DEPS_AVAILABLE = True
except ImportError as e:
    try:
        # Fallback to old import
        import google.generativeai as genai
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain.schema import Document
        from dotenv import load_dotenv
        DEPS_AVAILABLE = True
    except ImportError as e2:
        print(f"❌ Missing dependencies: {e2}")
        print("Install with: pip install langchain-google-genai chromadb python-dotenv")
        DEPS_AVAILABLE = False

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RuleKnowledgeBuilder:
    """Builds a searchable knowledge base from rule files."""
    
    def __init__(self):
        self.rules = []
        self.vectorstore = None
        self.embeddings = None
        self.rules_dir = Path(__file__).parent / 'app' / 'rules'
        self.temp_dir = tempfile.mkdtemp()
        
        if DEPS_AVAILABLE:
            self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize Google embeddings."""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print("❌ No Google API key found. Set GOOGLE_API_KEY environment variable.")
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
            
            # Initialize ChromaDB with persistent directory in project root
            self.project_root = os.path.dirname(os.path.abspath(__file__))
            persist_dir = os.path.join(self.project_root, "rule_knowledge_base")
            os.makedirs(persist_dir, exist_ok=True)
            
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=persist_dir
            )
            
            print(f"✅ Google embeddings and ChromaDB initialized at {persist_dir}")
            
        except Exception as e:
            print(f"❌ Failed to initialize embeddings: {e}")
            self.vectorstore = None
    
    def extract_rule_info(self, rule_file_path: Path) -> Dict[str, Any]:
        """Extract rule information from a rule file."""
        try:
            with open(rule_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rule_name = rule_file_path.stem
            rule_id = f"rule-{rule_name.replace('_', '-')}"
            
            # Extract rule patterns and messages
            patterns = []
            suggestions = []
            examples = []
            
            # Find regex patterns
            pattern_matches = re.findall(r'r[\'"]([^\'\"]+)[\'"]', content)
            patterns.extend(pattern_matches[:5])  # Limit to first 5 patterns
            
            # Find suggestion messages
            suggestion_matches = re.findall(r'suggestions\.append\([\'"]([^\'\"]+)[\'"]', content)
            suggestions.extend(suggestion_matches[:5])  # Limit to first 5 suggestions
            
            # Find example text in comments
            example_matches = re.findall(r'#.*[Ee]xample[:\s]*([^#\n]+)', content)
            examples.extend([ex.strip() for ex in example_matches[:3]])
            
            # Generate title from filename
            title = rule_name.replace('_', ' ').title()
            
            # Generate description from docstring or comments
            description = self._extract_description(content)
            
            # Extract tags based on rule type
            tags = self._generate_tags(rule_name, content)
            
            return {
                "id": rule_id,
                "title": title,
                "description": description,
                "patterns": patterns,
                "suggestions": suggestions,
                "examples": examples,
                "tags": tags,
                "file_name": rule_file_path.name
            }
            
        except Exception as e:
            logger.error(f"Error extracting info from {rule_file_path}: {e}")
            return None
    
    def _extract_description(self, content: str) -> str:
        """Extract description from docstring or comments."""
        # Try to find docstring
        docstring_match = re.search(r'"""([^"]+)"""', content)
        if docstring_match:
            return docstring_match.group(1).strip()
        
        # Try to find rule comments
        rule_comments = re.findall(r'# Rule[:\s]*([^#\n]+)', content)
        if rule_comments:
            return ". ".join(rule_comments[:2])
        
        # Fallback to general comments
        comments = re.findall(r'#\s*([^#\n]+)', content)
        meaningful_comments = [c.strip() for c in comments if len(c.strip()) > 10 and not c.strip().startswith('Load')]
        
        if meaningful_comments:
            return meaningful_comments[0]
        
        return "Writing style and grammar rule"
    
    def _generate_tags(self, rule_name: str, content: str) -> List[str]:
        """Generate tags based on rule name and content."""
        tags = []
        
        # Tags based on rule name
        name_tags = {
            'passive_voice': ['style', 'voice', 'clarity'],
            'long_sentences': ['readability', 'length', 'structure'],
            'can_may_terms': ['grammar', 'modal-verbs', 'precision'],
            'special_characters': ['formatting', 'symbols', 'typography'],
            'style_guide': ['style', 'consistency', 'formatting'],
            'accessibility': ['accessibility', 'inclusive', 'design'],
            'security': ['security', 'terminology', 'technical'],
            'technical': ['technical', 'terminology', 'accuracy'],
            'grammar': ['grammar', 'syntax', 'correctness'],
            'contractions': ['grammar', 'formality', 'style'],
            'mouse_interaction': ['ui', 'interaction', 'terminology'],
            'keyboard': ['ui', 'interaction', 'shortcuts'],
            'terminology': ['terminology', 'consistency', 'accuracy']
        }
        
        for key, key_tags in name_tags.items():
            if key in rule_name:
                tags.extend(key_tags)
        
        # Tags based on content analysis
        if 'passive' in content.lower():
            tags.append('passive-voice')
        if 'sentence' in content.lower():
            tags.append('sentence-structure')
        if 'ui' in content.lower() or 'interface' in content.lower():
            tags.append('ui')
        if 'accessibility' in content.lower():
            tags.append('accessibility')
        
        # Remove duplicates and limit
        return list(set(tags))[:5]
    
    def rule_to_text(self, rule: Dict[str, Any]) -> str:
        """Convert rule to searchable text."""
        text_parts = [
            f"RULE: {rule['title']}",
            f"DESCRIPTION: {rule['description']}"
        ]
        
        if rule['suggestions']:
            text_parts.append(f"GUIDANCE: {'. '.join(rule['suggestions'][:2])}")
        
        if rule['examples']:
            text_parts.append(f"EXAMPLES: {'. '.join(rule['examples'][:2])}")
        
        if rule['patterns']:
            text_parts.append(f"PATTERNS: Detects {', '.join(rule['patterns'][:3])}")
        
        if rule['tags']:
            text_parts.append(f"CATEGORIES: {', '.join(rule['tags'])}")
        
        return "\n".join(text_parts)
    
    def build_knowledge_base(self):
        """Build the complete knowledge base from all rule files."""
        if not DEPS_AVAILABLE:
            print("❌ Cannot build knowledge base without dependencies")
            return
        
        if self.embeddings is None or self.vectorstore is None:
            print(f"❌ Cannot build knowledge base - embeddings: {self.embeddings is not None}, vectorstore: {self.vectorstore is not None}")
            return
        
        print("🔍 Scanning rule files...")
        
        # Skip utility files
        skip_files = {'__init__.py', 'rag_rule_helper.py', 'spacy_utils.py'}
        rule_files = [f for f in self.rules_dir.glob('*.py') if f.name not in skip_files]
        
        print(f"Found {len(rule_files)} rule files")
        
        documents = []
        
        for rule_file in rule_files:
            print(f"📝 Processing {rule_file.name}...")
            
            rule_info = self.extract_rule_info(rule_file)
            if rule_info:
                self.rules.append(rule_info)
                
                # Convert to text and create document
                text = self.rule_to_text(rule_info)
                
                doc = Document(
                    page_content=text,
                    metadata={
                        "id": rule_info["id"],
                        "title": rule_info["title"],
                        "tags": ", ".join(rule_info["tags"]),  # Convert list to string
                        "file_name": rule_info["file_name"],
                        "type": "writing_rule"
                    }
                )
                documents.append(doc)
        
        # Add documents to ChromaDB
        if documents:
            print(f"📚 Adding {len(documents)} rules to knowledge base...")
            try:
                self.vectorstore.add_documents(documents)
                print("✅ Knowledge base created successfully!")
            except Exception as e:
                print(f"❌ Error adding documents to ChromaDB: {e}")
        else:
            print("❌ No valid rules found")
    
    def test_knowledge_base(self):
        """Test the knowledge base with sample queries."""
        if self.vectorstore is None or self.embeddings is None:
            print("❌ Knowledge base not available for testing")
            return
        
        test_queries = [
            "How to fix passive voice?",
            "Long sentences readability",
            "Modal verbs can may could",
            "UI terminology mouse click",
            "Special characters formatting"
        ]
        
        print("\n🧪 Testing knowledge base with sample queries...")
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            try:
                results = self.vectorstore.similarity_search(query, k=3)
                for i, result in enumerate(results):
                    print(f"  {i+1}. {result.metadata['title']}")
                    print(f"     Tags: {result.metadata['tags']}")  # Now it's already a string
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    def get_stats(self):
        """Get statistics about the knowledge base."""
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"Total rules: {len(self.rules)}")
        
        if self.rules:
            all_tags = []
            for rule in self.rules:
                all_tags.extend(rule['tags'])
            
            unique_tags = set(all_tags)
            print(f"Unique tags: {len(unique_tags)}")
            print(f"Most common tags: {', '.join(list(unique_tags)[:10])}")
            
            avg_suggestions = sum(len(rule['suggestions']) for rule in self.rules) / len(self.rules)
            print(f"Average suggestions per rule: {avg_suggestions:.1f}")
    
    def save_rule_summary(self):
        """Save a summary of all rules for reference."""
        summary_file = Path(__file__).parent / 'rule_knowledge_summary.md'
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Rule Knowledge Base Summary\n\n")
            f.write(f"Generated on: {__import__('datetime').datetime.now()}\n\n")
            f.write(f"Total rules: {len(self.rules)}\n\n")
            
            for rule in self.rules:
                f.write(f"## {rule['title']}\n\n")
                f.write(f"**ID:** {rule['id']}\n\n")
                f.write(f"**Description:** {rule['description']}\n\n")
                f.write(f"**Tags:** {', '.join(rule['tags'])}\n\n")
                
                if rule['suggestions']:
                    f.write(f"**Suggestions:**\n")
                    for suggestion in rule['suggestions'][:3]:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"✅ Rule summary saved to {summary_file}")

def main():
    """Main function to build the rule knowledge base."""
    print("🚀 Building Rule Knowledge Base...")
    print("=" * 50)
    
    if not DEPS_AVAILABLE:
        print("❌ Required dependencies not available")
        print("Install with: pip install langchain-google-genai chromadb python-dotenv")
        return
    
    builder = RuleKnowledgeBuilder()
    
    # Build the knowledge base
    builder.build_knowledge_base()
    
    # Test it
    builder.test_knowledge_base()
    
    # Show statistics
    builder.get_stats()
    
    # Save summary
    builder.save_rule_summary()
    
    print("\n🎉 Rule Knowledge Base complete!")
    print("\nThe knowledge base is now available for:")
    print("✅ Semantic search of writing rules")
    print("✅ Context-aware rule suggestions")
    print("✅ Enhanced RAG responses")
    print("✅ Rule discovery and guidance")

if __name__ == "__main__":
    main()
