# enhanced_rag/integration_guide.py
"""
Integration guide and migration script for Enhanced RAG system.
Provides step-by-step migration from existing RAG to enhanced version.
"""
import os
import sys
import subprocess
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGMigrationAssistant:
    """Assistant for migrating to enhanced RAG system"""
    
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)
        
    def check_existing_system(self) -> Dict[str, Any]:
        """Check current RAG system status"""
        status = {
            "ollama_available": False,
            "chromadb_available": False,
            "existing_collection": False,
            "collection_size": 0,
            "missing_dependencies": []
        }
        
        # Check Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                status["ollama_available"] = True
                models = response.json().get("models", [])
                status["available_models"] = [m["name"] for m in models]
        except:
            status["ollama_available"] = False
        
        # Check ChromaDB
        try:
            import chromadb
            client = chromadb.PersistentClient(path="./chroma_db")
            collections = client.list_collections()
            status["chromadb_available"] = True
            status["existing_collections"] = [c.name for c in collections]
            
            # Check for existing docscanner collection
            for collection in collections:
                if "docscanner" in collection.name.lower():
                    status["existing_collection"] = True
                    try:
                        status["collection_size"] = collection.count()
                    except:
                        status["collection_size"] = "unknown"
                    break
        except Exception as e:
            status["chromadb_available"] = False
            status["error"] = str(e)
        
        # Check dependencies
        required_packages = [
            ("spacy", "spacy"),
            ("chromadb", "chromadb"),
            ("requests", "requests"),
            ("rank_bm25", "rank-bm25")
        ]
        
        for package_name, pip_name in required_packages:
            try:
                __import__(package_name)
            except ImportError:
                status["missing_dependencies"].append(pip_name)
        
        # Check spaCy model
        try:
            import spacy
            spacy.load("en_core_web_sm")
        except:
            status["missing_dependencies"].append("spacy model (en_core_web_sm)")
        
        return status
    
    def install_dependencies(self) -> bool:
        """Install missing dependencies"""
        status = self.check_existing_system()
        missing = status["missing_dependencies"]
        
        if not missing:
            print("✅ All dependencies already installed")
            return True
        
        print(f"📦 Installing {len(missing)} missing dependencies...")
        
        for dep in missing:
            if dep == "spacy model (en_core_web_sm)":
                print("Installing spaCy English model...")
                try:
                    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                                 check=True, capture_output=True)
                    print("✅ spaCy model installed")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install spaCy model: {e}")
                    return False
            else:
                print(f"Installing {dep}...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                 check=True, capture_output=True)
                    print(f"✅ {dep} installed")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install {dep}: {e}")
                    return False
        
        print("✅ All dependencies installed successfully")
        return True
    
    def perform_migration(self, backup_existing: bool = True) -> bool:
        """Migrate existing RAG data to enhanced system"""
        try:
            from .enhanced_vectorstore import get_enhanced_store
            
            print("🚀 Starting RAG migration...")
            
            # Create enhanced store
            enhanced_store = get_enhanced_store("docscanner_enhanced")
            
            # Migrate from existing collection
            success = enhanced_store.migrate_from_existing_collection("docscanner_solutions")
            
            if success:
                print("✅ Migration completed successfully")
                
                # Test the migrated system
                print("🧪 Testing migrated system...")
                test_results = enhanced_store.test_retrieval()
                
                successful_tests = sum(1 for r in test_results.values() 
                                     if isinstance(r, dict) and r.get('results_count', 0) > 0)
                
                print(f"✅ {successful_tests}/{len(test_results)} test queries successful")
                return True
            else:
                print("❌ Migration failed")
                return False
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False
    
    def create_integration_example(self) -> str:
        """Create example integration code"""
        example_code = '''
# Example: Integrating Enhanced RAG with existing DocScanner

# 1. Import enhanced system
from enhanced_rag import get_enhanced_rag_system

# 2. Initialize (automatically migrates existing data)
rag_system = get_enhanced_rag_system()

# 3. Use in existing enrichment service (drop-in replacement)
def enrich_issue_with_solution_enhanced(issue: dict) -> dict:
    """Enhanced version of existing enrichment function"""
    feedback_text = issue.get("message", "")
    sentence_context = issue.get("context", "")
    rule_id = issue.get("issue_type", "unknown")
    
    # Get enhanced RAG suggestion
    response = rag_system.get_rag_suggestion(
        feedback_text=feedback_text,
        sentence_context=sentence_context,
        rule_id=rule_id,
        document_type="technical"
    )
    
    if response:
        # Update issue with enhanced response
        issue["solution_text"] = response.get("explanation", "")
        issue["proposed_rewrite"] = response.get("suggested_correction", "")
        issue["confidence"] = response.get("confidence", "medium")
        issue["sources"] = response.get("sources", [])
        issue["method"] = "enhanced_rag"
    
    return issue

# 4. Performance monitoring
def monitor_rag_performance():
    """Monitor enhanced RAG performance"""
    metrics = rag_system.get_system_metrics()
    print(f"Success rate: {metrics['performance_metrics']['successful_responses']}")
    print(f"Avg response time: {metrics['performance_metrics']['avg_response_time']:.3f}s")
    print(f"Total chunks: {metrics['vector_store_stats']['total_chunks']}")

# 5. Batch document ingestion
def ingest_new_documents(documents: List[Dict]):
    """Ingest new documents with enhanced chunking"""
    for doc in documents:
        chunk_count = rag_system.vector_store.ingest_document(
            document_text=doc["content"],
            source_doc_id=doc["id"],
            product=doc.get("product", "docscanner"),
            version=doc.get("version", "1.0"),
            additional_metadata=doc.get("metadata", {})
        )
        print(f"Ingested {chunk_count} chunks from {doc['id']}")
'''
        
        # Write example to file
        example_path = os.path.join(self.current_dir, "integration_example.py")
        with open(example_path, 'w') as f:
            f.write(example_code)
        
        return example_path
    
    def run_full_migration(self) -> bool:
        """Run complete migration process"""
        print("🚀 Enhanced RAG Migration Assistant")
        print("=" * 50)
        
        # Step 1: Check current system
        print("1. Checking current system...")
        status = self.check_existing_system()
        
        print(f"   Ollama: {'✅' if status['ollama_available'] else '❌'}")
        print(f"   ChromaDB: {'✅' if status['chromadb_available'] else '❌'}")
        print(f"   Existing data: {'✅' if status['existing_collection'] else '❌'}")
        if status.get('collection_size'):
            print(f"   Collection size: {status['collection_size']} documents")
        
        # Step 2: Install dependencies
        print("\n2. Installing dependencies...")
        if not self.install_dependencies():
            print("❌ Failed to install dependencies")
            return False
        
        # Step 3: Perform migration
        print("\n3. Migrating to enhanced system...")
        if not self.perform_migration():
            print("❌ Migration failed")
            return False
        
        # Step 4: Create integration example
        print("\n4. Creating integration example...")
        example_path = self.create_integration_example()
        print(f"✅ Integration example created: {example_path}")
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Review the integration example code")
        print("2. Update your enrichment service to use enhanced RAG")
        print("3. Monitor performance with rag_system.get_system_metrics()")
        print("4. Ingest new documents with enhanced chunking")
        
        return True


def quick_migration():
    """Quick migration for immediate use"""
    assistant = RAGMigrationAssistant()
    return assistant.run_full_migration()


if __name__ == "__main__":
    # Run migration assistant
    assistant = RAGMigrationAssistant()
    success = assistant.run_full_migration()
    
    if success:
        print("\n✅ Enhanced RAG system ready for use!")
        
        # Quick test
        try:
            from enhanced_rag import get_enhanced_rag_system
            rag = get_enhanced_rag_system()
            
            # Test query
            response = rag.get_rag_suggestion(
                feedback_text="passive voice detected",
                sentence_context="The file was created by the system.",
                rule_id="passive-voice"
            )
            
            if response:
                print(f"\n🧪 Quick test successful:")
                print(f"   Correction: {response.get('suggested_correction', 'N/A')}")
                print(f"   Confidence: {response.get('confidence', 'N/A')}")
            else:
                print("\n⚠️ Quick test failed - system may need additional setup")
                
        except Exception as e:
            print(f"\n⚠️ Quick test error: {e}")
    else:
        print("\n❌ Migration failed - manual setup required")
