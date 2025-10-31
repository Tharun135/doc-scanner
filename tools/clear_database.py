#!/usr/bin/env python3
"""
Clear all databases and uploaded documents from the doc-scanner system
"""
import os
import shutil
import sqlite3
from pathlib import Path

def clear_database():
    """Clear all databases and uploaded documents"""
    
    print("🗑️ Clearing all databases and uploaded documents...")
    print("=" * 60)
    
    base_path = Path(".")
    
    # 1. Remove ChromaDB directories
    chroma_dirs = [
        "chroma_db",
        "chromadb_data", 
        "chroma",
        "app/chroma_db"
    ]
    
    for dir_name in chroma_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"🗑️ Removing ChromaDB directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed: {dir_path}")
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    # 2. Remove general database directory
    db_dir = base_path / "db"
    if db_dir.exists():
        print(f"🗑️ Removing database directory: {db_dir}")
        try:
            shutil.rmtree(db_dir)
            print(f"✅ Removed: {db_dir}")
        except Exception as e:
            print(f"❌ Error removing {db_dir}: {e}")
    
    # 3. Clear SQLite databases (but keep the files for structure)
    sqlite_dbs = [
        "adaptive_feedback.db",
        "rag_evaluation.db", 
        "suggestion_metrics.db"
    ]
    
    for db_file in sqlite_dbs:
        db_path = base_path / db_file
        if db_path.exists():
            print(f"🗑️ Clearing SQLite database: {db_path}")
            try:
                # Connect and drop all tables
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Drop each table
                for table in tables:
                    table_name = table[0]
                    if table_name != 'sqlite_sequence':  # Don't drop system table
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                        print(f"  📋 Dropped table: {table_name}")
                
                conn.commit()
                conn.close()
                print(f"✅ Cleared database: {db_path}")
                
            except Exception as e:
                print(f"❌ Error clearing {db_path}: {e}")
    
    # 4. Remove uploaded document directories
    upload_dirs = [
        "data",
        "docs",
        "static/uploads",
        "app/static/uploads",
        "uploaded_docs",
        "uploads"
    ]
    
    for dir_name in upload_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"🗑️ Removing upload directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed: {dir_path}")
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    # 5. Remove backup directories that might contain old data
    backup_dirs = [
        "rag_backup_20251013_162139",
        "enhanced_rag"
    ]
    
    for dir_name in backup_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"🗑️ Removing backup directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed: {dir_path}")
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    # 6. Remove generated rule/solution PDFs
    pdf_dirs = [
        "rule_documentation_pdfs",
        "rule_solutions_pdfs"
    ]
    
    for dir_name in pdf_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"🗑️ Removing PDF directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed: {dir_path}")
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    # 7. Remove specific cache/temporary files
    temp_files = [
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        "*.log"
    ]
    
    # Remove __pycache__ directories recursively
    for pycache_dir in base_path.rglob("__pycache__"):
        print(f"🗑️ Removing cache directory: {pycache_dir}")
        try:
            shutil.rmtree(pycache_dir)
            print(f"✅ Removed: {pycache_dir}")
        except Exception as e:
            print(f"❌ Error removing {pycache_dir}: {e}")
    
    # Remove .pyc files recursively
    for pyc_file in base_path.rglob("*.pyc"):
        print(f"🗑️ Removing compiled Python file: {pyc_file}")
        try:
            pyc_file.unlink()
            print(f"✅ Removed: {pyc_file}")
        except Exception as e:
            print(f"❌ Error removing {pyc_file}: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Database cleanup completed!")
    print("📊 Summary:")
    print("   • ChromaDB vector databases cleared")
    print("   • SQLite databases cleared (tables dropped)")
    print("   • Uploaded documents removed")
    print("   • Cache files cleaned")
    print("   • Backup directories removed")
    print("\n💡 To start fresh:")
    print("   • Run the application and upload new documents")
    print("   • The system will recreate databases as needed")

if __name__ == "__main__":
    # Ask for confirmation
    print("⚠️ WARNING: This will remove ALL uploaded documents and clear ALL databases!")
    print("This action cannot be undone.")
    
    confirm = input("\nDo you want to continue? (type 'yes' to confirm): ").strip().lower()
    
    if confirm == 'yes':
        clear_database()
    else:
        print("❌ Operation cancelled.")