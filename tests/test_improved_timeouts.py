#!/usr/bin/env python3
"""
Test the improved Ollama API timeout handling and progressive timeout strategy.
"""

import requests
import json
import time

def test_improved_ollama_timeouts():
    """Test the enhanced Ollama integration with improved timeouts."""
    
    print("🚀 TESTING IMPROVED OLLAMA TIMEOUT HANDLING")
    print("=" * 55)
    
    # Load configuration
    try:
        with open('ollama_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded successfully")
        print(f"   Timeouts: {config['ollama_config']['timeouts']}")
        print(f"   Models: {list(config['ollama_config']['models'].values())}")
    except FileNotFoundError:
        print("⚠️ Configuration file not found, using defaults")
        config = None
    
    # Test cases with different complexity levels
    test_cases = [
        {
            "name": "Simple Rule Issue (Quick Timeout Expected)",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was saved by the user.",
            "expected_timeout": "quick (5s)",
            "complexity": "simple"
        },
        {
            "name": "Standard Rule Issue (Standard Timeout Expected)", 
            "feedback": "adverbs detected by rule",
            "sentence": "You can easily and simply configure the system settings automatically.",
            "expected_timeout": "standard (10s)",
            "complexity": "standard"
        },
        {
            "name": "Complex Long Sentence (High Timeout Expected)",
            "feedback": "long sentence detected by rule",
            "sentence": "When you configure the complex system settings, which include multiple database connections, comprehensive user permissions, detailed security protocols, and various integration options, you must ensure that all components are properly validated, thoroughly tested, and carefully reviewed before final deployment to the production environment.",
            "expected_timeout": "high (15s)",
            "complexity": "complex"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} cases with progressive timeout strategy...")
    
    ollama_direct_successes = 0
    timeout_improvements = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Feedback: '{test_case['feedback']}'")
        print(f"   Sentence Length: {len(test_case['sentence'])} chars")
        print(f"   Expected Timeout: {test_case['expected_timeout']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=25  # Allow up to 25 seconds for comprehensive testing
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                suggestion = result.get('suggestion', '')
                ai_answer = result.get('ai_answer', '')
                sources = result.get('sources', [])
                
                print(f"   ✅ Status: Success ({response_time:.2f}s)")
                print(f"   🔧 Method Used: {method}")
                
                # Check if we got ollama_rag_direct
                if method == "ollama_rag_direct":
                    print(f"   🎯 OLLAMA_RAG_DIRECT SUCCESS!")
                    print(f"   💡 AI Guidance: \"{ai_answer[:120]}...\"")
                    ollama_direct_successes += 1
                    
                    # Check if timeout was appropriate for complexity
                    if test_case['complexity'] == 'complex' and response_time > 8:
                        print(f"   ⏱️ Used extended timeout appropriately for complex issue")
                        timeout_improvements += 1
                    elif test_case['complexity'] == 'simple' and response_time < 8:
                        print(f"   ⚡ Used quick timeout appropriately for simple issue")
                        timeout_improvements += 1
                    
                elif method.startswith('chromadb'):
                    print(f"   📚 Used RAG fallback: {method}")
                    print(f"   💡 Guidance: \"{ai_answer[:80]}...\"")
                else:
                    print(f"   ⚠️ Used basic fallback: {method}")
                
                # Show sources if available
                if sources:
                    rule_id = sources[0].get('rule_id', 'unknown') if isinstance(sources[0], dict) else 'unknown'
                    print(f"   📖 Source Rule: {rule_id}")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                if response.text:
                    print(f"   Error Details: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            print(f"   ⏱️ TIMEOUT after {response_time:.1f}s - This may indicate timeout settings need adjustment")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Brief pause between tests
        time.sleep(1)
    
    # Summary
    direct_rate = (ollama_direct_successes / len(test_cases)) * 100
    timeout_efficiency = (timeout_improvements / len(test_cases)) * 100
    
    print(f"\n📊 IMPROVED TIMEOUT TEST RESULTS:")
    print(f"   ollama_rag_direct successes: {ollama_direct_successes}/{len(test_cases)} ({direct_rate:.1f}%)")
    print(f"   Appropriate timeout usage: {timeout_improvements}/{len(test_cases)} ({timeout_efficiency:.1f}%)")
    
    print(f"\n🎯 TIMEOUT IMPROVEMENT ASSESSMENT:")
    if direct_rate >= 70:
        print(f"   🎉 EXCELLENT - Improved timeouts are working!")
        print(f"   ✅ Successfully getting ollama_rag_direct responses")
    elif direct_rate >= 40:
        print(f"   👍 GOOD IMPROVEMENT - Better timeout handling")
        print(f"   ⚡ Some cases still using fallback (expected for reliability)")
    else:
        print(f"   ⚠️ STILL ROOM FOR IMPROVEMENT")
        print(f"   💡 May need to adjust timeout values or Ollama performance")
    
    return direct_rate, timeout_efficiency

def test_direct_ollama_api():
    """Test Ollama API directly to check baseline performance."""
    
    print(f"\n🔧 DIRECT OLLAMA API PERFORMANCE TEST")
    print("=" * 45)
    
    models_to_test = ['tinyllama:latest', 'phi3:mini']
    
    for model in models_to_test:
        print(f"\n🤖 Testing model: {model}")
        
        test_prompt = """Fix this writing issue: passive voice detected
Original: "The configuration was completed by the user."
Writing Rule: Convert passive voice to active voice with clear subject.
Provide specific guidance:"""

        try:
            start_time = time.time()
            
            response = requests.post('http://localhost:11434/api/generate', json={
                'model': model,
                'prompt': test_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.2,
                    'num_predict': 100,
                    'num_ctx': 1024
                }
            }, timeout=10)
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                print(f"   ✅ Response time: {response_time:.2f}s")
                print(f"   📝 Response length: {len(ai_response)} chars")
                print(f"   💡 Sample: \"{ai_response[:80]}...\"")
                
                if response_time < 5:
                    print(f"   ⚡ FAST - Good for quick timeout tier")
                elif response_time < 10:
                    print(f"   👍 MODERATE - Good for standard timeout tier")
                else:
                    print(f"   🐌 SLOW - Needs high timeout tier")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout after 10s - Model may need longer timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE OLLAMA TIMEOUT IMPROVEMENT TEST")
    print("=" * 60)
    
    # Test direct API performance first
    test_direct_ollama_api()
    
    # Test improved integration
    direct_rate, timeout_efficiency = test_improved_ollama_timeouts()
    
    print(f"\n🏆 FINAL TIMEOUT IMPROVEMENT RESULTS:")
    print(f"   Enhanced timeout strategy implemented")
    print(f"   Progressive timeouts: 5s → 10s → 15s based on complexity")
    print(f"   Better model selection and parameters")
    print(f"   Improved prompt engineering with more context")
    print(f"   ollama_rag_direct success rate: {direct_rate:.1f}%")
    
    if direct_rate >= 60:
        print(f"   🎉 TIMEOUT IMPROVEMENTS SUCCESSFUL!")
        print(f"   🚀 Ready for high-quality ollama_rag_direct responses!")
    else:
        print(f"   📈 PROGRESS MADE - Continue tuning for optimal performance")
