#!/usr/bin/env python3
"""
Direct test of Document Review Agent functionality
This demonstrates how the agent analyzes documents and finds issues.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('.')

def test_document_analysis():
    """Test the document analysis functionality directly"""
    print("🔍 Testing Document Review Agent Analysis...")
    print("=" * 60)
    
    # Import the analysis functions
    try:
        from app.app import analyze_sentence, load_rules
        print("✅ Successfully imported analysis functions")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Load the rules
    print("\n📚 Loading analysis rules...")
    rules = load_rules()
    print(f"✅ Loaded {len(rules)} rules")
    
    # Test document content from your test_demo.md
    test_content = """
    The report was completed by the team yesterday.
    This sentence is way too long and contains multiple clauses that make it difficult to read and understand because it goes on and on without proper breaks which can confuse readers.
    You should should check for repeated repeated words in this sentence.
    The system can detect detect various issues issues like this this.
    You can download the software from the website.
    The user may experience issues when using the feature.
    """
    
    print("\n🔍 Analyzing test content...")
    print("-" * 40)
    
    lines = [line.strip() for line in test_content.strip().split('\n') if line.strip()]
    total_issues = 0
    
    for i, line in enumerate(lines, 1):
        print(f"\nLine {i}: {line}")
        
        # Analyze the sentence
        feedback, readability_scores, quality_score = analyze_sentence(line, rules)
        
        if feedback:
            print(f"  🔴 Found {len(feedback)} issues:")
            for issue in feedback:
                if isinstance(issue, dict):
                    print(f"    • {issue.get('message', str(issue))}")
                else:
                    print(f"    • {issue}")
            total_issues += len(feedback)
        else:
            print("  ✅ No issues found")
    
    print("\n" + "=" * 60)
    print(f"📊 ANALYSIS COMPLETE")
    print(f"Total lines analyzed: {len(lines)}")
    print(f"Total issues found: {total_issues}")
    print("=" * 60)
    
    return total_issues > 0

if __name__ == "__main__":
    test_document_analysis()
