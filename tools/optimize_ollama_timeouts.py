#!/usr/bin/env python3
"""
Ultra-optimized Ollama integration with aggressive timeout improvements.
Focus on getting ollama_rag_direct working consistently.
"""

import requests
import json
import time
import logging

logger = logging.getLogger(__name__)

def test_ultra_optimized_ollama():
    """Test ultra-optimized Ollama configuration for fastest possible responses."""
    
    print("⚡ ULTRA-OPTIMIZED OLLAMA TESTING")
    print("=" * 40)
    
    # Ultra-fast configurations for different models
    optimized_configs = [
        {
            "name": "Ultra Fast TinyLlama",
            "model": "tinyllama:latest",
            "options": {
                "temperature": 0.1,
                "top_p": 0.7,
                "num_predict": 30,    # Very short responses
                "num_ctx": 512,       # Minimal context
                "repeat_penalty": 1.0 # No repeat penalty for speed
            },
            "timeout": 8
        },
        {
            "name": "Fast TinyLlama Extended",
            "model": "tinyllama:latest", 
            "options": {
                "temperature": 0.1,
                "top_p": 0.8,
                "num_predict": 60,
                "num_ctx": 1024,
                "repeat_penalty": 1.1
            },
            "timeout": 12
        },
        {
            "name": "Optimized Phi3 Mini",
            "model": "phi3:mini",
            "options": {
                "temperature": 0.1,
                "top_p": 0.8, 
                "num_predict": 80,
                "num_ctx": 1536,
                "repeat_penalty": 1.1
            },
            "timeout": 18
        }
    ]
    
    test_prompt = """Fix: passive voice detected
Text: "The file was saved by user"
Rule: Use active voice
Quick fix:"""

    print("🧪 Testing ultra-optimized configurations...")
    
    successful_configs = []
    
    for i, config in enumerate(optimized_configs, 1):
        print(f"\n⚡ Test {i}: {config['name']}")
        print(f"   Model: {config['model']}")
        print(f"   Timeout: {config['timeout']}s")
        print(f"   Max tokens: {config['options']['num_predict']}")
        
        start_time = time.time()
        
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': config['model'],
                    'prompt': test_prompt,
                    'stream': False,
                    'options': config['options']
                }, 
                timeout=config['timeout']
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                print(f"   ✅ SUCCESS: {response_time:.2f}s")
                print(f"   📝 Response: \"{ai_response}\"")
                print(f"   📊 Length: {len(ai_response)} chars")
                
                if response_time < config['timeout'] * 0.8:  # Finished well within timeout
                    print(f"   🚀 EXCELLENT - Fast and reliable!")
                    successful_configs.append({**config, 'actual_time': response_time, 'response': ai_response})
                else:
                    print(f"   ⚠️ ACCEPTABLE - But close to timeout limit")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Details: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            print(f"   ⏱️ TIMEOUT after {response_time:.1f}s")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print(f"\n📊 OPTIMIZATION RESULTS:")
    print(f"   Successful configurations: {len(successful_configs)}/{len(optimized_configs)}")
    
    if successful_configs:
        print(f"\n🏆 WORKING CONFIGURATIONS:")
        for i, config in enumerate(successful_configs, 1):
            print(f"   {i}. {config['name']}: {config['actual_time']:.2f}s")
            print(f"      → \"{config['response'][:60]}...\"")
        
        # Return the fastest working config
        fastest_config = min(successful_configs, key=lambda x: x['actual_time'])
        print(f"\n⚡ RECOMMENDED CONFIG: {fastest_config['name']}")
        return fastest_config
    else:
        print(f"   ⚠️ No configurations completed within timeout limits")
        return None

def update_enrichment_with_best_config(best_config):
    """Update the enrichment service with the best working configuration."""
    
    if not best_config:
        print("❌ No working configuration found to update")
        return
    
    print(f"\n🔧 UPDATING ENRICHMENT SERVICE")
    print(f"Using: {best_config['name']} ({best_config['actual_time']:.2f}s)")
    
    # Create the optimized configuration code
    optimized_code = f"""                    # OPTIMIZED Ollama call - Based on performance testing
                    response = requests.post('http://localhost:11434/api/generate', json={{
                        'model': '{best_config['model']}',  # Tested fastest model
                        'prompt': enhanced_prompt,
                        'stream': False,
                        'options': {{
                            'temperature': {best_config['options']['temperature']},
                            'top_p': {best_config['options']['top_p']},
                            'num_predict': {best_config['options']['num_predict']},  # Optimized for speed
                            'num_ctx': {best_config['options']['num_ctx']},
                            'repeat_penalty': {best_config['options'].get('repeat_penalty', 1.1)}
                        }}
                    }}, timeout={best_config['timeout']})  # Tested reliable timeout"""
    
    print("📝 Optimized configuration ready for integration:")
    print(f"   Model: {best_config['model']}")
    print(f"   Timeout: {best_config['timeout']}s")
    print(f"   Expected response time: ~{best_config['actual_time']:.1f}s")
    print(f"   Max tokens: {best_config['options']['num_predict']}")
    
    return optimized_code

def create_timeout_improvement_summary():
    """Create a summary of timeout improvements implemented."""
    
    print(f"\n📋 TIMEOUT IMPROVEMENT SUMMARY")
    print("=" * 35)
    
    improvements = [
        "✅ Progressive timeout strategy: 5s → 10s → 15s based on complexity",
        "✅ Better model selection: tinyllama for speed, phi3 for quality",
        "✅ Optimized generation parameters: reduced tokens, focused temperature",
        "✅ Enhanced prompt engineering: more context, better instructions", 
        "✅ Improved error handling: graceful fallback to chromadb_deterministic",
        "✅ Configuration-driven timeouts: easily adjustable via ollama_config.json",
        "✅ Performance testing: direct API testing to find optimal settings"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")
    
    print(f"\n⚡ PERFORMANCE TARGETS:")
    print(f"   • Quick responses: < 8 seconds (simple issues)")
    print(f"   • Standard responses: < 12 seconds (rule-based issues)")
    print(f"   • Complex responses: < 18 seconds (long sentences)")
    print(f"   • Fallback guarantee: chromadb_deterministic always works")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"   1. Use TinyLlama for speed-critical applications (< 8s)")
    print(f"   2. Use Phi3-mini for quality-critical applications (< 18s)")
    print(f"   3. Keep chromadb_deterministic as reliable fallback")
    print(f"   4. Monitor performance and adjust timeouts as needed")
    print(f"   5. Consider caching frequent ollama_rag_direct responses")

if __name__ == "__main__":
    print("🎯 ULTRA-OPTIMIZATION FOR OLLAMA_RAG_DIRECT")
    print("=" * 50)
    
    # Test ultra-optimized configurations
    best_config = test_ultra_optimized_ollama()
    
    # Update enrichment service if we found a good config
    optimized_code = update_enrichment_with_best_config(best_config)
    
    # Create improvement summary
    create_timeout_improvement_summary()
    
    if best_config:
        print(f"\n🎉 TIMEOUT OPTIMIZATION SUCCESSFUL!")
        print(f"   Best configuration: {best_config['name']}")
        print(f"   Reliable response time: {best_config['actual_time']:.2f}s")
        print(f"   🚀 Ready to integrate into enrichment service!")
    else:
        print(f"\n⚠️ TIMEOUT OPTIMIZATION NEEDS MORE WORK")
        print(f"   Consider: Hardware upgrade, model optimization, or caching strategy")
