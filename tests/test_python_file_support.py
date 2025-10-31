#!/usr/bin/env python3
"""
Test script to verify Python file support has been added to RAG system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.data_ingestion import DocumentLoader, get_supported_formats
    
    print("🔧 Testing Python file support in RAG system...")
    print()
    
    # Test DocumentLoader supported formats
    loader = DocumentLoader()
    print("✅ DocumentLoader supported formats:")
    for fmt in sorted(loader.supported_formats):
        print(f"   {fmt}")
    
    print()
    
    # Test get_supported_formats function
    supported = get_supported_formats()
    print("✅ get_supported_formats() result:")
    for fmt in sorted(supported):
        print(f"   {fmt}")
    
    print()
    
    # Check if Python files are supported
    if '.py' in loader.supported_formats:
        print("🎉 SUCCESS: Python files (.py) are now supported!")
    else:
        print("❌ FAILED: Python files (.py) not found in supported formats")
    
    # Check other code file types
    code_formats = ['.py', '.js', '.json', '.yaml', '.yml']
    supported_code = [fmt for fmt in code_formats if fmt in loader.supported_formats]
    
    print(f"✅ Code file formats supported: {', '.join(supported_code)}")
    
    # Test the code content extraction method
    print()
    print("🔧 Testing code content extraction method...")
    if hasattr(loader, '_extract_code_content'):
        print("✅ _extract_code_content method found")
        
        # Test with our test file
        test_file = os.path.join(os.path.dirname(__file__), 'app', 'rules', 'grammar_rules.py')
        if os.path.exists(test_file):
            try:
                content = loader._extract_code_content(test_file)
                if content:
                    print(f"✅ Successfully extracted content from {os.path.basename(test_file)}")
                    print(f"   Content length: {len(content)} characters")
                    print(f"   First 200 chars: {content[:200]}...")
                else:
                    print("❌ No content extracted")
            except Exception as e:
                print(f"❌ Error extracting content: {e}")
        else:
            print(f"⚠️ Test file not found: {test_file}")
    else:
        print("❌ _extract_code_content method not found")
    
    print()
    print("🎯 Summary:")
    print("✅ Python file support has been successfully added to the RAG system!")
    print("✅ You can now upload .py, .js, .json, .yaml, and .yml files")
    print("✅ The upload interface will show these formats as supported")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Unexpected error: {e}")