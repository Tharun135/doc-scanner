#!/usr/bin/env python3
"""
Debug script to investigate sentence highlighting issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import tempfile
import requests
import json

def debug_sentence_highlighting():
    """Debug the sentence highlighting issue"""
    
    # Create a test document with bullet points like the user described
    test_content = """# Security Information for Industrial Edge App

The following security considerations must be met:

• Customer is responsible for configuring the application as per the installation/user manual, based on system requirements

• The operator personnel accessing the system is well trained in the usage of the system

• Operator is responsible for configuring the PLCs with appropriate read/write access levels (Legitimization)

These requirements ensure proper security implementation."""

    print("🔍 Debugging sentence highlighting issues...")
    print("Test content:")
    print(test_content)
    print("\n" + "="*70 + "\n")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_path = f.name
    
    try:
        # Upload and analyze
        with open(temp_path, 'rb') as f:
            response = requests.post('http://127.0.0.1:5000/upload', 
                                   files={'file': ('test.md', f, 'text/markdown')})
        
        if response.status_code == 200:
            result = response.json()
            sentences = result.get('sentences', [])
            
            print(f"📊 Analysis Results:")
            print(f"Total sentences: {len(sentences)}")
            print("\n" + "="*70 + "\n")
            
            # Check each sentence and its issues
            total_issues = 0
            for i, sentence in enumerate(sentences):
                feedback = sentence.get('feedback', [])
                sentence_text = sentence.get('sentence', '')
                
                print(f"Sentence {i+1}:")
                print(f"  Text: {sentence_text[:100]}...")
                print(f"  Issues: {len(feedback)}")
                
                for j, issue in enumerate(feedback):
                    total_issues += 1
                    print(f"    Issue {j+1}: {issue.get('message', 'No message')}")
                    print(f"    Text: {issue.get('text', 'No text')}")
                    print(f"    Position: {issue.get('start', 'N/A')}-{issue.get('end', 'N/A')}")
                
                print()
            
            print(f"Total issues found: {total_issues}")
            
            # Check for the specific problem: multiple identical issues on sentence 1
            first_sentence_issues = sentences[0].get('feedback', []) if sentences else []
            if len(first_sentence_issues) > 1:
                print(f"\n🚨 PROBLEM DETECTED: Sentence 1 has {len(first_sentence_issues)} issues")
                
                # Check if they're duplicates
                messages = [issue.get('message', '') for issue in first_sentence_issues]
                unique_messages = set(messages)
                
                if len(unique_messages) < len(messages):
                    print("❌ DUPLICATE ISSUES DETECTED!")
                
                # Check if all issues have same text/position
                texts = [issue.get('text', '') for issue in first_sentence_issues]
                positions = [(issue.get('start'), issue.get('end')) for issue in first_sentence_issues]
                
                print("Issue details:")
                for i, issue in enumerate(first_sentence_issues):
                    print(f"  Issue {i+1}: {issue.get('message', 'No message')}")
                    print(f"    Text: '{issue.get('text', 'No text')}'")
                    print(f"    Position: {issue.get('start', 'N/A')}-{issue.get('end', 'N/A')}")
                    print()
                    
        else:
            print(f"❌ Server error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    debug_sentence_highlighting()
