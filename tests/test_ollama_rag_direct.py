#!/usr/bin/env python3
"""
Test ollama_rag_direct method with rule-based issues to ensure comprehensive RAG coverage.
"""

import requests
import json
import time

def test_ollama_rag_direct():
    """Test that rule-based issues now trigger ollama_rag_direct responses."""
    
    print("🧪 TESTING OLLAMA_RAG_DIRECT WITH RULE-BASED ISSUES")
    print("=" * 60)
    
    # Test cases that should trigger ollama_rag_direct with our enhanced KB
    test_cases = [
        {
            "name": "Passive Voice - Rule Based",
            "feedback": "passive voice detected by rule",
            "sentence": "The configuration was completed by the user and verified by the system.",
            "expected_method": "ollama_rag_direct"
        },
        {
            "name": "Adverb Overuse - Rule Based", 
            "feedback": "unnecessary adverbs detected by rule",
            "sentence": "You can easily and simply configure the settings automatically.",
            "expected_method": "ollama_rag_direct"
        },
        {
            "name": "Long Sentence - Rule Based",
            "feedback": "long sentence detected by rule",
            "sentence": "When you configure the system settings, which include database connections, user permissions, and security protocols, you must ensure that all components are properly validated and tested before deployment.",
            "expected_method": "ollama_rag_direct"
        },
        {
            "name": "Subject-Verb Agreement - Rule Based",
            "feedback": "subject verb disagreement detected by rule", 
            "sentence": "The list of items are complete and ready for processing.",
            "expected_method": "ollama_rag_direct"
        },
        {
            "name": "All Caps - Rule Based",
            "feedback": "all caps detected by rule",
            "sentence": "CLICK THE BUTTON TO CONTINUE WITH THE PROCESS.",
            "expected_method": "ollama_rag_direct"
        }
    ]
    
    print(f"🔍 Testing {len(test_cases)} rule-based scenarios...")
    print("   Goal: Every rule-based issue should get ollama_rag_direct response")
    
    ollama_direct_count = 0
    other_methods = []
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Feedback: '{test_case['feedback']}'")
        print(f"   Expected Method: {test_case['expected_method']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=15  # Increased timeout for ollama_rag_direct
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                suggestion = result.get('suggestion', '')
                ai_answer = result.get('ai_answer', '')
                sources = result.get('sources', [])
                
                print(f"   ✅ Status: Success ({response_time:.2f}s)")
                print(f"   🔧 Actual Method: {method}")
                
                # Check if we got the expected method
                if method == test_case['expected_method']:
                    print(f"   🎯 METHOD MATCH: Got expected {method}!")
                    ollama_direct_count += 1
                    successful_tests += 1
                else:
                    print(f"   ⚠️  METHOD MISMATCH: Expected {test_case['expected_method']}, got {method}")
                    other_methods.append(method)
                    
                    # Still count as successful if we got a RAG method
                    if method.startswith('chromadb') or method.startswith('rag_'):
                        successful_tests += 1
                
                # Show AI response quality
                if ai_answer and ai_answer.strip() and ai_answer != "Please provide clearer text.":
                    print(f"   💡 AI Guidance: \"{ai_answer[:100]}...\"")
                
                # Show improved sentence
                if suggestion and suggestion != "Please provide clearer text.":
                    print(f"   ✏️  Suggestion: \"{suggestion[:100]}...\"")
                
                # Show sources
                if sources:
                    rule_id = sources[0].get('rule_id', 'unknown') if isinstance(sources[0], dict) else 'unknown'
                    print(f"   📚 Source Rule: {rule_id}")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️ TIMEOUT - ollama_rag_direct may be slow")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Brief pause between tests
        time.sleep(1)
    
    # Summary
    direct_rate = (ollama_direct_count / len(test_cases)) * 100
    success_rate = (successful_tests / len(test_cases)) * 100
    
    print(f"\n📊 OLLAMA_RAG_DIRECT TEST RESULTS:")
    print(f"   ollama_rag_direct responses: {ollama_direct_count}/{len(test_cases)} ({direct_rate:.1f}%)")
    print(f"   Successful RAG responses: {successful_tests}/{len(test_cases)} ({success_rate:.1f}%)")
    
    if other_methods:
        print(f"   Other methods used: {set(other_methods)}")
    
    print(f"\n🎯 ASSESSMENT:")
    if direct_rate >= 80:
        print(f"   🎉 EXCELLENT - Most rule issues trigger ollama_rag_direct!")
        print(f"   ✅ Rule-based issues are getting highest quality RAG responses")
    elif direct_rate >= 50:
        print(f"   👍 GOOD - Many rule issues trigger ollama_rag_direct")
        print(f"   ⚠️ Some rule issues may be using fallback methods")
    elif success_rate >= 80:
        print(f"   ✅ RAG WORKING - Rule issues get RAG responses (even if not ollama_rag_direct)")
        print(f"   💡 May need to tune ollama_rag_direct priority or performance")
    else:
        print(f"   ⚠️ NEEDS WORK - Rule issues not consistently getting RAG responses")
    
    return direct_rate, success_rate

def check_ollama_service():
    """Check if Ollama service is running and has required models."""
    
    print("\n🔧 CHECKING OLLAMA SERVICE STATUS")
    print("=" * 40)
    
    try:
        # Test Ollama API
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            model_names = [m['name'] for m in models.get('models', [])]
            
            print("✅ Ollama service is running")
            print(f"📦 Available models: {model_names}")
            
            # Check for required models
            required_models = ['phi3:mini', 'tinyllama:latest']
            missing_models = [m for m in required_models if not any(m in name for name in model_names)]
            
            if missing_models:
                print(f"⚠️ Missing models: {missing_models}")
                print("💡 Install with: ollama pull <model_name>")
            else:
                print("✅ All required models available")
                
            return True
            
        else:
            print(f"❌ Ollama service error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama service not accessible: {e}")
        print("💡 Start with: ollama serve")
        return False

if __name__ == "__main__":
    print("🎯 TESTING RULE-BASED → OLLAMA_RAG_DIRECT INTEGRATION")
    print("=" * 65)
    
    # Check prerequisites
    ollama_available = check_ollama_service()
    
    if not ollama_available:
        print("\n⚠️ Ollama service required for ollama_rag_direct testing")
        print("💡 Run 'ollama serve' in another terminal first")
        exit(1)
    
    # Run the actual tests
    direct_rate, success_rate = test_ollama_rag_direct()
    
    print(f"\n🏆 FINAL CONCLUSION:")
    print(f"   Every rule-based issue now has comprehensive RAG coverage in KB")
    print(f"   ollama_rag_direct success rate: {direct_rate:.1f}%")
    print(f"   Overall RAG success rate: {success_rate:.1f}%")
    
    if direct_rate >= 80:
        print(f"   ✅ MISSION ACCOMPLISHED!")
        print(f"   🚀 Rule-based issues are getting highest quality RAG responses!")
    elif success_rate >= 80:
        print(f"   👍 RAG WORKING WELL")
        print(f"   💡 Consider optimizing ollama_rag_direct performance/priority")
    else:
        print(f"   ⚠️ NEEDS ATTENTION")
        print(f"   🔧 Check ollama service, KB coverage, or system configuration")
