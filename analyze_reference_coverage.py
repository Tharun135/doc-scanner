"""
Analysis: Reference Files vs Existing Rules
===========================================

This script compares the JSON reference files with existing implemented rules
to identify gaps and overlaps.
"""

import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def analyze_reference_files():
    """Analyze all reference JSON files and categorize the rules."""
    
    reference_dir = "reference files"
    existing_rules_dir = "app/rules"
    
    print("🔍 ANALYSIS: Reference Files vs Existing Rules")
    print("=" * 60)
    
    # Load and categorize reference files
    reference_categories = {}
    
    for filename in os.listdir(reference_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(reference_dir, filename)
            category = filename.replace('.json', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\n📁 {category.upper()}")
                print("-" * 30)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    rules = data
                elif isinstance(data, dict) and 'rules' in data:
                    rules = data['rules']
                else:
                    rules = [data] if isinstance(data, dict) else []
                
                reference_categories[category] = rules
                print(f"Rules found: {len(rules)}")
                
                # Show first few rules as examples
                for i, rule in enumerate(rules[:3]):
                    rule_id = rule.get('id', f'rule_{i}')
                    title = rule.get('title', 'No title')
                    print(f"  • {rule_id}: {title}")
                
                if len(rules) > 3:
                    print(f"  ... and {len(rules) - 3} more")
                    
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    
    # Analyze existing rules
    print(f"\n\n🔧 EXISTING IMPLEMENTED RULES")
    print("-" * 40)
    
    existing_files = [f for f in os.listdir(existing_rules_dir) 
                     if f.endswith('.py') and f != '__init__.py' 
                     and not f.startswith('__')]
    
    print(f"Total rule files: {len(existing_files)}")
    
    # Categorize existing rules
    coverage_analysis = {
        'accessibility': [],
        'capitalization': [], 
        'clarity': [],
        'formatting': [],
        'grammar': [],
        'punctuation': [],
        'terminology': [],
        'tone': []
    }
    
    for rule_file in existing_files:
        rule_name = rule_file.replace('.py', '')
        
        # Categorize based on filename patterns
        if any(term in rule_name.lower() for term in ['access', 'inclusive']):
            coverage_analysis['accessibility'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['grammar', 'verb', 'tense']):
            coverage_analysis['grammar'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['format', 'style']):
            coverage_analysis['formatting'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['clear', 'simple', 'concise', 'readability']):
            coverage_analysis['clarity'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['tone', 'voice']):
            coverage_analysis['tone'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['terms', 'terminology']):
            coverage_analysis['terminology'].append(rule_name)
        elif any(term in rule_name.lower() for term in ['passive', 'sentence']):
            coverage_analysis['grammar'].append(rule_name)
    
    # Show coverage analysis
    print(f"\n\n📊 COVERAGE ANALYSIS")
    print("=" * 40)
    
    total_reference_rules = sum(len(rules) for rules in reference_categories.values())
    total_existing_rules = len(existing_files)
    
    print(f"📚 Reference Rules: {total_reference_rules}")
    print(f"✅ Implemented Rules: {total_existing_rules}")
    
    for category, ref_rules in reference_categories.items():
        existing_in_category = coverage_analysis.get(category, [])
        coverage_percent = (len(existing_in_category) / len(ref_rules) * 100) if ref_rules else 0
        
        print(f"\n{category.upper()}:")
        print(f"  Reference: {len(ref_rules)} rules")
        print(f"  Implemented: {len(existing_in_category)} rules")
        print(f"  Coverage: {coverage_percent:.1f}%")
        
        if existing_in_category:
            print(f"  Files: {', '.join(existing_in_category[:3])}")
            if len(existing_in_category) > 3:
                print(f"         ...and {len(existing_in_category) - 3} more")
    
    # Identify gaps
    print(f"\n\n🚨 POTENTIAL GAPS TO IMPLEMENT")
    print("=" * 40)
    
    gaps = []
    for category, ref_rules in reference_categories.items():
        existing_in_category = coverage_analysis.get(category, [])
        if len(ref_rules) > len(existing_in_category):
            gap_count = len(ref_rules) - len(existing_in_category)
            gaps.append((category, gap_count, ref_rules[:3]))  # Show first 3 as examples
    
    gaps.sort(key=lambda x: x[1], reverse=True)  # Sort by gap size
    
    for category, gap_count, example_rules in gaps:
        print(f"\n{category.upper()}: {gap_count} potential new rules")
        for rule in example_rules:
            title = rule.get('title', 'No title')
            print(f"  • {title}")
    
    return reference_categories, coverage_analysis

if __name__ == "__main__":
    analyze_reference_files()
