import sys
sys.path.insert(0, '.')

from core.deterministic_suggestions import DeterministicSuggestionGenerator
from core.issue_resolution_engine import IssueResolutionEngine

# The exact sentence from production
original = 'The PROFINET IO Connector provides the raw data, and the analysis of the record data must be done by the client.'

issue = {
    'feedback': 'Avoid passive voice - consider using active voice for clearer, more direct writing',
    'context': original,
    'rule_id': 'passive_voice',
    'document_type': 'technical'
}

print("="*70)
print("TESTING MODAL PASSIVE: 'must be done by the client'")
print("="*70)

print(f"\n📝 Original:")
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
        
        if rewrite.strip() != original.strip():
            print("\n✅ REWRITE IS DIFFERENT - Problem solved!")
            
            # Check if it's actually active voice now
            if 'must be done' not in rewrite.lower():
                print("✅ Passive construction removed!")
            if 'the client must' in rewrite.lower():
                print("✅ Clear actor identified (the client)!")
        else:
            print("\n❌ REWRITE IS IDENTICAL - Still broken!")
    
    print(f"\n📋 Guidance:")
    print(result.get('guidance', 'N/A'))
else:
    print("\n❌ No result generated!")

print("\n" + "="*70)
print("EXPECTED OUTPUT")
print("="*70)
print("\nThe passive part: 'the analysis of the record data must be done by the client'")
print("Should become: 'the client must do the analysis of the record data'")
print("\nFull sentence:")
print('"The PROFINET IO Connector provides the raw data, and the client must do the analysis of the record data."')
