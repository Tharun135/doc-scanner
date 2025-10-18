#!/usr/bin/env python3
"""
Simple test to verify the upload interface shows Python file support
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data_ingestion import get_supported_formats

print("🎯 Testing upload interface supported formats...")
print()

# Get the formats that would be displayed in the upload interface
formats = get_supported_formats()

print("✅ Formats that will be shown in upload interface:")
formatted_list = ', '.join(sorted(formats)).upper()
print(f"   {formatted_list}")

print()
print("🔍 Checking specific formats:")
format_checks = {
    '.py': 'Python files',
    '.js': 'JavaScript files', 
    '.json': 'JSON files',
    '.yaml': 'YAML files',
    '.yml': 'YAML files',
    '.pdf': 'PDF files',
    '.docx': 'Word documents',
    '.md': 'Markdown files',
    '.txt': 'Text files',
    '.html': 'HTML files'
}

for fmt, description in format_checks.items():
    status = "✅" if fmt in formats else "❌"
    print(f"   {status} {fmt} - {description}")

print()
print("🎉 RESULT:")
if '.py' in formats:
    print("✅ SUCCESS: Python files (.py) will now appear in the upload interface!")
    print("✅ You can now upload your rules folder Python files to the RAG knowledge base!")
else:
    print("❌ FAILED: Python files not supported")

print()
print("💡 Next steps:")
print("   1. Restart your Flask application")
print("   2. Go to the upload page: http://127.0.0.1:5000/rag/upload_knowledge")  
print("   3. You should see .py files in the supported formats list")
print("   4. You can now select and upload Python files from your rules folder")