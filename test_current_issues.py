#!/usr/bin/env python3
"""
Test the current issues with document upload and AI suggestions
"""

import requests
import json
import time
import sys

def test_document_issues():
    """Test document upload and issue detection"""
    print("🔍 TESTING DOCUMENT ISSUES")
    print("=" * 50)
    
    # Test content with various issues
    test_content = """The document was written by the author. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point. The utilization of complex terminology makes the document harder to understand."""
    
    print(f"📝 Test content: {test_content}")
    
    # Test the upload endpoint
    url = "http://localhost:5000/upload"
    files = {'file': ('test.txt', test_content.encode('utf-8'), 'text/plain')}
    
    try:
        print("\n📤 Uploading test document...")
        response = requests.post(url, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            
            # Check sentences
            sentences = result.get('sentences', [])
            print(f"📝 Sentences found: {len(sentences)}")
            
            total_issues = 0
            for i, sentence in enumerate(sentences):
                feedback = sentence.get('feedback', [])
                print(f"  Sentence {i+1}: {len(feedback)} issues")
                total_issues += len(feedback)
                
                for issue in feedback:
                    print(f"    - {issue.get('message', 'No message')}")
            
            print(f"\n📈 Total issues found: {total_issues}")
            
            if total_issues == 0:
                print("❌ PROBLEM: No issues detected!")
                return False
            else:
                print("✅ Issues detected successfully!")
                return True
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_ai_suggestions():
    """Test AI suggestion endpoint"""
    print("\n🤖 TESTING AI SUGGESTIONS")
    print("=" * 50)
    
    url = "http://localhost:5000/ai_suggestion"
    
    test_cases = [
        {
            "feedback": "Passive voice detected - consider active voice",
            "sentence": "The document was written by the author.",
            "document_type": "general"
        },
        {
            "feedback": "Long sentence detected - consider breaking into shorter sentences", 
            "sentence": "This is a very long sentence that continues to go on and on without any clear purpose.",
            "document_type": "general"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔬 Test case {i+1}: {test_case['feedback']}")
        
        try:
            response = requests.post(url, json=test_case, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI suggestion successful!")
                print(f"Method: {result.get('method', 'unknown')}")
                print(f"Suggestion: {result.get('suggestion', 'No suggestion')[:100]}...")
                print(f"Confidence: {result.get('confidence', 'unknown')}")
            else:
                print(f"❌ AI suggestion failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ AI suggestion error: {e}")

def main():
    print("🚀 TESTING CURRENT ISSUES")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server...")
    time.sleep(2)
    
    # Test document issues
    issues_working = test_document_issues()
    
    # Test AI suggestions
    test_ai_suggestions()
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print(f"Document issues working: {'✅' if issues_working else '❌'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
