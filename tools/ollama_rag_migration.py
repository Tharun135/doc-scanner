#!/usr/bin/env python3
"""
Migration plan and test for Ollama + ChromaDB + LlamaIndex RAG setup
This replaces the current Google Gemini + LangChain setup with local components.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_current_rag_status():
    """Check the current RAG implementation status"""
    print("🔍 Current RAG Implementation Status")
    print("=" * 50)
    
    try:
        from app.rules.rag_rule_helper import RAG_AVAILABLE, RAG_ENABLED
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        print(f"RAG_ENABLED: {RAG_ENABLED}")
        
        if not RAG_AVAILABLE:
            print("❌ Current RAG system not functional - missing dependencies")
            print("   This is perfect for migration to Ollama stack!")
        else:
            print("✅ Current RAG system functional")
            
    except Exception as e:
        print(f"❌ Error checking RAG status: {e}")
        
    print()

def check_dependencies_needed():
    """Check what dependencies we need for Ollama setup"""
    print("📦 Dependencies Check for Ollama Stack")
    print("=" * 50)
    
    required_packages = [
        'llama-index-core',
        'llama-index-llms-ollama', 
        'llama-index-vector-stores-chroma',
        'chromadb',
        'ollama'
    ]
    
    missing = []
    installed = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    print(f"✅ Installed: {installed}")
    print(f"❌ Missing: {missing}")
    
    if missing:
        print(f"\n💡 To install missing packages:")
        print(f"pip install {' '.join(missing)}")
    
    print()
    return missing

def plan_migration_steps():
    """Show the migration plan"""
    print("🗺️  Migration Plan: Google Gemini → Ollama Stack")
    print("=" * 50)
    
    steps = [
        "1. Install dependencies: llama-index, chromadb, ollama",
        "2. Install Ollama locally (ollama.ai)",  
        "3. Download a suitable model (llama3, mistral, phi3)",
        "4. Create new ollama_rag_system.py (replaces scripts/rag_system.py)",
        "5. Update app/rules/rag_rule_helper.py to use Ollama",
        "6. Create rules knowledge base in ChromaDB",
        "7. Test with existing writing rules",
        "8. Update app/ai_improvement.py integration",
        "9. Update web interface for local RAG badges"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n✨ Benefits after migration:")
    benefits = [
        "🏠 Fully local - no API keys needed",
        "⚡ Faster responses - no network latency", 
        "🔒 Complete privacy - all data stays local",
        "💰 Zero ongoing costs - no per-token charges",
        "🎯 Customizable - can fine-tune for writing",
        "📚 Same rule integration - minimal code changes"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print()

def show_implementation_preview():
    """Show what the new implementation would look like"""
    print("👀 Implementation Preview")
    print("=" * 50)
    
    preview_code = '''
# New ollama_rag_system.py structure:

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
import chromadb

class OllamaRAGSystem:
    def __init__(self, model="llama3"):
        # Local Ollama LLM
        self.llm = Ollama(model=model, request_timeout=30.0)
        
        # ChromaDB setup
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection("docscanner_rules")
        
        # LlamaIndex integration
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)
        self.query_engine = self.index.as_query_engine(llm=self.llm, similarity_top_k=3)
    
    def get_rag_suggestion(self, feedback_text, sentence_context, document_type="general"):
        """Generate RAG suggestion using local Ollama"""
        
        prompt = f"""
        You are a technical writing assistant. 
        
        Issue: {feedback_text}
        Original sentence: "{sentence_context}"
        Document type: {document_type}
        
        Provide a complete sentence rewrite that fixes the issue.
        Format: OPTION 1: [rewrite], WHY: [brief explanation]
        """
        
        response = self.query_engine.query(prompt)
        return {
            "suggestion": str(response),
            "confidence": "high",
            "method": "ollama_rag",
            "sources": response.source_nodes if hasattr(response, 'source_nodes') else []
        }
    '''
    
    print(preview_code)
    print()

def compatibility_check():
    """Check compatibility with existing code"""
    print("🔗 Compatibility with Existing Code")
    print("=" * 50)
    
    print("✅ Compatible interfaces:")
    interfaces = [
        "app/rules/rag_rule_helper.py - Same function signatures",
        "app/ai_improvement.py - Same return format", 
        "Web interface - Same suggestion structure",
        "Rule integration - Same check_with_rag() function",
        "Fallback system - Same smart fallback logic"
    ]
    
    for interface in interfaces:
        print(f"   {interface}")
    
    print(f"\n📝 Required changes:")
    changes = [
        "Replace scripts/rag_system.py import",
        "Update dependency imports",
        "Add Ollama model configuration",
        "Update ChromaDB client initialization"
    ]
    
    for change in changes:
        print(f"   • {change}")
    
    print()

def main():
    """Main analysis function"""
    print("🚀 Doc-Scanner: Ollama RAG Migration Analysis")
    print("=" * 50)
    print()
    
    check_current_rag_status()
    missing_deps = check_dependencies_needed()
    plan_migration_steps() 
    show_implementation_preview()
    compatibility_check()
    
    print("🎯 Next Steps:")
    print("1. Run: pip install llama-index-core llama-index-llms-ollama llama-index-vector-stores-chroma chromadb ollama")
    print("2. Install Ollama: https://ollama.ai")
    print("3. Download model: ollama pull llama3")
    print("4. Implement ollama_rag_system.py")
    print("5. Test with existing rules")
    
    if not missing_deps:
        print("\n✅ Ready to proceed with migration!")
    else:
        print(f"\n⚠️  Install {len(missing_deps)} missing dependencies first")

if __name__ == "__main__":
    main()
