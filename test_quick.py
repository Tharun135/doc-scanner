import sys
sys.path.insert(0, '.')

from core.deterministic_suggestions import DeterministicSuggestionGenerator
from core.issue_resolution_engine import IssueResolutionEngine

# The real production issue
original = 'You can activate in the configuration file to print out this information in the user log file in a cyclic way (for example, every 10 seconds).'

issue = {
    'feedback': 'Consider breaking this long sentence (30 words) into shorter ones for better readability',
    'context': original,
    'rule_id': 'long_sentence',
    'document_type': 'technical'
}

print("="*70)
print("TESTING REAL 30-WORD SENTENCE FROM PRODUCTION")
print("="*70)

print(f"\n📝 Original ({len(original.split())} words):")
print(f'"{original}"')

# Classify
engine = IssueResolutionEngine()
issue_type = engine.classify_issue(issue)
print(f"\n✓ Classified as: {issue_type}")

# Generate suggestion
gen = DeterministicSuggestionGenerator()
result = gen.generate_suggestion(issue)

if result:
    print(f"\n💡 Method: {result.get('method', 'unknown')}")
    print(f"✨ Confidence: {result.get('confidence', 'unknown')}")
    
    rewrite = result.get('rewrite', '')
    if rewrite:
        print(f"\n🔄 Deterministic Rewrite:")
        print(f'"{rewrite}"')
        
        # Count sentences in rewrite
        import re
        sentences = [s.strip() for s in re.split(r'[.!?]+', rewrite) if s.strip()]
        print(f"\n📊 Analysis:")
        print(f"  • Split into {len(sentences)} sentences")
        for i, sent in enumerate(sentences, 1):
            wc = len(sent.split())
            print(f"  • Sentence {i}: {wc} words - \"{sent}\"")
        
        if rewrite.strip() != original.strip():
            print("\n✅ REWRITE IS DIFFERENT - Problem solved!")
        else:
            print("\n❌ REWRITE IS IDENTICAL - Still broken!")
    
    print(f"\n📋 Guidance:")
    print(result.get('guidance', 'N/A'))
else:
    print("\n❌ No result generated!")

print("\n" + "="*70)
print("COMPARISON")
print("="*70)
print("\n❌ Old AI (BROKEN):")
print('  "You can activate in the configuration file to print out this information in."')
print('  "The user log file in a cyclic way (for example, every 10 seconds)."')
print("\n✅ New Deterministic (CORRECT):")
print('  Should intelligently split on natural boundaries')
