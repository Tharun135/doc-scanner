#!/usr/bin/env python3
"""
Rule Summary Report - Shows all active rules and their capabilities
"""

import sys
import os
sys.path.append('.')

def show_rule_summary():
    print("📊 DOCUMENT SCANNER - RULE SUMMARY REPORT")
    print("=" * 60)
    print(f"📅 Generated: August 20, 2025")
    print(f"🔧 Total Active Rules: 9")
    print()
    
    rules_info = [
        {
            "name": "consistency_rules.py",
            "category": "🔍 Consistency",
            "checks": [
                "Step numbering consistency (1., 2., 3...)",
                "Units of measure standardization",
                "Terminology consistency",
                "Heading capitalization consistency"
            ]
        },
        {
            "name": "grammar_rules.py", 
            "category": "📝 Grammar",
            "checks": [
                "Multiple consecutive spaces",
                "Subject-verb agreement",
                "Sentence capitalization (ignores markdown info syntax)",
                "Overly long sentences (30+ words)"
            ],
            "disabled": ["Repeating punctuation (!!, ??)"]
        },
        {
            "name": "long_sentence.py",
            "category": "📏 Readability", 
            "checks": [
                "Sentences longer than 25 words"
            ]
        },
        {
            "name": "nominalizations.py",
            "category": "✏️ Style",
            "checks": [
                "Nominalization patterns (-tion, -ment, -ness, etc.)",
                "Suggests verb forms instead"
            ]
        },
        {
            "name": "passive_voice.py",
            "category": "📢 Voice",
            "checks": [
                "Passive voice constructions (using spaCy dependencies)"
            ]
        },
        {
            "name": "readability_rules.py",
            "category": "📖 Readability",
            "checks": [
                "Sentence length analysis", 
                "Grade level assessment (Flesch-Kincaid)"
            ],
            "disabled": ["Flesch Reading Ease score warnings"]
        },
        {
            "name": "style_rules.py",
            "category": "🎨 Style",
            "checks": [
                "Passive voice patterns (regex-based)",
                "ALL CAPS usage (ignores markdown info syntax)",
                "Adverb overuse (-ly endings)",
                "Overuse of 'very'"
            ],
            "disabled": ["Multiple exclamation marks"]
        },
        {
            "name": "terminology_rules.py",
            "category": "📚 Terminology",
            "checks": [
                "Preferred terminology (login vs log in, etc.)",
                "Abbreviation consistency",
                "Hyphenated terms consistency"
            ]
        },
        {
            "name": "vague_terms.py",
            "category": "🎯 Precision",
            "checks": [
                "Vague terms (some, several, various, stuff, things)"
            ]
        }
    ]
    
    for i, rule in enumerate(rules_info, 1):
        print(f"{i:2d}. {rule['category']} - {rule['name']}")
        print("    ✅ Active Checks:")
        for check in rule['checks']:
            print(f"       • {check}")
        
        if 'disabled' in rule:
            print("    ❌ Disabled Checks:")
            for disabled in rule['disabled']:
                print(f"       • {disabled}")
        print()
    
    print("🔧 CUSTOMIZATIONS APPLIED:")
    print("=" * 30)
    print("❌ Removed Rules:")
    print("   • Low readability (Flesch score) warnings")
    print("   • Repeating punctuation (!!, ??) warnings") 
    print("   • Multiple exclamation marks warnings")
    print()
    print("🔧 Modified Rules:")
    print("   • Sentence capitalization: ignores markdown info syntax")
    print("   • ALL CAPS detection: ignores markdown info syntax") 
    print("     (info \"NOTICE\", warning \"TEXT\", etc.)")
    print()
    print("🎯 SUPPORTED MARKDOWN SYNTAX:")
    print("   • info \"TEXT\"")
    print("   • warning \"TEXT\"") 
    print("   • note \"TEXT\"")
    print("   • tip \"TEXT\"")
    print("   • caution \"TEXT\"")

if __name__ == "__main__":
    show_rule_summary()
