#!/usr/bin/env python3
"""
Debug why the AI isn't splitting correctly.
"""

import sys
import os
import re

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pattern_matching():
    """Test our pattern matching logic step by step."""
    
    print("🔍 DEBUGGING AI SENTENCE SPLITTING")
    print("=" * 50)
    
    sentence = "You can configure the Modbus TCP Connector to the field devices to consume the acquired data in the IED for value creation by using the Common Configurator."
    
    print(f"Original sentence: {sentence}")
    print(f"Length: {len(sentence.split())} words")
    print()
    
    # Test pattern 1: can configure...by using
    pattern1 = r'can\s+configure.*?by\s+using'
    match1 = re.search(pattern1, sentence, re.IGNORECASE)
    print(f"Pattern 1 (can configure...by using): {'✅ MATCHED' if match1 else '❌ NO MATCH'}")
    
    if match1:
        print(f"  Matched text: '{match1.group()}'")
    
    # Test specific terms
    terms_check = {
        'modbus tcp connector': 'modbus tcp connector' in sentence.lower(),
        'field devices': 'field devices' in sentence.lower(), 
        'common configurator': 'common configurator' in sentence.lower()
    }
    
    print("\nKey terms check:")
    for term, found in terms_check.items():
        print(f"  '{term}': {'✅ FOUND' if found else '❌ MISSING'}")
    
    # Test our expected logic path
    print("\nLogic path test:")
    if match1 and all(terms_check.values()):
        print("✅ Should trigger our specific technical pattern!")
        
        # This is what our code should generate
        sentence1 = "You can configure the Modbus TCP Connector to connect to the field devices using the Common Configurator."
        sentence2 = "This allows the IED to consume the acquired data for value creation."
        
        print("\nExpected output:")
        print(f"OPTION 1: {sentence1}")
        print(f"OPTION 2: {sentence2}")
        print(f"Words: {len(sentence1.split())} + {len(sentence2.split())} = {len(sentence1.split()) + len(sentence2.split())} (vs original {len(sentence.split())})")
        
    else:
        print("❌ Logic path not triggered")

def test_ai_system_priority():
    """Check which AI system is actually being used."""
    
    print("\n" + "=" * 50)
    print("🔍 CHECKING AI SYSTEM PRIORITY")
    print("=" * 50)
    
    try:
        # Check RAG availability
        try:
            from app.rag_system import get_rag_suggestion
            rag_available = True
            print("✅ RAG system is available")
        except ImportError as e:
            rag_available = False
            print(f"❌ RAG system not available: {e}")
        
        # Check if RAG is being prioritized
        if rag_available:
            print("⚠️  RAG system has PRIORITY - this might override our rule-based improvements!")
            print("   The Gemini RAG system generates its own sentence splits")
            print("   Our improved _split_long_sentence() is used only as fallback")
        else:
            print("✅ RAG not available - rule-based system should be used")
            
    except Exception as e:
        print(f"Error checking systems: {e}")

def test_import_issue():
    """Test if there's an import issue."""
    
    print("\n" + "=" * 50)
    print("🔍 TESTING IMPORT ISSUES")  
    print("=" * 50)
    
    try:
        from app.ai_improvement import GeminiAISuggestionEngine, RAG_AVAILABLE
        print("✅ Import successful")
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        
        engine = GeminiAISuggestionEngine()
        print("✅ Engine created successfully")
        
        # Test the method exists
        if hasattr(engine, '_split_long_sentence'):
            print("✅ _split_long_sentence method exists")
        else:
            print("❌ _split_long_sentence method missing!")
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pattern_matching()
    test_ai_system_priority()  
    test_import_issue()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)
