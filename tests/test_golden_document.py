"""
Golden Document Regression Test

Run this after every major change to detect unexpected behavior shifts.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import analysis components
from app.app import analyze_sentence, load_rules
from core.document_review_gate import run_document_review_gate

# Load rules once
_rules = load_rules()

def analyze_document_with_ai(text: str) -> dict:
    """Analyze document for golden test."""
    html_content = f"<html><body>{text}</body></html>"
    
    # Run document review gate
    document_review = run_document_review_gate(html_content, "golden_document.txt")
    
    # Parse into sentences
    sentences = text.split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    # Analyze sentences
    issues = []
    for idx, sentence in enumerate(sentences):
        prev_sent = sentences[idx - 1] if idx > 0 else None
        next_sent = sentences[idx + 1] if idx < len(sentences) - 1 else None
        
        feedback, readability, quality = analyze_sentence(
            sentence, _rules, 
            previous_sentence=prev_sent,
            next_sentence=next_sent
        )
        
        for item in feedback:
            issues.append({
                'sentence': sentence,
                'rule_id': item.get('rule', 'unknown'),
                'decision_type': item.get('decision_type', 'guide'),
                'reviewer_rationale': item.get('reviewer_rationale', ''),
                'rewrite': item.get('ai_suggestion', '')
            })
    
    return {
        'issues': issues,
        'document_intent': document_review.document_type,
        'quality_score': 100 - (len(issues) * 5),
        'blocking': document_review.blocking
    }


def load_golden_document():
    """Load the golden test document."""
    golden_path = os.path.join(os.path.dirname(__file__), 'golden_document.txt')
    with open(golden_path, 'r', encoding='utf-8') as f:
        return f.read()


def run_golden_test():
    """Run the golden document through the analyzer."""
    print("="*80)
    print("GOLDEN DOCUMENT REGRESSION TEST")
    print("="*80)
    print("\nLoading golden document...")
    
    document = load_golden_document()
    
    print(f"\nDocument length: {len(document)} chars")
    print("\nRunning analysis...\n")
    
    try:
        result = analyze_document_with_ai(document)
        
        print(f"Analysis complete.")
        print(f"\nIssues found: {len(result.get('issues', []))}")
        print(f"Quality score: {result.get('quality_score', 'N/A')}")
        print(f"Document intent: {result.get('document_intent', 'N/A')}")
        
        # Categorize outcomes
        outcomes = {}
        for issue in result.get('issues', []):
            decision = issue.get('decision_type', 'unknown')
            if decision not in outcomes:
                outcomes[decision] = []
            outcomes[decision].append(issue.get('sentence', ''))
        
        print(f"\nOutcome Distribution:")
        for decision, sentences in outcomes.items():
            print(f"  {decision}: {len(sentences)}")
        
        print(f"\n{'='*80}")
        print("DETAILED RESULTS")
        print(f"{'='*80}\n")
        
        for idx, issue in enumerate(result.get('issues', []), 1):
            print(f"\n[{idx}] Sentence: {issue.get('sentence', '')[:80]}...")
            print(f"    Rule: {issue.get('rule_id', 'N/A')}")
            print(f"    Decision: {issue.get('decision_type', 'N/A')}")
            print(f"    Rationale: {issue.get('reviewer_rationale', 'N/A')[:100]}...")
            if issue.get('rewrite'):
                print(f"    Rewrite: {issue.get('rewrite', '')[:80]}...")
        
        print(f"\n{'='*80}")
        print("✓ Golden test completed successfully")
        print(f"{'='*80}\n")
        
        return result
        
    except Exception as e:
        print(f"\n✗ EXCEPTION during golden test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = run_golden_test()
    sys.exit(0 if result else 1)
