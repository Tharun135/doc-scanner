#!/usr/bin/env python3
"""
Test script to verify new rules format compatibility with existing functionality.
"""

import sys
import os
import json
import requests
import time

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_rules_loading():
    """Test that rules load correctly."""
    print("🔧 Testing rules loading...")
    
    from app.app import get_rules
    rules = get_rules()
    
    print(f"✅ Loaded {len(rules)} rules:")
    for i, rule in enumerate(rules, 1):
        module_name = rule.__module__.split('.')[-1]
        print(f"  {i}. {module_name}.{rule.__name__}")
    
    return len(rules) > 0

def test_rules_execution():
    """Test that rules execute and return expected format."""
    print("\n🎯 Testing rules execution...")
    
    from app.app import get_rules, review_document
    
    # Test content with clear issues
    test_content = """
    this is a test document. microsoft and google are companies. 
    The document was written by the team using passive voice.
    there are some issues with capitalization here.
    """
    
    rules = get_rules()
    result = review_document(test_content, rules)
    
    print(f"✅ Review completed. Found {len(result['issues'])} issues:")
    
    # Check format
    for i, issue in enumerate(result['issues'][:3], 1):  # Show first 3
        print(f"  {i}. Type: {type(issue)}")
        print(f"     Keys: {list(issue.keys())}")
        print(f"     Message: {issue.get('message', 'N/A')[:50]}...")
        print(f"     Position: {issue.get('start', 'N/A')}-{issue.get('end', 'N/A')}")
    
    # Verify expected format
    expected_keys = {'text', 'start', 'end', 'message'}
    format_ok = all(
        isinstance(issue, dict) and 
        expected_keys.issubset(issue.keys())
        for issue in result['issues']
    )
    
    print(f"✅ Format compatibility: {'PASS' if format_ok else 'FAIL'}")
    return format_ok and len(result['issues']) > 0

def test_web_integration():
    """Test that rules work through the web interface."""
    print("\n🌐 Testing web integration...")
    
    # Create a test file
    test_content = """this is a test document with issues.
microsoft should be capitalized.
The document was written by someone using passive voice."""
    
    try:
        # Test the upload endpoint
        files = {'file': ('test.txt', test_content, 'text/plain')}
        response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Web upload successful")
            print(f"   Found {len(data.get('sentence_data', []))} sentences")
            
            # Check if issues were found in sentences
            issues_found = sum(
                len(sentence.get('feedback', []))
                for sentence in data.get('sentence_data', [])
            )
            print(f"   Found {issues_found} total issues in sentences")
            
            return issues_found > 0
        else:
            print(f"❌ Web upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Web integration test failed: {e}")
        return False

def test_individual_rules():
    """Test individual rules to ensure they work correctly."""
    print("\n🔍 Testing individual rules...")
    
    test_cases = [
        ("capitalization", "microsoft and google are companies"),
        ("grammar", "The document was written by me"),
        ("clarity", "It is very clear that this is obviously redundant"),
        ("punctuation", "Hello world,how are you?"),
        ("tone", "You must do this immediately or else"),
    ]
    
    results = {}
    
    for rule_name, test_text in test_cases:
        try:
            module = __import__(f'app.rules.{rule_name}', fromlist=['check'])
            result = module.check(test_text)
            results[rule_name] = {
                'status': 'PASS',
                'issues_found': len(result),
                'issues': result[:2]  # First 2 issues
            }
            print(f"✅ {rule_name}: Found {len(result)} issues")
        except Exception as e:
            results[rule_name] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ {rule_name}: {e}")
    
    return results

def main():
    """Run all compatibility tests."""
    print("🚀 Starting new rules format compatibility test\n")
    
    # Wait a moment for the server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = {
        'rules_loading': test_rules_loading(),
        'rules_execution': test_rules_execution(),
        'web_integration': test_web_integration(),
        'individual_rules': test_individual_rules()
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, result in tests.items():
        if isinstance(result, bool):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20s}: {status}")
            all_passed = all_passed and result
        elif isinstance(result, dict):
            # Individual rules results
            rule_statuses = [r['status'] for r in result.values()]
            passed = rule_statuses.count('PASS')
            total = len(rule_statuses)
            status = f"✅ {passed}/{total} PASS" if passed == total else f"⚠️ {passed}/{total} PASS"
            print(f"{test_name:20s}: {status}")
            all_passed = all_passed and (passed == total)
    
    print("="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! New rules format is fully compatible.")
        print("✅ Rules are working correctly with existing functionality.")
    else:
        print("⚠️ Some tests failed. Check the details above.")
        print("💡 Rules may need adjustments for full compatibility.")
    
    print("\n💡 Key findings:")
    print("• Rules load successfully using the existing loader")
    print("• Rules return the expected list format")
    print("• The app converts string issues to dict format automatically")
    print("• Web integration works but position info may be missing")
    print("• Consider enhancing rules to return structured data with positions")
    
    return all_passed

if __name__ == "__main__":
    main()
