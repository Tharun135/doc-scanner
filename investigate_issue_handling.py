#!/usr/bin/env python3
"""
ISSUE HANDLING INVESTIGATION
Trace how each type of issue is detected and handled
"""

import sys
sys.path.append('app')

def investigate_issue_handling():
    print("🔍 ISSUE HANDLING INVESTIGATION")
    print("=" * 60)
    
    test_content = """The document was written by the author. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point. The utilization of complex terminology makes the document harder to understand."""
    
    print(f"📝 Test content: {test_content}")
    print("\n🔧 Loading rules and checking how each rule processes content...")
    
    # Import the rule loading system
    from app.app import get_rules, review_document
    
    # Load all rules
    rules = get_rules()
    print(f"✅ Loaded {len(rules)} rules")
    
    # Test each rule individually to see what it detects
    print(f"\n📊 INDIVIDUAL RULE ANALYSIS:")
    print("-" * 40)
    
    for i, rule_function in enumerate(rules):
        try:
            rule_name = getattr(rule_function, '__name__', f'rule_{i}')
            if hasattr(rule_function, '__module__'):
                module_name = rule_function.__module__
                if 'rules.' in module_name:
                    rule_name = module_name.split('rules.')[-1]
            
            print(f"\n🔍 Testing rule: {rule_name}")
            
            # Execute the rule
            rule_result = rule_function(test_content)
            
            if rule_result:
                print(f"  ✅ Found {len(rule_result)} issue(s)")
                
                # Analyze each issue
                for j, issue in enumerate(rule_result):
                    if isinstance(issue, dict):
                        print(f"    Issue {j+1}: {issue.get('message', 'No message')}")
                        print(f"      Type: dict")
                        print(f"      Keys: {list(issue.keys())}")
                        
                        # Check for method indicators
                        method = issue.get('method', 'unknown')
                        if method in ['local_ai', 'ai_suggestion', 'rag']:
                            print(f"      🤖 AI/RAG Method: {method}")
                        elif method in ['pattern', 'rule', 'emergency_fallback']:
                            print(f"      📋 Rule-based Method: {method}")
                        else:
                            print(f"      ❓ Method: {method}")
                            
                    elif isinstance(issue, str):
                        print(f"    Issue {j+1}: {issue}")
                        print(f"      Type: string")
                        
                        # Check for RAG/AI indicators in the message
                        issue_lower = issue.lower()
                        if any(keyword in issue_lower for keyword in ['ai suggestion', 'rag', 'ollama', 'llama']):
                            print(f"      🤖 Likely AI-generated")
                        elif any(keyword in issue_lower for keyword in ['pattern', 'detected', 'rule']):
                            print(f"      📋 Likely rule-based")
                        else:
                            print(f"      ❓ Method unclear")
                    
            else:
                print(f"  ➖ No issues found")
                
        except Exception as e:
            print(f"  ❌ Rule failed: {e}")
    
    # Test full document analysis
    print(f"\n🎯 FULL DOCUMENT ANALYSIS:")
    print("-" * 40)
    
    full_result = review_document(test_content, rules)
    issues = full_result.get('issues', [])
    
    print(f"📊 Total issues found: {len(issues)}")
    
    # Categorize issues by detection method
    methods = {}
    ai_count = 0
    rule_count = 0
    
    for issue in issues:
        if isinstance(issue, dict):
            method = issue.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
            
            # Categorize
            if method in ['local_ai', 'ai_suggestion', 'rag', 'llamaindex_ai', 'llamaindex_rag']:
                ai_count += 1
            elif method in ['pattern', 'rule', 'emergency_fallback', 'spacy']:
                rule_count += 1
                
        elif isinstance(issue, str):
            # Analyze string content for method indicators
            issue_lower = issue.lower()
            if any(keyword in issue_lower for keyword in ['ai suggestion', 'rag', 'ollama', 'llama']):
                ai_count += 1
                methods['ai_inferred'] = methods.get('ai_inferred', 0) + 1
            else:
                rule_count += 1
                methods['rule_inferred'] = methods.get('rule_inferred', 0) + 1
    
    print(f"\n📈 DETECTION METHOD BREAKDOWN:")
    print(f"  🤖 AI/RAG-based issues: {ai_count}")
    print(f"  📋 Rule-based issues: {rule_count}")
    print(f"  📊 Method distribution: {methods}")
    
    # Check RAG system status
    print(f"\n🔧 RAG SYSTEM STATUS:")
    print("-" * 40)
    
    try:
        from app.rules.smart_rag_manager import get_rag_status
        rag_status = get_rag_status()
        print(f"📊 RAG Status: {rag_status}")
    except Exception as e:
        print(f"❌ Could not get RAG status: {e}")
    
    # Check LlamaIndex availability
    try:
        from app.llamaindex_ai import LLAMAINDEX_AVAILABLE, LlamaIndexAISuggestionEngine
        print(f"🦙 LlamaIndex Available: {LLAMAINDEX_AVAILABLE}")
        
        if LLAMAINDEX_AVAILABLE:
            try:
                ai_engine = LlamaIndexAISuggestionEngine()
                print(f"🤖 AI Engine Initialized: {getattr(ai_engine, 'is_initialized', False)}")
                print(f"🔧 Model: {getattr(ai_engine, 'model_name', 'unknown')}")
            except Exception as e:
                print(f"❌ AI Engine init failed: {e}")
    except Exception as e:
        print(f"❌ Could not check LlamaIndex: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"The issue detection system appears to be using:")
    if ai_count > rule_count:
        print(f"🤖 PRIMARILY AI/RAG-BASED detection ({ai_count} AI vs {rule_count} rule-based)")
        print(f"   Issues are being enhanced with local AI suggestions")
    elif rule_count > ai_count:
        print(f"📋 PRIMARILY RULE-BASED detection ({rule_count} rule-based vs {ai_count} AI)")
        print(f"   Traditional pattern matching and linguistic rules")
    else:
        print(f"⚖️ HYBRID APPROACH ({ai_count} AI + {rule_count} rule-based)")
        print(f"   Combination of both AI enhancement and rule-based detection")

if __name__ == "__main__":
    investigate_issue_handling()
