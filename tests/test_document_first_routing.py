"""
Test the fixed document-first AI system routing
This verifies that /ai_suggestion now uses the document-first system
"""

import requests
import json
import time

def test_document_first_routing():
    """Test if the AI suggestion route now uses document-first system"""
    print("🚀 Testing Document-First AI Route Fix")
    print("=" * 60)
    
    # Wait for server to be ready
    server_ready = False
    for i in range(10):
        try:
            r = requests.get('http://localhost:5000/rag/stats', timeout=2)
            if r.status_code == 200:
                server_ready = True
                stats = r.json()
                doc_count = stats.get('stats', {}).get('documents_count', 0)
                print(f"✅ Server ready! Found {doc_count} documents in database")
                break
        except:
            print(f"⏳ Waiting for server... attempt {i+1}/10")
            time.sleep(2)
    
    if not server_ready:
        print("❌ Server not ready - please start with: python run.py")
        return False
    
    # Test cases that should trigger document search
    test_cases = [
        {
            "name": "Technical Configuration",
            "feedback": "improve clarity",
            "sentence": "Configure the PLC tags in the Common Configurator to enable data exchange.",
            "document_type": "user_manual",
            "expected_methods": ["document_first", "advanced_rag", "ollama_enhanced"]
        },
        {
            "name": "Passive Voice with Technical Context",
            "feedback": "passive voice detected",
            "sentence": "The file was created by the system for automation purposes.",
            "document_type": "technical_guide",
            "expected_methods": ["document_first", "advanced_rag", "ollama_enhanced"]
        },
        {
            "name": "Industrial Process",
            "feedback": "improve precision",
            "sentence": "Start the motor and check the sensor readings.",
            "document_type": "procedure",
            "expected_methods": ["document_first", "advanced_rag", "ollama_enhanced"]
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} test cases...")
    
    success_count = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input: {test['sentence'][:50]}...")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test['feedback'],
                    'sentence': test['sentence'],
                    'document_type': test['document_type'],
                    'writing_goals': ['clarity', 'precision']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 'unknown')
                sources_count = len(result.get('sources', []))
                
                print(f"   Method: {method}")
                print(f"   Confidence: {confidence}")
                print(f"   Sources: {sources_count}")
                
                # Check if it's using document-first methods
                if method in test['expected_methods']:
                    print(f"   ✅ SUCCESS: Using document-first method '{method}'")
                    success_count += 1
                elif method in ['smart_rule_based', 'smart_fallback']:
                    print(f"   ❌ STILL USING OLD METHOD: '{method}' (should use document-first)")
                else:
                    print(f"   ⚠️  UNKNOWN METHOD: '{method}' (investigating...)")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 Results: {success_count}/{len(test_cases)} tests using document-first methods")
    
    if success_count == len(test_cases):
        print("✅ ALL TESTS PASSED! Document-first system is working!")
    elif success_count > 0:
        print("⚠️  PARTIAL SUCCESS: Some tests still using old methods")
    else:
        print("❌ ALL TESTS FAILED: Still using old smart_rule_based/smart_fallback")
    
    print("\n🎯 Expected Behavior:")
    print("   ✅ Method should be: 'document_first' or 'advanced_rag' or 'ollama_enhanced'")
    print("   ❌ Method should NOT be: 'smart_rule_based' or 'smart_fallback'")
    
    return success_count == len(test_cases)

if __name__ == "__main__":
    test_document_first_routing()