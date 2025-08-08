#!/usr/bin/env python3

"""
Script to identify performance issues in rule files.
"""

import os
import re

def analyze_rule_files():
    """Analyze all rule files for performance issues."""
    
    rule_dir = "d:/doc-scanner/app/rules"
    issues_found = []
    
    for filename in os.listdir(rule_dir):
        if filename.endswith('.py') and filename != '__init__.py' and filename != 'spacy_utils.py':
            filepath = os.path.join(rule_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_issues = []
                
                # Check for individual spaCy loading
                if 'spacy.load(' in content:
                    file_issues.append("❌ CRITICAL: Individual spaCy model loading")
                
                # Check for unused spaCy processing
                if 'doc = nlp(' in content:
                    # Check if doc is actually used
                    doc_usage_patterns = [r'doc\.', r'\bdoc\b(?!\s*=)']
                    doc_used = any(re.search(pattern, content) for pattern in doc_usage_patterns)
                    if not doc_used:
                        file_issues.append("❌ HIGH: Unused spaCy document processing")
                
                # Check for BeautifulSoup usage
                if 'BeautifulSoup(' in content:
                    file_issues.append("⚠️  MEDIUM: Individual HTML parsing")
                
                # Check if using shared spacy utils
                if 'from .spacy_utils import' in content:
                    file_issues.append("✅ GOOD: Using shared spaCy utilities")
                
                if file_issues:
                    issues_found.append({
                        'file': filename,
                        'issues': file_issues
                    })
                    
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return issues_found

def main():
    print("🔍 ANALYZING RULE FILES FOR PERFORMANCE ISSUES")
    print("=" * 70)
    
    issues = analyze_rule_files()
    
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    for file_info in issues:
        print(f"\n📁 {file_info['file']}")
        for issue in file_info['issues']:
            print(f"   {issue}")
            if "CRITICAL" in issue:
                critical_count += 1
            elif "HIGH" in issue:
                high_count += 1
            elif "MEDIUM" in issue:
                medium_count += 1
    
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY:")
    print(f"   🔥 CRITICAL issues: {critical_count} (spaCy model loading)")
    print(f"   ⚠️  HIGH issues: {high_count} (unused spaCy processing)")
    print(f"   📋 MEDIUM issues: {medium_count} (individual HTML parsing)")
    print(f"   📁 Total files with issues: {len(issues)}")
    
    if critical_count > 0:
        print(f"\n🚨 URGENT: {critical_count} files are loading spaCy individually!")
        print("   This could add 2-10 seconds to document analysis time.")
        print("   Recommend converting all to use shared spacy_utils.")

if __name__ == "__main__":
    main()
