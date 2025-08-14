#!/usr/bin/env python3

import requests
import time
import json

def test_web_interface_detailed():
    """Test the actual web interface to see what issues are displayed"""
    
    print("🌐 TESTING WEB INTERFACE DETAILED RESPONSE")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Waiting for server...")
    time.sleep(2)
    
    # Test content similar to what you reported
    test_content = """Security guidelines for usage of USB sticks within shop floor are applied.
The system uses appropriate security measures.
Customer is responsible for configuring the application security settings.
The system is installed in an environment that ensures physical access is limited to authorized maintenance personnel.
System includes hardware, firmware and operating system components.
Centralized IT security components (Active Directory, Centralized IT Logging Server) are provided and configured.
The operator personnel accessing the system is well trained.
The operator uses appropriate access controls.
Operator is responsible for configuring the PLCs with appropriate security settings."""
    
    print(f"📝 Test content:")
    print("-" * 40)
    for i, line in enumerate(test_content.strip().split('\n'), 1):
        print(f"{i:2d}: {line}")
    print("-" * 40)
    
    try:
        # Upload document
        print("\n📤 Uploading test document...")
        files = {'file': ('test_unclear.txt', test_content)}
        response = requests.post('http://localhost:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            
            sentences = result.get('sentences', [])
            print(f"\n📝 DETAILED SENTENCE ANALYSIS ({len(sentences)} sentences)")
            print("=" * 60)
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\nSentence {i}:")
                print(f"  Original Text: {sentence.get('sentence', '')[:100]}...")
                print(f"  HTML Text: {sentence.get('html_text', '')[:100]}...")
                print(f"  Position: {sentence.get('start', 0)}-{sentence.get('end', 0)}")
                
                feedback_items = sentence.get('feedback', [])
                print(f"  Issues Found: {len(feedback_items)}")
                
                for j, issue in enumerate(feedback_items, 1):
                    print(f"    Issue {j}:")
                    print(f"      Text: '{issue.get('text', '')}'")
                    print(f"      Message: '{issue.get('message', '')}'")
                    print(f"      Position: {issue.get('start', 0)}-{issue.get('end', 0)}")
                    
                    # Check for potential problems
                    issue_text = issue.get('text', '')
                    issue_message = issue.get('message', '')
                    
                    if len(issue_text) < 10 and len(issue_message) < 10:
                        print(f"      ⚠️  POTENTIAL PROBLEM: Very short issue description")
                    
                    if issue_text == issue_message:
                        print(f"      ℹ️  Note: Text and message are identical")
                    
                    if not issue_text and not issue_message:
                        print(f"      ❌ PROBLEM: No issue description found!")
            
            # Check for unmatched issues in raw response
            print(f"\n🔍 RAW RESPONSE STRUCTURE CHECK")
            print("-" * 40)
            
            # Look for any other issue data that might not be in sentences
            raw_json = json.dumps(result, indent=2)
            if 'issue' in raw_json.lower() or 'error' in raw_json.lower():
                print("Found issue/error related data in response:")
                # Search for issue patterns
                import re
                issue_patterns = re.findall(r'"[^"]*issue[^"]*":\s*"[^"]*"', raw_json, re.IGNORECASE)
                for pattern in issue_patterns[:5]:  # Show first 5 matches
                    print(f"  {pattern}")
            
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_web_interface_detailed()
