#!/usr/bin/env python3
"""
Performance optimization tools for DocScanner RAG system.
Measures speed and provides optimization recommendations.
"""

import time
import requests
import json
from statistics import mean, median
from typing import List, Dict

class PerformanceOptimizer:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def measure_response_time(self, endpoint: str, payload: dict, num_tests: int = 5) -> Dict:
        """Measure response time for multiple requests"""
        times = []
        errors = 0
        
        print(f"🔬 Testing {endpoint} with {num_tests} requests...")
        
        for i in range(num_tests):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    times.append(response_time)
                    print(f"  Request {i+1}: {response_time:.0f}ms")
                else:
                    errors += 1
                    print(f"  Request {i+1}: ERROR {response.status_code}")
                    
            except requests.RequestException as e:
                errors += 1
                print(f"  Request {i+1}: ERROR {str(e)[:50]}...")
        
        if times:
            return {
                "avg_ms": mean(times),
                "median_ms": median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "success_rate": (len(times) / num_tests) * 100,
                "errors": errors
            }
        else:
            return {"error": "All requests failed", "errors": errors}
    
    def test_ai_suggestions(self):
        """Test AI suggestion performance with different types"""
        test_cases = [
            {
                "name": "Adverb Issue",
                "payload": {
                    "feedback": "Check use of adverb: easily",
                    "sentence": "You can easily configure the settings"
                }
            },
            {
                "name": "Passive Voice Issue", 
                "payload": {
                    "feedback": "avoid passive voice",
                    "sentence": "The file was uploaded by the user"
                }
            },
            {
                "name": "Modal Verb Issue",
                "payload": {
                    "feedback": "avoid modal verbs",
                    "sentence": "You should click the button and you may proceed"
                }
            },
            {
                "name": "Long Sentence Issue",
                "payload": {
                    "feedback": "long sentence",
                    "sentence": "This is a very long sentence that contains multiple clauses and should be broken down into shorter, more manageable pieces for better readability and user comprehension."
                }
            }
        ]
        
        print("🚀 PERFORMANCE TESTING: AI Suggestions")
        print("=" * 50)
        
        results = {}
        for test_case in test_cases:
            print(f"\n📊 {test_case['name']}:")
            result = self.measure_response_time("/ai_suggestion", test_case["payload"])
            results[test_case["name"]] = result
            
            if "error" not in result:
                print(f"   ✅ Avg: {result['avg_ms']:.0f}ms | Success: {result['success_rate']:.0f}%")
                
                # Performance rating
                if result['avg_ms'] < 500:
                    print("   🟢 EXCELLENT (< 500ms)")
                elif result['avg_ms'] < 1000:
                    print("   🟡 GOOD (< 1s)")
                elif result['avg_ms'] < 2000:
                    print("   🟠 OK (< 2s)")
                else:
                    print("   🔴 SLOW (> 2s)")
            else:
                print(f"   ❌ FAILED: {result['error']}")
        
        return results
    
    def analyze_performance(self, results: Dict):
        """Analyze performance results and provide recommendations"""
        print("\n🔍 PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        successful_tests = [r for r in results.values() if "error" not in r]
        if not successful_tests:
            print("❌ No successful tests to analyze")
            return
        
        avg_times = [r["avg_ms"] for r in successful_tests]
        overall_avg = mean(avg_times)
        
        print(f"📈 Overall Performance:")
        print(f"   • Average Response Time: {overall_avg:.0f}ms")
        print(f"   • Fastest Test: {min(avg_times):.0f}ms")
        print(f"   • Slowest Test: {max(avg_times):.0f}ms")
        
        # Recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        
        if overall_avg > 2000:
            print("🔴 CRITICAL - Response time too slow:")
            print("   1. Check if Ollama is loaded and ready")
            print("   2. Consider using lighter models (tinyllama vs phi3)")
            print("   3. Reduce LLM timeout from 2s to 1s")
            print("   4. Enable more aggressive caching")
            
        elif overall_avg > 1000:
            print("🟠 MODERATE - Room for improvement:")
            print("   1. Enable response caching for repeated queries")
            print("   2. Optimize ChromaDB query limit (use n_results=2 vs 4)")
            print("   3. Pre-warm Ollama models on startup")
            print("   4. Use connection pooling for requests")
            
        elif overall_avg > 500:
            print("🟡 GOOD - Minor optimizations possible:")
            print("   1. Fine-tune LLM parameters (reduce num_predict)")
            print("   2. Implement query result caching")
            print("   3. Consider async processing for non-critical paths")
            
        else:
            print("🟢 EXCELLENT - Performance is optimal!")
            print("   1. Monitor for regression")
            print("   2. Consider load testing for production")
    
    def suggest_optimizations(self):
        """Provide specific optimization code suggestions"""
        print("\n⚡ SPECIFIC OPTIMIZATIONS TO IMPLEMENT:")
        print("=" * 50)
        
        optimizations = [
            {
                "title": "1. Enable Aggressive Caching",
                "description": "Cache ChromaDB queries and deterministic rewrites",
                "impact": "🟢 HIGH - 50-80% speed improvement on repeated queries",
                "code": "@lru_cache(maxsize=500)\ndef cached_query(query_text): ..."
            },
            {
                "title": "2. Reduce LLM Timeout",
                "description": "Set timeout=0.5 for ultra-fast fallback",
                "impact": "🟢 HIGH - Eliminates slow LLM waits",
                "code": "timeout=0.5  # Instead of timeout=2"
            },
            {
                "title": "3. Optimize ChromaDB Queries",
                "description": "Reduce n_results from 4 to 2",
                "impact": "🟡 MEDIUM - 20-30% faster vector search",
                "code": "n_results=2  # Instead of n_results=4"
            },
            {
                "title": "4. Pre-compile Regex Patterns",
                "description": "Compile regex patterns once at module level",
                "impact": "🟡 MEDIUM - Faster pattern matching",
                "code": "ADVERB_PATTERN = re.compile(r'\\b(easily|simply)\\b')"
            },
            {
                "title": "5. Async Processing",
                "description": "Use async for LLM calls with immediate fallback",
                "impact": "🟢 HIGH - Non-blocking LLM requests",
                "code": "asyncio.wait_for(llm_call(), timeout=0.5)"
            }
        ]
        
        for opt in optimizations:
            print(f"\n{opt['title']}")
            print(f"   📝 {opt['description']}")
            print(f"   📊 {opt['impact']}")
            print(f"   💻 {opt['code']}")

def main():
    optimizer = PerformanceOptimizer()
    
    print("🎯 DOCSCANNER PERFORMANCE OPTIMIZER")
    print("==================================")
    
    # Test performance
    try:
        results = optimizer.test_ai_suggestions()
        optimizer.analyze_performance(results)
        optimizer.suggest_optimizations()
        
    except requests.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server")
        print("   Make sure the server is running on http://localhost:5000")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
