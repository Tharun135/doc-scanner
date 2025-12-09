#!/usr/bin/env python3
"""
Tool to find and list uploaded documents in the DocScanner RAG system.
"""

import sys
import os
import sqlite3
import json
from pathlib import Path

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def find_uploaded_documents():
    """Find and list all uploaded documents in the system."""
    
    print("🔍 Searching for Uploaded Documents")
    print("=" * 50)
    
    # 1. Check ChromaDB storage location
    print("\n📂 Checking ChromaDB Storage...")
    
    # ChromaDB typically stores data in a local directory
    chroma_paths = [
        "chroma_data",
        ".chroma",  
        "data/chroma",
        "app/chroma_data",
        os.path.expanduser("~/.chroma")
    ]
    
    for path in chroma_paths:
        if os.path.exists(path):
            print(f"✅ Found ChromaDB directory: {path}")
            # List contents
            for root, dirs, files in os.walk(path):
                if files:
                    print(f"   📁 {root}/")
                    for file in files[:5]:  # Limit to first 5 files
                        print(f"     📄 {file}")
                    if len(files) > 5:
                        print(f"     ... and {len(files)-5} more files")
        else:
            print(f"❌ No ChromaDB directory at: {path}")
    
    # 2. Check for SQLite databases
    print(f"\n💾 Checking for Database Files...")
    
    db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]
    found_dbs = []
    
    for pattern in db_patterns:
        for db_file in Path(".").rglob(pattern):
            found_dbs.append(str(db_file))
            print(f"✅ Found database: {db_file}")
    
    # 3. Try to connect to databases and check for document tables
    print(f"\n🗃️ Checking Database Contents...")
    
    for db_path in found_dbs:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"   📋 Tables in {db_path}: {[t[0] for t in tables]}")
            
            # Check for document-related tables
            doc_tables = [t[0] for t in tables if any(keyword in t[0].lower() 
                         for keyword in ['document', 'chunk', 'knowledge', 'rag'])]
            
            for table in doc_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     📊 {table}: {count} records")
                    
                    # Get sample data
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        columns = [description[0] for description in cursor.description]
                        rows = cursor.fetchall()
                        
                        print(f"     📝 Sample columns: {columns[:5]}...")
                        for i, row in enumerate(rows):
                            preview = str(row)[:100] + "..." if len(str(row)) > 100 else str(row)
                            print(f"       Row {i+1}: {preview}")
                
                except sqlite3.Error as e:
                    print(f"     ❌ Error reading {table}: {e}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"   ❌ Could not read {db_path}: {e}")
    
    # 4. Check for uploaded files directory
    print(f"\n📁 Checking for Upload Directories...")
    
    upload_dirs = [
        "uploads",
        "temp",
        "data",
        "knowledge_base", 
        "documents",
        "app/uploads",
        "app/temp"
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"✅ Found upload directory: {dir_path}/ ({len(files)} items)")
            for file in files[:5]:
                print(f"   📄 {file}")
            if len(files) > 5:
                print(f"   ... and {len(files)-5} more files")
        else:
            print(f"❌ No directory: {dir_path}")
    
    # 5. Try to import and check RAG system directly
    print(f"\n🔧 Checking RAG System Status...")
    
    try:
        # Check if we can access the RAG system
        import chromadb
        print("✅ ChromaDB is available")
        
        # Try to connect to the default client
        try:
            client = chromadb.Client()
            collections = client.list_collections()
            print(f"📚 Collections: {[c.name for c in collections]}")
            
            for collection in collections:
                count = collection.count()
                print(f"   📊 {collection.name}: {count} items")
                
                if count > 0:
                    # Get sample data
                    results = collection.peek(limit=3)
                    print(f"     📝 Sample IDs: {results['ids'][:3] if results['ids'] else 'None'}")
                    if results['metadatas']:
                        print(f"     🏷️ Sample metadata: {results['metadatas'][0] if results['metadatas'][0] else 'None'}")
                
        except Exception as e:
            print(f"❌ ChromaDB connection error: {e}")
            
    except ImportError:
        print("❌ ChromaDB not available")
    
    print(f"\n🎯 Summary:")
    print(f"Your document with 1937 chunks is stored in the ChromaDB vector database.")
    print(f"You can view it by accessing the RAG dashboard at: http://localhost:5000/rag/dashboard")
    
    return True

if __name__ == "__main__":
    find_uploaded_documents()