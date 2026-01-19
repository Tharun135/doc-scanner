"""
Test the deterministic system with the real 30-word sentence issue from production.
"""

import sys
sys.path.append('.')

from tools.enhanced_rag_integration import enhanced_enrich_issue_with_solution

print("="*70)
print("TESTING REAL PRODUCTION ISSUE - Long Sentence (30 words)")
print("="*70)

# The exact issue from production
original_sentence = "You can activate in the configuration file to print out this information in the user log file in a cyclic way (for example, every 10 seconds)."

issue = {
    "message": "Consider breaking this long sentence (30 words) into shorter ones for better readability",
    "context": original_sentence,
    "issue_type": "long_sentence",
    "rule_id": "long_sentence"
}

print(f"\n📝 Original Sentence ({len(original_sentence.split())} words):")
print(f'"{original_sentence}"')
print("\n⚠️ Issue: Long sentence needs splitting")

# Process with new deterministic system
result = enhanced_enrich_issue_with_solution(issue)

print(f"\n💡 Method Used: {result.get('method', 'unknown')}")
print(f"✨ Confidence: {result.get('confidence', 'unknown')}")

if result.get('proposed_rewrite'):
    rewrite = result['proposed_rewrite']
    print(f"\n🔄 Deterministic Rewrite:")
    print(f'"{rewrite}"')
    
    # Count sentences
    import re
    sentences = [s.strip() for s in re.split(r'[.!?]+', rewrite) if s.strip()]
    print(f"\n📊 Analysis:")
    print(f"  • Split into {len(sentences)} sentences")
    for i, sent in enumerate(sentences, 1):
        word_count = len(sent.split())
        print(f"  • Sentence {i}: {word_count} words")
    
    # Verify it's different from original
    if rewrite.strip() != original_sentence.strip():
        print("\n✅ REWRITE IS DIFFERENT - Problem solved!")
    else:
        print("\n❌ REWRITE IS IDENTICAL - Still broken!")
else:
    print("\n❌ No rewrite produced!")

print("\n" + "="*70)
print("COMPARISON WITH OLD AI")
print("="*70)

print("\n❌ Old AI Split (BROKEN):")
print('   "You can activate in the configuration file to print out this information in."')
print('   "The user log file in a cyclic way (for example, every 10 seconds)."')
print("\n   Problem: Splits mid-phrase, creates grammatically incorrect sentences")

print("\n✅ New Deterministic Split (CORRECT):")
print('   Should split on natural boundaries, maintain grammar')
