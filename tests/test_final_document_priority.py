#!/usr/bin/env python3
"""
Comprehensive test to verify document-first AI priority is working.
"""

import requests
import json
import time

def test_document_priority():
    """Test document-first priority with various scenarios."""
    
    print("🔧 Document-First AI Priority Test")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Check RAG status first
    try:
        rag_response = requests.get(f"{base_url}/rag/stats")
        if rag_response.status_code == 200:
            stats = rag_response.json()
            doc_count = stats.get('document_count', 0)
            print(f"📊 Knowledge Base: {doc_count} documents available")
            
            if doc_count == 0:
                print("⚠️  No documents in knowledge base - upload documents first!")
                return
        else:
            print("⚠️  Cannot check knowledge base status")
    except Exception as e:
        print(f"⚠️  RAG status check failed: {e}")
    
    # Test cases designed to match common documentation content
    test_cases = [
        {
            "name": "Technical Configuration",
            "feedback": "improve clarity",
            "sentence": "Configure the PLC tags in the Common Configurator to enable data exchange.",
            "expected": "Should find matches in technical documentation"
        },
        {
            "name": "User Interface Instructions", 
            "feedback": "make more direct",
            "sentence": "You can click on the configuration button to open the settings dialog.",
            "expected": "Should find UI guidance in uploaded docs"
        },
        {
            "name": "System Process Description",
            "feedback": "passive voice detected", 
            "sentence": "The data is processed by the system and stored in the database.",
            "expected": "Should find similar processes in documentation"
        },
        {
            "name": "Installation Steps",
            "feedback": "simplify instruction",
            "sentence": "The software installation package should be downloaded from the official website.",
            "expected": "Should find installation guidance"
        },
        {
            "name": "Troubleshooting Context",
            "feedback": "improve accuracy",
            "sentence": "If the connection fails, check the network settings and firewall configuration.",
            "expected": "Should find troubleshooting patterns"
        }
    ]
    
    print(f"\n🧪 Testing AI Suggestion Priority:")
    print("-" * 40)
    
    results = {}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Sentence: {test_case['sentence'][:60]}...")
        
        try:
            # Test AI suggestion
            response = requests.post(
                f"{base_url}/ai_suggestion",
                json={
                    "feedback": test_case["feedback"],
                    "sentence": test_case["sentence"], 
                    "document_type": "user_manual",
                    "option_number": 1
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 'unknown')
                sources = result.get('sources', [])
                context_used = result.get('context_used', {})
                
                print(f"✅ Method: {method}")
                print(f"✅ Confidence: {confidence}")
                print(f"✅ Sources: {len(sources)} source(s)")
                
                # Analyze the priority
                priority_level = analyze_method_priority(method)
                print(f"✅ Priority Level: {priority_level}")
                
                results[test_case['name']] = {
                    'method': method,
                    'priority': priority_level,
                    'confidence': confidence,
                    'sources': len(sources)
                }
                
                time.sleep(1)  # Brief pause between requests
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results[test_case['name']] = {'error': response.status_code}
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            results[test_case['name']] = {'error': str(e)}
    
    # Analyze results
    print(f"\n📊 Priority Analysis:")
    print("-" * 40)
    
    priority_counts = {}
    for name, result in results.items():
        if 'error' not in result:
            priority = result['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    for priority, count in sorted(priority_counts.items()):
        percentage = (count / len(results)) * 100
        print(f"   {priority}: {count}/{len(results)} tests ({percentage:.0f}%)")
    
    # Success criteria
    print(f"\n🎯 Document-First Success Analysis:")
    print("-" * 40)
    
    document_methods = ['document_search', 'hybrid_document_llm', 'document_search_primary', 'document_search_extended']
    rag_methods = ['ollama_rag', 'advanced_rag', 'vector_openai', 'contextual_rag']
    rule_methods = ['smart_rule_based', 'intelligent_analysis', 'smart_fallback']
    
    doc_count = sum(1 for r in results.values() if r.get('method') in document_methods)
    rag_count = sum(1 for r in results.values() if r.get('method') in rag_methods)
    rule_count = sum(1 for r in results.values() if r.get('method') in rule_methods)
    
    total_tests = len([r for r in results.values() if 'error' not in r])
    
    if total_tests > 0:
        print(f"   🔍 Document Search: {doc_count}/{total_tests} ({doc_count/total_tests*100:.0f}%)")
        print(f"   📚 RAG Methods: {rag_count}/{total_tests} ({rag_count/total_tests*100:.0f}%)")
        print(f"   ⚡ Rule-Based: {rule_count}/{total_tests} ({rule_count/total_tests*100:.0f}%)")
        
        if doc_count > 0:
            print(f"\n🎉 SUCCESS: Document-first approach is working!")
            print(f"   {doc_count} tests successfully used document search")
        elif rag_count > 0:
            print(f"\n📚 GOOD: RAG system is working with document context")
            print(f"   {rag_count} tests used RAG methods")
        else:
            print(f"\n⚠️  NOTICE: All tests fell back to rule-based methods")
            print(f"   This may indicate:")
            print(f"   • Limited relevant content in uploaded documents")
            print(f"   • Document search thresholds too strict")
            print(f"   • Technical issues with document retrieval")

def analyze_method_priority(method):
    """Analyze which priority level a method represents."""
    
    document_first = ['document_search', 'document_search_primary', 'document_search_extended', 'hybrid_document_llm']
    rag_enhanced = ['ollama_rag', 'advanced_rag', 'vector_openai', 'contextual_rag']
    rule_based = ['smart_rule_based', 'intelligent_analysis']
    fallback = ['smart_fallback', 'basic_fallback', 'emergency_fallback']
    
    if method in document_first:
        return "1. Document-First (PRIORITY)"
    elif method in rag_enhanced:
        return "2. RAG-Enhanced (GOOD)"
    elif method in rule_based:
        return "3. Rule-Based (BACKUP)"
    elif method in fallback:
        return "4. Fallback (LAST RESORT)"
    else:
        return f"Unknown ({method})"

if __name__ == "__main__":
    print("🚀 Testing Document-First AI Priority Configuration")
    print("*" * 60)
    
    test_document_priority()
    
    print(f"\n✅ Test completed!")
    print(f"\n💡 Key Points:")
    print(f"   • Document search should be priority #1")
    print(f"   • RAG methods are acceptable fallbacks")
    print(f"   • Rule-based should only be used when documents don't help")
    print(f"   • Your 7042 uploaded documents are the primary knowledge source!")