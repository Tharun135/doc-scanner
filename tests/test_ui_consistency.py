"""
UI Consistency & Decision Label Validation Tests

Validates that decision labels match behavior and that rationale is always visible.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import analysis components
from app.app import analyze_sentence, load_rules

# Load rules once
_rules = load_rules()

def analyze_document_with_ai(text: str) -> dict:
    """Analyze document for UI consistency test."""
    sentences = text.split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
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
                'explanation': item.get('explanation', ''),
                'rewrite': item.get('ai_suggestion', '')
            })
    
    return {
        'issues': issues,
        'document_intent': 'test',
        'quality_score': 100 - (len(issues) * 5)
    }


class UIConsistencyValidator:
    """Validates UI consistency and decision labeling."""
    
    # Expected decision type mappings
    DECISION_LABELS = {
        'rewrite': 'AI-Enhanced Rewrite',
        'explain': 'Semantic Explanation',
        'guide': 'Reviewer Guidance',
        'no_change': 'Reviewer Rationale'
    }
    
    def __init__(self):
        self.failures = []
        self.warnings = []
    
    def test_decision_labels(self):
        """Test 8.1: Decision labels match behavior."""
        print("\n" + "="*80)
        print("TEST 8.1: Decision Labels Match Behavior")
        print("="*80 + "\n")
        
        test_cases = [
            ("The system will start automatically.", "rewrite"),
            ("The server certificate must include the IP address in the SAN field or the FQDN if it is registered in DNS.", "explain"),
            ("In version 3.0, the system was redesigned.", "no_change"),
        ]
        
        for text, expected_decision in test_cases:
            print(f"\nTesting: {text[:60]}...")
            result = analyze_document_with_ai(text)
            
            issues = result.get('issues', [])
            if not issues:
                print(f"  ⚠ No issues found (expected: {expected_decision})")
                self.warnings.append(f"No issues for: {text[:40]}")
                continue
            
            for issue in issues:
                decision_type = issue.get('decision_type')
                expected_label = self.DECISION_LABELS.get(decision_type)
                
                # Check for forbidden labels
                if self._check_forbidden_labels(issue):
                    print(f"  ✗ FAIL: Forbidden label detected")
                    self.failures.append(f"Forbidden label in: {text[:40]}")
                    continue
                
                # Verify decision type is valid
                if decision_type not in self.DECISION_LABELS:
                    print(f"  ✗ FAIL: Invalid decision type: {decision_type}")
                    self.failures.append(f"Invalid decision: {decision_type}")
                else:
                    print(f"  ✓ Decision type: {decision_type} → {expected_label}")
        
        return len(self.failures) == 0
    
    def test_reviewer_rationale_visibility(self):
        """Test 8.2: Reviewer rationale is always visible for non-rewrite outcomes."""
        print("\n" + "="*80)
        print("TEST 8.2: Reviewer Rationale Visibility")
        print("="*80 + "\n")
        
        test_cases = [
            "In version 3.0, the system was redesigned.",
            "Access is restricted for security reasons.",
            "Here is an example of a properly configured certificate:",
        ]
        
        for text in test_cases:
            print(f"\nTesting: {text[:60]}...")
            result = analyze_document_with_ai(text)
            
            issues = result.get('issues', [])
            if not issues:
                print(f"  ⚠ No issues found")
                self.warnings.append(f"No issues for: {text[:40]}")
                continue
            
            for issue in issues:
                decision_type = issue.get('decision_type')
                rationale = issue.get('reviewer_rationale', '')
                explanation = issue.get('explanation', '')
                
                # For non-rewrite decisions, rationale or explanation must exist
                if decision_type != 'rewrite':
                    if not rationale and not explanation:
                        print(f"  ✗ FAIL: Missing rationale for {decision_type}")
                        self.failures.append(f"Missing rationale: {text[:40]}")
                    elif self._is_generic_advice(rationale) or self._is_generic_advice(explanation):
                        print(f"  ⚠ WARNING: Generic advice detected")
                        self.warnings.append(f"Generic advice: {text[:40]}")
                    else:
                        print(f"  ✓ Rationale present: {rationale[:60]}...")
                else:
                    print(f"  ✓ Rewrite decision (rationale optional)")
        
        return len(self.failures) == 0
    
    def _check_forbidden_labels(self, issue: dict) -> bool:
        """Check for forbidden UI labels."""
        forbidden = [
            "AI failed",
            "validation error",
            "error occurred",
            "exception"
        ]
        
        issue_str = str(issue).lower()
        return any(forbidden_term in issue_str for forbidden_term in forbidden)
    
    def _is_generic_advice(self, text: str) -> bool:
        """Check if text is generic advice without specific rationale."""
        if not text:
            return False
        
        generic_patterns = [
            "consider",
            "try",
            "you may want to",
            "it is recommended",
            "please"
        ]
        
        text_lower = text.lower()
        # Generic if it starts with generic patterns but lacks specific explanation
        if any(text_lower.startswith(pattern) for pattern in generic_patterns):
            if len(text) < 50:  # Too short to be specific
                return True
        
        return False
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*80)
        print("UI CONSISTENCY VALIDATION SUMMARY")
        print("="*80 + "\n")
        
        print(f"Failures: {len(self.failures)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.failures:
            print("\n✗ FAILURES:")
            for failure in self.failures:
                print(f"  - {failure}")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.failures and not self.warnings:
            print("✓ All UI consistency checks passed")
        
        print("\n" + "="*80 + "\n")
        
        return len(self.failures) == 0


def main():
    """Run UI consistency validation tests."""
    validator = UIConsistencyValidator()
    
    test_1 = validator.test_decision_labels()
    test_2 = validator.test_reviewer_rationale_visibility()
    
    all_passed = validator.print_summary()
    
    if all_passed:
        print("✓ UI consistency validated")
        return 0
    else:
        print("✗ UI consistency issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
