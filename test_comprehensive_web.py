#!/usr/bin/env python3
"""Test with the exact content the user might be using"""

import requests
import io

# Test content similar to what user might be testing
test_content = """
The document was written. It was reviewed by the team. The process will be finalized soon.
This is a very long sentence that contains redundant phrases that make it wordy and difficult to read which is problematic for clarity.
The utilization of complex terminology makes the document harder to understand.
There are mistakes in spelling and grammar that need fixing.
In order to make use of the system, you should perform an analysis and conduct a review.
The user can click on the button to access the file.
"""

print("Testing web interface with comprehensive content...")
print("=" * 60)
print(f"Content to analyze:\n{test_content}")
print("=" * 60)

url = "http://127.0.0.1:5000/upload"

# Create a file-like object
file_content = test_content.encode('utf-8')
files = {
    'file': ('test_document.txt', io.BytesIO(file_content), 'text/plain')
}

try:
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nNumber of sentences analyzed: {len(result.get('sentences', []))}")
        
        total_issues = 0
        issue_types = {}
        
        for i, sentence in enumerate(result.get('sentences', [])):
            issues = sentence.get('feedback', [])  # FIXED: Use 'feedback' instead of 'issues'
            total_issues += len(issues)
            
            print(f"\nSentence {i+1}: '{sentence.get('text', '')[:50]}...'")
            print(f"  Issues found: {len(issues)}")
            
            for j, issue in enumerate(issues):
                issue_text = issue.get('message', issue.get('suggestion', 'No description'))
                print(f"    {j+1}. {issue_text}")
                
                # Categorize issues
                if 'passive voice' in issue_text.lower():
                    issue_types['Passive Voice'] = issue_types.get('Passive Voice', 0) + 1
                elif 'long sentence' in issue_text.lower() or 'breaking' in issue_text.lower():
                    issue_types['Long Sentences'] = issue_types.get('Long Sentences', 0) + 1
                elif 'utilize' in issue_text.lower() or 'verbose' in issue_text.lower():
                    issue_types['Concise Words'] = issue_types.get('Concise Words', 0) + 1
                elif 'modifier' in issue_text.lower() or 'very' in issue_text.lower():
                    issue_types['Unnecessary Modifiers'] = issue_types.get('Unnecessary Modifiers', 0) + 1
                elif 'in order to' in issue_text.lower() or 'make use of' in issue_text.lower():
                    issue_types['Wordy Phrases'] = issue_types.get('Wordy Phrases', 0) + 1
                elif 'perform an analysis' in issue_text.lower() or 'conduct a review' in issue_text.lower():
                    issue_types['Weak Verbs'] = issue_types.get('Weak Verbs', 0) + 1
                else:
                    issue_types['Other'] = issue_types.get('Other', 0) + 1
        
        print(f"\n" + "=" * 60)
        print(f"TOTAL ISSUES FOUND: {total_issues}")
        print(f"\nISSUE BREAKDOWN BY TYPE:")
        for issue_type, count in issue_types.items():
            print(f"  - {issue_type}: {count} issues")
        
        print(f"\nQuality Score: {result.get('report', {}).get('avgQualityScore', 'N/A')}")
        print(f"Total Sentences: {result.get('report', {}).get('totalSentences', 'N/A')}")
        print(f"Total Words: {result.get('report', {}).get('totalWords', 'N/A')}")
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error testing web interface: {e}")
