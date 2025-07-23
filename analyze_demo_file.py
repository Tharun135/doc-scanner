#!/usr/bin/env python3
"""
Direct File Analysis Tool
Analyzes your test_demo.md file and shows the same results you'd see in VS Code
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('.')

def analyze_test_demo_file():
    """Analyze the test_demo.md file directly"""
    print("🔍 Document Review Agent - File Analysis")
    print("=" * 70)
    
    # Import the analysis functions
    try:
        from app.app import analyze_sentence, load_rules
        print("✅ Successfully imported analysis functions")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Load the rules
    print("\\n📚 Loading analysis rules...")
    rules = load_rules()
    print(f"✅ Loaded {len(rules)} rules")
    
    # Read the test demo file
    file_path = "test_demo.md"
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\\n📄 Analyzing file: {file_path}")
    print(f"📊 File size: {len(content)} characters")
    print("-" * 70)
    
    # Split into lines and analyze each line
    lines = [line.strip() for line in content.split('\\n') if line.strip() and not line.startswith('#')]
    total_issues = 0
    all_issues = []
    
    for i, line in enumerate(lines, 1):
        if len(line) > 10:  # Skip very short lines
            print(f"\\nLine {i}: {line}")
            
            # Analyze the sentence
            feedback, readability_scores, quality_score = analyze_sentence(line, rules)
            
            if feedback:
                print(f"  🔴 Found {len(feedback)} issues:")
                for issue in feedback:
                    issue_text = issue.get('message', str(issue)) if isinstance(issue, dict) else str(issue)
                    print(f"    • {issue_text}")
                    
                    # Store for summary
                    all_issues.append({
                        'line': i,
                        'content': line,
                        'issue': issue_text
                    })
                
                total_issues += len(feedback)
            else:
                print("  ✅ No issues found")
    
    # Summary
    print("\\n" + "=" * 70)
    print(f"📊 ANALYSIS SUMMARY")
    print(f"📁 File: {file_path}")
    print(f"📏 Lines analyzed: {len(lines)}")
    print(f"🔴 Total issues found: {total_issues}")
    print("=" * 70)
    
    if all_issues:
        print("\\n🔍 DETAILED ISSUES:")
        for issue in all_issues:
            print(f"Line {issue['line']}: {issue['issue']}")
    
    print("\\n✨ This is exactly what you would see in VS Code with the extension!")
    return total_issues > 0

if __name__ == "__main__":
    analyze_test_demo_file()
