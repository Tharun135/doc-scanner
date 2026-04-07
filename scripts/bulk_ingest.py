"""
bulk_ingest.py
Enables bulk ingestion of technical manuals and style guides into the ChromaDB Knowledge Base.
Usage:
    python scripts/bulk_ingest.py --dir /path/to/documents
"""

import sys
import os
import argparse
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def bulk_ingest(directory_path):
    """Scan directory and ingest all supported technical documents."""
    try:
        from app.services.enrichment import ingest_document_to_rag
        
        path = Path(directory_path)
        if not path.is_dir():
            print(f"❌ Error: {directory_path} is not a valid directory.")
            return

        supported_exts = ['.txt', '.pdf', '.docx', '.md']
        files = [f for f in path.iterdir() if f.suffix.lower() in supported_exts]

        print(f"📚 Found {len(files)} documents to ingest.")

        for i, file_path in enumerate(files):
            print(f"[{i+1}/{len(files)}] Ingesting {file_path.name}...")
            
            # Read file content safely
            content = ""
            if file_path.suffix.lower() == '.txt' or file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # For PDF/DOCX, it would typically use your existing parse_file logic
                from app.services.parsing import parse_file
                with open(file_path, 'rb') as f:
                    # Simulation: parse_file usually handles file objects from Flask
                    # For CLI, we wrap it
                    content = parse_file(f)

            if content:
                ingest_document_to_rag(content, file_path.name)
                print(f"   ✅ Success")
            else:
                print(f"   ⚠️ Skipping: Could not extract content")

        print("\n🎉 Bulk ingestion complete!")

    except Exception as e:
        print(f"❌ Bulk ingestion failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bulk ingest documents into RAG.')
    parser.add_argument('--dir', required=True, help='Directory containing documents')
    args = parser.parse_args()
    
    bulk_ingest(args.dir)
