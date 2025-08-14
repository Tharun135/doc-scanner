#!/usr/bin/env python3

import requests
import time
import json

def test_unclear_issues():
    """Test document content that might be causing unclear issue descriptions"""
    
    print("🔍 TESTING UNCLEAR ISSUE DESCRIPTIONS")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Waiting for server...")
    time.sleep(2)
    
    # Test content that might cause unclear issues
    test_content = """Security guidelines for usage of USB sticks within shop floor are applied.
The system uses appropriate security measures.
Customer is responsible for configuring the application security settings.
The system is installed in an environment that ensures physical access is limited to authorized maintenance personnel.
System includes hardware, firmware and operating system components.
Centralized IT security components (Active Directory, Centralized IT Logging Server) are provided and configured.
The operator personnel accessing the system is well trained.
The operator uses appropriate access controls.
Operator is responsible for configuring the PLCs with appropriate security settings."""
    
    print(f"📝 Test content with potentially unclear issues:")
    print("-" * 40)
    print(test_content)
    print("-" * 40)
    
    try:
        # Upload document
        print("\n📤 Uploading test document...")
        files = {'file': ('test_unclear.txt', test_content)}
        response = requests.post('http://localhost:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            
            sentences = result.get('sentences', [])
            print(f"📝 Sentences found: {len(sentences)}")
            
            total_issues = 0
            for i, sentence in enumerate(sentences, 1):
                issues = sentence.get('issues', [])
                if issues:
                    print(f"\n  Sentence {i}: {len(issues)} issues")
                    print(f"    Text: {sentence.get('original_text', '')[:80]}...")
                    for issue in issues:
                        issue_text = issue.get('issue', 'Unknown issue')
                        rule_type = issue.get('rule_type', 'unknown')
                        print(f"    - Issue: {issue_text}")
                        print(f"      Rule type: {rule_type}")
                        
                        # Check for unclear issue descriptions
                        if (len(issue_text) < 20 or 
                            issue_text == sentence.get('original_text', '').strip() or
                            issue_text in ['appropriate', 'hardware, firmware and operating']):
                            print(f"      ⚠️  UNCLEAR ISSUE DETECTED: '{issue_text}'")
                        
                        total_issues += 1
                else:
                    print(f"\n  Sentence {i}: 0 issues")
                    print(f"    Text: {sentence.get('original_text', '')[:80]}...")
            
            print(f"\n📈 Total issues found: {total_issues}")
            
            # Also check the raw response structure
            print("\n🔍 RAW RESPONSE ANALYSIS")
            print("-" * 40)
            print(json.dumps(result, indent=2)[:1000] + "..." if len(json.dumps(result, indent=2)) > 1000 else json.dumps(result, indent=2))
            
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_unclear_issues()
