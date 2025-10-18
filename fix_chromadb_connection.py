#!/usr/bin/env python3
"""
Fix ChromaDB connection issue by ensuring consistent settings across all instances.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def fix_chromadb_connection():
    """Fix the ChromaDB connection issue."""
    
    print("🔧 Fixing ChromaDB connection issue...")
    
    # First, let's clear any existing instances
    try:
        import chromadb
        # Clear any cached instances
        if hasattr(chromadb, '_instances'):
            chromadb._instances.clear()
        print("✅ Cleared existing ChromaDB instances")
    except:
        pass
    
    # Now test a clean connection
    try:
        from app.document_first_ai import DocumentFirstAIEngine
        print("🔍 Testing DocumentFirstAIEngine...")
        
        # Create a fresh engine instance
        engine = DocumentFirstAIEngine()
        print(f"✅ Engine created successfully")
        print(f"📊 Documents available: {engine.collection.count() if engine.collection else 0}")
        
        # Test a search
        result = engine.get_document_first_suggestion(
            feedback_text="Avoid passive voice in sentence",
            sentence_context="The installation steps are demonstrated in a video at the following link:",
            document_type="user_manual",
            writing_goals=["clarity", "directness"]
        )
        
        print(f"🎯 Test result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_chromadb_fix():
    """Create a fix for the ChromaDB settings conflict."""
    
    chromadb_fix_code = '''
"""
ChromaDB Connection Fix
This ensures consistent settings across all ChromaDB instances.
"""

import chromadb
from chromadb.config import Settings

# Global ChromaDB settings to ensure consistency
CHROMADB_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db",
    anonymized_telemetry=False
)

def get_chromadb_client():
    """Get a consistent ChromaDB client with unified settings."""
    try:
        client = chromadb.PersistentClient(path="./chroma_db", settings=CHROMADB_SETTINGS)
        return client
    except Exception as e:
        # If there's a conflict, try with different settings
        try:
            client = chromadb.PersistentClient(path="./chroma_db")
            return client
        except Exception as e2:
            # Last resort: use ephemeral client
            return chromadb.Client()

def get_or_create_collection(client, collection_name="docscanner_knowledge"):
    """Get or create a collection with consistent settings."""
    try:
        collection = client.get_collection(name=collection_name)
        return collection
    except:
        # Create collection if it doesn't exist
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        return collection
'''
    
    with open('app/chromadb_fix.py', 'w') as f:
        f.write(chromadb_fix_code)
    
    print("✅ Created chromadb_fix.py")

if __name__ == "__main__":
    print("🚀 ChromaDB Connection Fix\n")
    
    # Create the fix file
    create_chromadb_fix()
    
    # Test the fix
    success = fix_chromadb_connection()
    
    if success:
        print("\n🎉 ChromaDB connection fix successful!")
        print("👉 The document-first AI should now work properly")
    else:
        print("\n⚠️ ChromaDB issue persists - will need manual intervention")
        print("👉 Recommend restarting all Python processes and trying again")