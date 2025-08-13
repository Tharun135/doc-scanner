#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE INVESTIGATION
Trace every single step to find exactly where issues are being filtered out
"""

import requests
import json
import time
import sys
sys.path.append('app')

def final_investigation():
    """The most comprehensive investigation possible"""
    
    print("🔍 FINAL COMPREHENSIVE INVESTIGATION")
    print("=" * 80)
    print("Tracing every step from backend to frontend to find the exact issue")
    print("=" * 80)
    
    # Wait for server
    time.sleep(3)
    
    # Test content that should trigger EVERY type of rule
    test_content = """The document was written by the author and it was reviewed extensively by team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding of the content. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed immediately. Furthermore, the implementation was conducted by the development team. The system was designed to facilitate user interaction. Very detailed documentation was provided."""
    
    print(f"📝 Test content ({len(test_content)} chars):")
    print(f"{test_content}")
    print("=" * 80)
    
    # STEP 1: Test backend DIRECTLY to confirm it works
    print("STEP 1: BACKEND DIRECT TEST")
    print("-" * 40)
    
    try:
        from app.app import get_rules, review_document
        
        rules = get_rules()
        backend_result = review_document(test_content, rules)
        backend_issues = backend_result.get('issues', [])
        
        print(f"✅ Backend detected {len(backend_issues)} issues")
        
        # Categorize backend issues
        backend_categories = {}
        for issue in backend_issues:
            message = issue.get('message', '').lower()
            if 'passive voice' in message:
                backend_categories['passive_voice'] = backend_categories.get('passive_voice', 0) + 1
            elif 'long sentence' in message or 'breaking' in message:
                backend_categories['long_sentence'] = backend_categories.get('long_sentence', 0) + 1
            elif 'modifier' in message and 'very' in message:
                backend_categories['modifier'] = backend_categories.get('modifier', 0) + 1
            elif 'weak verb' in message or 'nominalization' in message:
                backend_categories['weak_verb'] = backend_categories.get('weak_verb', 0) + 1
            elif 'verbose' in message or 'utiliz' in message or 'simplif' in message:
                backend_categories['verbose'] = backend_categories.get('verbose', 0) + 1
            else:
                backend_categories['other'] = backend_categories.get('other', 0) + 1
        
        print(f"Backend issue breakdown: {backend_categories}")
        
        if len(backend_categories) == 1 and 'passive_voice' in backend_categories:
            print("❌ BACKEND PROBLEM: Backend itself only detecting passive voice!")
            print("   Need to investigate why other rules aren't triggering")
            investigate_rules_directly(test_content)
            return
        elif len(backend_categories) > 1:
            print("✅ Backend working correctly - detecting multiple issue types")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return
    
    # STEP 2: Test Flask /upload_progressive endpoint
    print(f"\nSTEP 2: FLASK /upload_progressive TEST")
    print("-" * 40)
    
    test_file = 'final_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        url = 'http://127.0.0.1:5000/upload_progressive'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            print("📤 Sending to /upload_progressive...")
            response = requests.post(url, files=files, data=data, timeout=90)
            
            if response.status_code == 200:
                flask_result = response.json()
                
                # Save for inspection
                with open('final_investigation.json', 'w', encoding='utf-8') as f:
                    json.dump(flask_result, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Flask response saved to 'final_investigation.json'")
                
                if 'sentences' in flask_result:
                    sentences = flask_result['sentences']
                    print(f"Flask returned {len(sentences)} sentences")
                    
                    total_flask_issues = 0
                    flask_categories = {}
                    
                    for i, sentence in enumerate(sentences):
                        feedback = sentence.get('feedback', [])
                        total_flask_issues += len(feedback)
                        
                        print(f"\nSentence {i+1}: {len(feedback)} issues")
                        if feedback:
                            for j, issue in enumerate(feedback[:2]):  # Show first 2
                                message = issue.get('message', 'No message')
                                print(f"  {j+1}. {message[:70]}...")
                                
                                # Categorize
                                message_lower = message.lower()
                                if 'passive voice' in message_lower:
                                    flask_categories['passive_voice'] = flask_categories.get('passive_voice', 0) + 1
                                elif 'long sentence' in message_lower or 'breaking' in message_lower:
                                    flask_categories['long_sentence'] = flask_categories.get('long_sentence', 0) + 1
                                elif 'modifier' in message_lower and 'very' in message_lower:
                                    flask_categories['modifier'] = flask_categories.get('modifier', 0) + 1
                                elif 'weak verb' in message_lower:
                                    flask_categories['weak_verb'] = flask_categories.get('weak_verb', 0) + 1
                                elif 'verbose' in message_lower or 'utiliz' in message_lower:
                                    flask_categories['verbose'] = flask_categories.get('verbose', 0) + 1
                                else:
                                    flask_categories['other'] = flask_categories.get('other', 0) + 1
                    
                    print(f"\nFlask total issues: {total_flask_issues}")
                    print(f"Flask issue breakdown: {flask_categories}")
                    
                    # STEP 3: Compare backend vs Flask
                    print(f"\nSTEP 3: BACKEND VS FLASK COMPARISON")
                    print("-" * 40)
                    
                    print(f"Backend: {len(backend_issues)} issues, {len(backend_categories)} types")
                    print(f"Flask: {total_flask_issues} issues, {len(flask_categories)} types")
                    
                    if len(flask_categories) == 1 and 'passive_voice' in flask_categories:
                        print(f"\n❌ FLASK FILTERING ISSUE CONFIRMED!")
                        print(f"   Backend detects {len(backend_categories)} types")
                        print(f"   But Flask only preserves passive voice")
                        print(f"   The distribution logic is filtering out non-passive issues")
                        
                        # Check the actual distribution
                        print(f"\n🔧 ANALYZING DISTRIBUTION LOGIC...")
                        analyze_distribution_issue(backend_issues, sentences)
                        
                    elif len(flask_categories) > 1:
                        print(f"\n✅ FLASK WORKING: Multiple types preserved")
                        print(f"   Problem might be frontend rendering")
                        print(f"   Check browser developer console for JavaScript errors")
                    else:
                        print(f"\n❓ UNEXPECTED FLASK BEHAVIOR")
                
                else:
                    print(f"❌ No sentences in Flask response")
                    print(f"Keys: {list(flask_result.keys())}")
                    
            else:
                print(f"❌ Flask error: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

def investigate_rules_directly(test_content):
    """Investigate individual rules to see which ones are actually working"""
    
    print(f"\n🔧 INVESTIGATING INDIVIDUAL RULES")
    print("-" * 40)
    
    try:
        from app.app import get_rules
        
        rules = get_rules()
        print(f"Testing {len(rules)} rules individually...")
        
        working_rules = 0
        rule_results = {}
        
        for i, rule in enumerate(rules[:10]):  # Test first 10 rules
            try:
                result = rule(test_content)
                if result and len(result) > 0:
                    working_rules += 1
                    rule_name = str(rule).split('.')[-1] if '.' in str(rule) else str(rule)
                    rule_results[rule_name] = len(result)
                    print(f"  Rule {i+1}: {len(result)} issues - {rule_name}")
            except Exception as e:
                print(f"  Rule {i+1}: ERROR - {str(e)[:50]}")
        
        print(f"\nWorking rules: {working_rules}/{len(rules)}")
        print(f"Rule results: {rule_results}")
        
        if working_rules <= 2:
            print(f"❌ RULES NOT WORKING: Most rules are not triggering")
            print(f"   This explains why only passive voice is detected")
        
    except Exception as e:
        print(f"❌ Rule investigation failed: {e}")

def analyze_distribution_issue(backend_issues, flask_sentences):
    """Analyze why the distribution is filtering out issues"""
    
    print(f"Backend issues detected: {len(backend_issues)}")
    print(f"Flask sentences: {len(flask_sentences)}")
    
    total_flask_issues = sum(len(s.get('feedback', [])) for s in flask_sentences)
    print(f"Total issues in Flask sentences: {total_flask_issues}")
    
    if total_flask_issues < len(backend_issues):
        print(f"❌ ISSUE LOSS: {len(backend_issues) - total_flask_issues} issues lost in distribution")
        print(f"   The distribution logic has a bug that's filtering out issues")
        
        # Show what types were lost
        flask_messages = []
        for s in flask_sentences:
            for issue in s.get('feedback', []):
                flask_messages.append(issue.get('message', '').lower())
        
        backend_messages = [issue.get('message', '').lower() for issue in backend_issues]
        
        lost_passive = sum(1 for msg in backend_messages if 'passive voice' in msg) - sum(1 for msg in flask_messages if 'passive voice' in msg)
        lost_long = sum(1 for msg in backend_messages if 'long sentence' in msg) - sum(1 for msg in flask_messages if 'long sentence' in msg)
        lost_modifier = sum(1 for msg in backend_messages if 'modifier' in msg) - sum(1 for msg in flask_messages if 'modifier' in msg)
        
        print(f"   Lost passive voice: {lost_passive}")
        print(f"   Lost long sentence: {lost_long}")
        print(f"   Lost modifier: {lost_modifier}")

if __name__ == "__main__":
    final_investigation()
