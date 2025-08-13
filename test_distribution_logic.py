#!/usr/bin/env python3
"""
Test the fixed distribution logic directly
"""

import time

def test_fixed_distribution():
    """Test the distribution logic with a simple simulation"""
    
    print("🔍 TESTING FIXED DISTRIBUTION LOGIC")
    print("=" * 50)
    
    # Simulate the backend detection results (21 issues found)
    document_issues = [
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Consider breaking into shorter sentences", "type": "long_sentence"},
        {"message": "Issue: Unnecessary modifier detected - consider removing 'very'", "type": "modifier"},
        {"message": "Issue: Unnecessary modifier detected - consider removing 'very'", "type": "modifier"},
        {"message": "Consider removing unnecessary modifier: 'very long'", "type": "modifier"},
        {"message": "Consider removing unnecessary modifier: 'extremely difficult'", "type": "modifier"},
        {"message": "Consider removing unnecessary modifier: 'very important'", "type": "modifier"},
        {"message": "Weak verb construction: Replace 'there are very'", "type": "weak_verb"},
        {"message": "Possible passive voice detected - consider active voice", "type": "passive_voice"},
        {"message": "Possible passive voice detected - consider active voice", "type": "passive_voice"},
        {"message": "Possible passive voice detected - consider active voice", "type": "passive_voice"},
        {"message": "Possible passive voice detected - consider active voice", "type": "passive_voice"},
        {"message": "Many sentences start with the same word", "type": "other"}
    ]
    
    # Simulate sentences (assume 6 sentences like in typical document)
    sentences = [
        "The document was written by the author.",
        "It was reviewed extensively by the team members.",
        "This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding.",
        "The utilization of complex terminology makes the document harder to understand.",
        "Additionally, there are very important points that need to be addressed.",
        "Furthermore, the implementation was conducted by the development team."
    ]
    
    print(f"Total issues to distribute: {len(document_issues)}")
    print(f"Number of sentences: {len(sentences)}")
    
    # Apply the fixed distribution logic
    issues_per_sentence = max(1, len(document_issues) // len(sentences))
    print(f"Issues per sentence (base): {issues_per_sentence}")
    
    distribution_result = []
    
    for index, sent in enumerate(sentences):
        sentence_feedback = []
        
        # Calculate which issues to assign to this sentence
        start_idx = index * issues_per_sentence
        end_idx = (index + 1) * issues_per_sentence
        
        # For the last sentence, assign any remaining issues
        if index == len(sentences) - 1:
            end_idx = len(document_issues)
        
        # Assign issues to this sentence
        for issue_idx in range(start_idx, min(end_idx, len(document_issues))):
            if issue_idx < len(document_issues):
                issue = document_issues[issue_idx]
                sentence_feedback.append({
                    "message": issue["message"],
                    "type": issue["type"],
                    "sentence_index": index
                })
        
        # If we have more issues than sentences, distribute extras to early sentences
        if len(document_issues) > len(sentences) and index < (len(document_issues) % len(sentences)):
            extra_issue_idx = len(sentences) * issues_per_sentence + index
            if extra_issue_idx < len(document_issues):
                issue = document_issues[extra_issue_idx]
                sentence_feedback.append({
                    "message": issue["message"],
                    "type": issue["type"],
                    "sentence_index": index
                })
        
        distribution_result.append({
            "sentence": sent[:60] + "..." if len(sent) > 60 else sent,
            "issues": sentence_feedback
        })
    
    # Display results
    print(f"\n📊 DISTRIBUTION RESULTS:")
    print("=" * 50)
    
    total_distributed = 0
    issue_type_counts = {}
    
    for i, result in enumerate(distribution_result):
        sentence = result["sentence"]
        issues = result["issues"]
        
        print(f"\nSentence {i+1}: '{sentence}'")
        print(f"Issues assigned: {len(issues)}")
        
        if issues:
            for j, issue in enumerate(issues):
                issue_type = issue["type"]
                print(f"  {j+1}. [{issue_type}] {issue['message'][:60]}...")
                
                # Count issue types
                issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
                total_distributed += 1
        else:
            print("  No issues assigned")
    
    print(f"\n🎯 SUMMARY:")
    print(f"Total issues distributed: {total_distributed}")
    print(f"Original issues: {len(document_issues)}")
    print(f"Distribution success: {'✅ Perfect' if total_distributed == len(document_issues) else '❌ Missing issues'}")
    
    print(f"\nIssue types distributed:")
    for issue_type, count in issue_type_counts.items():
        print(f"  {issue_type}: {count}")
    
    if len(issue_type_counts) > 1:
        print(f"\n✅ SUCCESS: Multiple issue types will be visible across sentences!")
        print(f"   You should now see {len(issue_type_counts)} different issue types in your browser")
    else:
        print(f"\n❌ PROBLEM: Only {len(issue_type_counts)} issue type distributed")

if __name__ == "__main__":
    test_fixed_distribution()
