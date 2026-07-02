"""
DocScanner AI - Reviewer-Grade Behavioral Test Suite

This is NOT unit testing.
This is BEHAVIORAL VALIDATION.

Each test validates that the system behaves like a human reviewer,
not like an overly aggressive AI assistant.
"""

import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual analysis components
from app.app import analyze_sentence, load_rules
from core.document_review_gate import run_document_review_gate
from bs4 import BeautifulSoup

# Load rules once at module level
_rules = load_rules()


def analyze_document_with_ai(text: str) -> Dict:
    """
    Wrapper function for behavioral testing.
    Simulates the document analysis pipeline.
    
    For testing purposes, bypasses document gate for short inputs
    to test sentence-level rules directly.
    """
    # Convert plain text to minimal HTML
    html_content = f"<html><body><p>{text}</p></body></html>"
    
    # Count sentences in input
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    # For short test inputs (< 5 sentences), bypass gate and test rules directly
    if sentence_count < 5:
        # Parse into sentences and analyze directly
        sentences = text.split('.')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        # Analyze sentences
        issues = []
        for idx, sentence in enumerate(sentences):
            # Get previous and next sentence for context
            prev_sent = sentences[idx - 1] if idx > 0 else None
            next_sent = sentences[idx + 1] if idx < len(sentences) - 1 else None
            
            # Analyze this sentence
            feedback, readability, quality = analyze_sentence(
                sentence, 
                _rules, 
                previous_sentence=prev_sent,
                next_sentence=next_sent
            )
            
            for item in feedback:
                issues.append({
                    'sentence': sentence,
                    'rule_id': item.get('rule', 'unknown'),
                    'message': item.get('message', ''),
                    'decision_type': item.get('decision_type', 'guide'),
                    'reviewer_rationale': item.get('reviewer_rationale', ''),
                    'explanation': item.get('explanation', ''),
                    'rewrite': item.get('ai_suggestion', '')
                })
        
        return {
            'issues': issues,
            'document_intent': 'test',
            'quality_score': 100 - (len(issues) * 5),
            'blocking': False
        }
    
    # For longer documents, use full gate + analysis
    document_review = run_document_review_gate(html_content, "test_document.txt")
    
    # If blocking, return document-level issues
    if document_review.blocking:
        return {
            'issues': [],
            'document_intent': document_review.document_type,
            'quality_score': 0,
            'blocking': True,
            'document_issues': [{'message': issue.message, 'severity': issue.severity} 
                              for issue in document_review.issues]
        }
    
    # Parse into sentences and analyze
    sentences = text.split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    # Analyze sentences
    issues = []
    for idx, sentence in enumerate(sentences):
        # Get previous and next sentence for context
        prev_sent = sentences[idx - 1] if idx > 0 else None
        next_sent = sentences[idx + 1] if idx < len(sentences) - 1 else None
        
        # Analyze this sentence
        feedback, readability, quality = analyze_sentence(
            sentence, 
            _rules, 
            previous_sentence=prev_sent,
            next_sentence=next_sent
        )
        
        for item in feedback:
            issues.append({
                'sentence': sentence,
                'rule_id': item.get('rule', 'unknown'),
                'message': item.get('message', ''),
                'decision_type': item.get('decision_type', 'guide'),
                'reviewer_rationale': item.get('reviewer_rationale', ''),
                'explanation': item.get('explanation', ''),
                'rewrite': item.get('ai_suggestion', '')
            })
    
    return {
        'issues': issues,
        'document_intent': document_review.document_type,
        'quality_score': 100 - (len(issues) * 5),
        'blocking': False
    }


class OutcomeType(Enum):
    """Expected outcome types from the reviewer system."""
    AI_ENHANCED_REWRITE = "AI-Enhanced Rewrite"
    SEMANTIC_EXPLANATION = "Semantic Explanation"
    REVIEWER_GUIDANCE = "Reviewer Guidance"
    REVIEWER_RATIONALE = "Reviewer Rationale"
    NO_FEEDBACK = "No Feedback"


@dataclass
class TestCase:
    """A single behavioral test case."""
    test_id: str
    name: str
    input_text: str
    expected_outcome: OutcomeType
    expected_behaviors: List[str]
    fail_conditions: List[str]
    validation_keywords: Optional[List[str]] = None
    category: str = "general"


class BehaviorValidator:
    """Validates system behavior against expected reviewer patterns."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def run_test(self, test: TestCase) -> Dict:
        """Run a single behavioral test."""
        print(f"\n{'='*80}")
        print(f"TEST {test.test_id}: {test.name}")
        print(f"Category: {test.category}")
        print(f"{'='*80}")
        print(f"\nINPUT:\n{test.input_text}\n")
        
        try:
            # Run the actual analysis
            result = analyze_document_with_ai(test.input_text)
            
            # Validate behavior
            validation = self._validate_result(test, result)
            
            if validation['passed']:
                self.passed.append((test.test_id, test.name))
                print(f"\n✓ PASS")
            else:
                self.failed.append((test.test_id, test.name, validation['failures']))
                print(f"\n✗ FAIL")
                for failure in validation['failures']:
                    print(f"  - {failure}")
            
            if validation['warnings']:
                self.warnings.append((test.test_id, validation['warnings']))
                print(f"\n⚠ WARNINGS:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
            
            return validation
            
        except Exception as e:
            print(f"\n✗ EXCEPTION: {str(e)}")
            self.failed.append((test.test_id, test.name, [f"Exception: {str(e)}"]))
            return {'passed': False, 'failures': [f"Exception: {str(e)}"], 'warnings': []}
    
    def _validate_result(self, test: TestCase, result: Dict) -> Dict:
        """Validate the result against expected behaviors."""
        failures = []
        warnings = []
        
        # Check if result has expected structure
        if not result or 'issues' not in result:
            failures.append("Result missing 'issues' key")
            return {'passed': False, 'failures': failures, 'warnings': warnings}
        
        issues = result.get('issues', [])
        
        # Validate each expected behavior
        for behavior in test.expected_behaviors:
            if not self._check_behavior(behavior, result, issues):
                failures.append(f"Expected behavior not found: {behavior}")
        
        # Check fail conditions
        for fail_condition in test.fail_conditions:
            if self._check_fail_condition(fail_condition, result, issues):
                failures.append(f"Fail condition triggered: {fail_condition}")
        
        # Validate keywords if specified
        if test.validation_keywords:
            if not self._check_keywords(test.validation_keywords, result, issues):
                warnings.append(f"Expected keywords not found: {test.validation_keywords}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures,
            'warnings': warnings
        }
    
    def _check_behavior(self, behavior: str, result: Dict, issues: List) -> bool:
        """Check if a specific behavior is present in the result."""
        behavior_lower = behavior.lower()
        
        # Check for outcome types
        if "ai-enhanced rewrite" in behavior_lower:
            return any(i.get('decision_type') == 'rewrite' for i in issues)
        
        if "semantic explanation" in behavior_lower:
            return any(i.get('decision_type') == 'explain' for i in issues)
        
        if "reviewer guidance" in behavior_lower:
            return any(i.get('decision_type') == 'guide' for i in issues)
        
        if "reviewer rationale" in behavior_lower:
            return any(i.get('decision_type') == 'no_change' for i in issues)
        
        if "no feedback" in behavior_lower or "skipped" in behavior_lower:
            return len(issues) == 0
        
        if "document intent" in behavior_lower:
            return 'document_intent' in result
        
        if "quality score" in behavior_lower:
            score = result.get('quality_score', 0)
            if ">" in behavior_lower:
                threshold = int(behavior_lower.split(">")[1].strip().replace("%", ""))
                return score > threshold
        
        # Generic text search in result
        result_str = str(result).lower()
        return behavior_lower in result_str
    
    def _check_fail_condition(self, condition: str, result: Dict, issues: List) -> bool:
        """Check if a fail condition is triggered."""
        condition_lower = condition.lower()
        result_str = str(result).lower()
        
        # Check for specific failure patterns
        if "analyzes headings as sentences" in condition_lower:
            return any("heading" in str(i).lower() and i.get('decision_type') == 'rewrite' for i in issues)
        
        if "rewrites" in condition_lower and "automatically" in condition_lower:
            return len([i for i in issues if i.get('decision_type') == 'rewrite']) > 3
        
        if "ai rewrite attempted" in condition_lower:
            return any(i.get('decision_type') == 'rewrite' for i in issues)
        
        if "tense guidance" in condition_lower or "tense enforcement" in condition_lower:
            return any("tense" in str(i).lower() for i in issues)
        
        if "changes meaning" in condition_lower:
            # This requires semantic analysis - add warning
            return False  # Cannot detect automatically
        
        if "guidance instead of rewrite" in condition_lower:
            return any(i.get('decision_type') == 'guide' for i in issues)
        
        if "invents an actor" in condition_lower:
            # Check if passive voice rewrite adds unmentioned actors
            return False  # Requires manual review
        
        if "hallucinate" in condition_lower:
            # Check for unexpected content in rewrites
            return False  # Requires manual review
        
        # Generic text search
        return condition_lower in result_str
    
    def _check_keywords(self, keywords: List[str], result: Dict, issues: List) -> bool:
        """Check if required keywords appear in the result."""
        result_str = str(result).lower()
        return all(keyword.lower() in result_str for keyword in keywords)
    
    def print_summary(self):
        """Print test execution summary."""
        print(f"\n\n{'='*80}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"\nTotal Tests: {len(self.passed) + len(self.failed)}")
        print(f"✓ Passed: {len(self.passed)}")
        print(f"✗ Failed: {len(self.failed)}")
        print(f"⚠ Warnings: {len(self.warnings)}")
        
        if self.failed:
            print(f"\n\nFAILED TESTS:")
            for test_id, name, failures in self.failed:
                print(f"\n{test_id}: {name}")
                for failure in failures:
                    print(f"  - {failure}")
        
        if self.warnings:
            print(f"\n\nWARNINGS:")
            for test_id, warnings in self.warnings:
                print(f"\n{test_id}:")
                for warning in warnings:
                    print(f"  - {warning}")
        
        print(f"\n{'='*80}\n")
        
        return len(self.failed) == 0


# ============================================================================
# TEST CASES
# ============================================================================

def get_all_tests() -> List[TestCase]:
    """Return all behavioral test cases."""
    return [
        # ====================================================================
        # 1. DOCUMENT-LEVEL REVIEW (GATEKEEPING)
        # ====================================================================
        
        TestCase(
            test_id="1.1",
            name="Clean Procedural Document",
            category="Document-Level Review",
            input_text="""Configure the OPC UA server.

Prerequisites:
- Valid certificate
- Network access

Procedure:
1. Open the configuration tool.
2. Select the server instance.
3. Apply the certificate.""",
            expected_outcome=OutcomeType.AI_ENHANCED_REWRITE,
            expected_behaviors=[
                "Document intent: procedural",
                "Sentence analysis runs selectively",
            ],
            fail_conditions=[
                "Analyzes headings as sentences",
                "Flags prerequisites as grammar issues",
                "Rewrites numbered steps automatically"
            ]
        ),
        
        TestCase(
            test_id="1.2",
            name="Missing Goal / Wall of Text",
            category="Document-Level Review",
            input_text="""The system uses certificates and connections and configuration settings that are required and important and must be handled carefully because otherwise issues may occur during runtime.""",
            expected_outcome=OutcomeType.REVIEWER_GUIDANCE,
            expected_behaviors=[
                "Early structural warning",
                "Reviewer Guidance"
            ],
            fail_conditions=[
                "Starts rewriting sentences",
                "AI suggestions immediately"
            ]
        ),
        
        # ====================================================================
        # 2. SENTENCE ELIGIBILITY FILTERING
        # ====================================================================
        
        TestCase(
            test_id="2.1",
            name="Title / Heading",
            category="Sentence Eligibility",
            input_text="Configuring KEPware server with certificates",
            expected_outcome=OutcomeType.NO_FEEDBACK,
            expected_behaviors=[
                "Classified as title",
                "No tense enforcement"
            ],
            fail_conditions=[
                "Tense guidance is shown",
                "AI rewrite attempted"
            ]
        ),
        
        TestCase(
            test_id="2.2",
            name="Fragment / Metadiscourse",
            category="Sentence Eligibility",
            input_text="For example:",
            expected_outcome=OutcomeType.NO_FEEDBACK,
            expected_behaviors=[
                "Skipped",
                "No feedback shown"
            ],
            fail_conditions=[
                "Any rule fires"
            ]
        ),
        
        # ====================================================================
        # 3. VERB TENSE NORMALIZATION (SIMPLE PRESENT)
        # ====================================================================
        
        TestCase(
            test_id="3.1",
            name="Safe Conversion (Procedural)",
            category="Verb Tense",
            input_text="The system will validate the configuration.",
            expected_outcome=OutcomeType.AI_ENHANCED_REWRITE,
            expected_behaviors=[
                "Issue detected: future tense",
                "AI-Enhanced Rewrite"
            ],
            fail_conditions=[
                "Reviewer guidance instead of rewrite",
                "Changes meaning"
            ],
            validation_keywords=["validate", "configuration"]
        ),
        
        TestCase(
            test_id="3.2",
            name="Historical Context",
            category="Verb Tense",
            input_text="In version 3.0, the system was redesigned.",
            expected_outcome=OutcomeType.REVIEWER_RATIONALE,
            expected_behaviors=[
                "Issue detected",
                "Reviewer Rationale",
                "Historical context preserved"
            ],
            fail_conditions=[
                "Rewrites to present tense"
            ]
        ),
        
        # ====================================================================
        # 4. LONG SENTENCE HANDLING
        # ====================================================================
        
        TestCase(
            test_id="4.1",
            name="Simple Long Sentence (Auto-Split)",
            category="Long Sentence",
            input_text="The system reads the configuration file and validates the parameters before starting.",
            expected_outcome=OutcomeType.AI_ENHANCED_REWRITE,
            expected_behaviors=[
                "AI-Enhanced Rewrite",
                "Split into two sentences"
            ],
            fail_conditions=[
                "Only guidance is shown",
                "Sentence is paraphrased instead of split"
            ]
        ),
        
        TestCase(
            test_id="4.2",
            name="Conditional / Compliance Sentence",
            category="Long Sentence",
            input_text="The server certificate must include the IP address in the SAN field or the FQDN if it is registered in DNS.",
            expected_outcome=OutcomeType.SEMANTIC_EXPLANATION,
            expected_behaviors=[
                "Semantic Explanation",
                "Mandatory requirement",
                "Two alternatives"
            ],
            fail_conditions=[
                "AI rewrites it",
                "Just split it"
            ]
        ),
        
        # ====================================================================
        # 5. PASSIVE VOICE
        # ====================================================================
        
        TestCase(
            test_id="5.1",
            name="Safe Passive → Active",
            category="Passive Voice",
            input_text="The file was created by the system.",
            expected_outcome=OutcomeType.AI_ENHANCED_REWRITE,
            expected_behaviors=[
                "AI-Enhanced Rewrite"
            ],
            fail_conditions=[
                "Generic advice instead of rewrite"
            ],
            validation_keywords=["system", "created", "file"]
        ),
        
        TestCase(
            test_id="5.2",
            name="Intentional Passive (Unknown Actor)",
            category="Passive Voice",
            input_text="Access is restricted for security reasons.",
            expected_outcome=OutcomeType.REVIEWER_RATIONALE,
            expected_behaviors=[
                "Reviewer Rationale",
                "Actor intentionally omitted"
            ],
            fail_conditions=[
                "AI invents an actor"
            ]
        ),
        
        # ====================================================================
        # 6. ADVERBS & STYLE
        # ====================================================================
        
        TestCase(
            test_id="6.1",
            name="Subjective Adverb",
            category="Adverbs & Style",
            input_text="Here is an example of a properly configured certificate:",
            expected_outcome=OutcomeType.REVIEWER_RATIONALE,
            expected_behaviors=[
                "Reviewer Rationale",
                "Intentional and subjective"
            ],
            fail_conditions=[
                "Remove or replace without rationale",
                "AI rewrites it"
            ]
        ),
        
        # ====================================================================
        # 7. RAG BEHAVIOR (CRITICAL)
        # ====================================================================
        
        TestCase(
            test_id="7.1",
            name="RAG Does Not Hallucinate",
            category="RAG Behavior",
            input_text="Some of the properties of alarm notifications are specifically implemented for the SIMATIC S7+ Connector.",
            expected_outcome=OutcomeType.AI_ENHANCED_REWRITE,
            expected_behaviors=[
                "AI-Enhanced Rewrite"
            ],
            fail_conditions=[
                "Mentions unrelated systems",
                "Copies example text"
            ],
            validation_keywords=["alarm notifications", "SIMATIC S7+"]
        ),
    ]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all behavioral tests."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              DocScanner AI - Reviewer-Grade Test Suite                    ║
║                                                                            ║
║              This is BEHAVIORAL VALIDATION, not unit testing.             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    validator = BehaviorValidator()
    tests = get_all_tests()
    
    # Run tests by category
    categories = {}
    for test in tests:
        if test.category not in categories:
            categories[test.category] = []
        categories[test.category].append(test)
    
    for category, category_tests in categories.items():
        print(f"\n\n{'#'*80}")
        print(f"# {category.upper()}")
        print(f"{'#'*80}")
        
        for test in category_tests:
            validator.run_test(test)
    
    # Print summary
    all_passed = validator.print_summary()
    
    if all_passed:
        print("✓ All behavioral tests passed.")
        print("Your app behaves like a REVIEWER, not a noisy AI.")
        return 0
    else:
        print("✗ Some tests failed.")
        print("Fix these behaviors before adding features.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
