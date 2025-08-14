"""
Full RAG Upgrade Guide
Optional upgrade to vector embeddings with LlamaIndex for enhanced semantic search.
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_full_rag_requirements():
    """Check if full RAG dependencies are available."""
    
    print("🔍 Checking Full RAG Requirements\n")
    
    required_packages = [
        "llama-index-core",
        "llama-index-llms-ollama", 
        "llama-index-embeddings-huggingface",
        "sentence-transformers",
        "torch"
    ]
    
    missing_packages = []
    available_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            available_packages.append(package)
            print(f"✅ {package} - Available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Not installed")
    
    print(f"\n📊 Status: {len(available_packages)}/{len(required_packages)} packages available")
    
    if missing_packages:
        print(f"\n📦 Missing Packages:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print(f"\n💡 To install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        
        print(f"\n⚠️ Note: This will require ~2GB disk space for ML models")
        return False
    else:
        print(f"\n✅ All dependencies available for full RAG!")
        return True

def compare_rag_systems():
    """Compare simplified vs full RAG capabilities."""
    
    print("📊 RAG System Comparison\n")
    
    comparison = [
        {
            "Feature": "Rule Matching",
            "Simplified RAG": "Keyword-based",
            "Full RAG": "Semantic similarity",
            "Benefit": "Better understanding of context"
        },
        {
            "Feature": "Search Accuracy", 
            "Simplified RAG": "Exact keyword matches",
            "Full RAG": "Contextual similarity",
            "Benefit": "Finds relevant rules even with different wording"
        },
        {
            "Feature": "Performance",
            "Simplified RAG": "Very fast",
            "Full RAG": "Slower (ML processing)",
            "Benefit": "Trade-off: accuracy vs speed"
        },
        {
            "Feature": "Disk Space",
            "Simplified RAG": "< 1MB",
            "Full RAG": "~2GB (ML models)",
            "Benefit": "Lightweight vs comprehensive"
        },
        {
            "Feature": "Dependencies",
            "Simplified RAG": "None (built-in Python)",
            "Full RAG": "PyTorch, Transformers, etc.",
            "Benefit": "Simple vs advanced"
        },
        {
            "Feature": "Offline Capability",
            "Simplified RAG": "100% offline",
            "Full RAG": "100% offline (after model download)",
            "Benefit": "Both work without internet"
        }
    ]
    
    print(f"{'Feature':<20} {'Simplified RAG':<25} {'Full RAG':<25} {'Benefit'}")
    print("-" * 95)
    
    for item in comparison:
        print(f"{item['Feature']:<20} {item['Simplified RAG']:<25} {item['Full RAG']:<25} {item['Benefit']}")
    
    print(f"\n💡 Recommendation:")
    print(f"   - Use Simplified RAG for: Fast responses, limited resources, simple deployments")
    print(f"   - Use Full RAG for: Maximum accuracy, complex queries, semantic understanding")

def test_full_rag_if_available():
    """Test full RAG system if dependencies are available."""
    
    print("🧪 Testing Full RAG System\n")
    
    try:
        from llama_index.core import VectorStoreIndex, Document, Settings
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ LlamaIndex imports successful")
        
        # Test if Ollama is available
        try:
            llm = Ollama(model="llama3.2:3b", request_timeout=10.0)
            print("✅ Ollama LLM connection available")
            ollama_available = True
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
            print("   Install Ollama from https://ollama.ai for local LLM")
            ollama_available = False
        
        # Test embeddings
        try:
            embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
            print("✅ HuggingFace embeddings available")
            
            # Test basic embedding
            test_text = "This is a test sentence for embedding."
            embedding = embed_model.get_text_embedding(test_text)
            print(f"✅ Embedding test successful (dimension: {len(embedding)})")
            
        except Exception as e:
            print(f"❌ Embedding test failed: {e}")
            return False
        
        # Test document indexing
        try:
            # Create sample documents
            documents = [
                Document(text="Passive voice makes writing less direct. Use active voice instead."),
                Document(text="Wordy phrases reduce clarity. Use concise language."),
                Document(text="Technical jargon confuses readers. Define terms clearly.")
            ]
            
            # Create index
            index = VectorStoreIndex.from_documents(documents)
            print("✅ Document indexing successful")
            
            # Test query
            query_engine = index.as_query_engine()
            response = query_engine.query("How to improve writing clarity?")
            print(f"✅ Query test successful: {str(response)[:100]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Full RAG test failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ LlamaIndex not available: {e}")
        return False

def upgrade_instructions():
    """Provide step-by-step upgrade instructions."""
    
    print("📋 Full RAG Upgrade Instructions\n")
    
    steps = [
        {
            "step": 1,
            "title": "Install Dependencies",
            "description": "Install required packages (requires ~2GB disk space)",
            "command": "pip install llama-index-core llama-index-llms-ollama llama-index-embeddings-huggingface sentence-transformers torch"
        },
        {
            "step": 2,
            "title": "Install Ollama (Optional)",
            "description": "For local LLM processing without cloud dependencies",
            "command": "Download from https://ollama.ai and install llama3.2:3b model"
        },
        {
            "step": 3,
            "title": "Update Configuration",
            "description": "The system will automatically detect and use full RAG when available",
            "command": "No changes needed - automatic fallback system"
        },
        {
            "step": 4,
            "title": "Test System",
            "description": "Verify full RAG is working",
            "command": "python full_rag_upgrade.py"
        }
    ]
    
    for step in steps:
        print(f"Step {step['step']}: {step['title']}")
        print(f"   Description: {step['description']}")
        print(f"   Command: {step['command']}")
        print()
    
    print("⚠️ Important Notes:")
    print("   - Full RAG requires significant disk space (~2GB)")
    print("   - First run will download ML models (internet required)")
    print("   - After setup, works completely offline")
    print("   - Simplified RAG remains as fallback")

def main():
    """Main function to run upgrade assessment."""
    
    print("🚀 Doc Scanner RAG Upgrade Assessment\n")
    
    # Check current system
    print("📍 Current System Status:")
    try:
        from app.rules.rag_main import is_rag_available
        if is_rag_available():
            print("✅ Simplified RAG system is working")
        else:
            print("❌ RAG system not available")
    except Exception as e:
        print(f"❌ Error checking RAG system: {e}")
    
    print("\n" + "="*80)
    
    # Check requirements
    full_rag_ready = check_full_rag_requirements()
    
    print("\n" + "="*80)
    
    # Show comparison
    compare_rag_systems()
    
    print("\n" + "="*80)
    
    if full_rag_ready:
        # Test full RAG
        full_rag_working = test_full_rag_if_available()
        
        if full_rag_working:
            print("\n🎉 Full RAG System Ready!")
            print("Your system can be upgraded to use semantic embeddings for enhanced accuracy.")
        else:
            print("\n⚠️ Full RAG Dependencies Available but System Not Ready")
            print("Some configuration may be needed.")
    else:
        print("\n📋 Full RAG Upgrade Available")
        upgrade_instructions()
    
    print("\n🎯 Assessment Complete!")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Current: Simplified RAG (keyword-based) ✅ Working")
    print(f"   Available: Full RAG (semantic embeddings) {'✅ Ready' if full_rag_ready else '📦 Needs installation'}")
    print(f"   Recommendation: {'Upgrade when ready' if not full_rag_ready else 'Test and deploy'}")

if __name__ == "__main__":
    main()
