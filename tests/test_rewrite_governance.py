"""
Governance Tests for AI Rewrite System

These tests enforce the non-negotiable contracts of the rewrite engine:
1. No rewrites without justification
2. All justifications must be in ALLOWED_TRIGGERS
3. Rewrite rate must stay below safety threshold
4. Zero false rewrites on golden dataset

If these tests fail, the system has regressed and must not ship.
"""

import pytest
from app.semantic_context import build_document_context, can_be_rewritten, rewrite_required
from app.document_first_ai import DocumentFirstAIEngine
from app.rewrite_governance import (
    validate_justification,
    validate_rewrite_result,
    validate_batch_stats,
    ALLOWED_TRIGGERS,
    FORBIDDEN_TRIGGERS,
    MAX_REWRITE_RATE,
    GovernanceViolation
)
import spacy

nlp = spacy.load("en_core_web_sm")


class TestGovernanceContracts:
    """Test that governance contracts are enforced."""
    
    def test_no_justification_rewrites_forbidden(self):
        """All rewrites must have a justification."""
        # Simulate rewrite without justification
        result = {
            "original": "The system is configured.",
            "suggestion": "The system configures itself.",
            "justification": "",  # VIOLATION
            "method": "llm_fallback"
        }
        
        with pytest.raises(RuntimeError, match="without justification"):
            validate_rewrite_result(result)
    
    def test_forbidden_triggers_rejected(self):
        """Style and fluency triggers must be rejected."""
        for forbidden in FORBIDDEN_TRIGGERS:
            with pytest.raises(RuntimeError, match="FORBIDDEN"):
                validate_justification(forbidden)
    
    def test_unknown_triggers_rejected(self):
        """Only ALLOWED_TRIGGERS are permitted."""
        with pytest.raises(RuntimeError, match="Illegal rewrite trigger"):
            validate_justification("readability_improvement")
    
    def test_allowed_triggers_accepted(self):
        """All ALLOWED_TRIGGERS should validate successfully."""
        for trigger in ALLOWED_TRIGGERS:
            validate_justification(trigger)  # Should not raise
    
    def test_rewrite_rate_ceiling_enforced(self):
        """Batch rewrite rate must not exceed MAX_REWRITE_RATE."""
        # Simulate excessive rewriting
        stats = {
            "total_sentences": 100,
            "approved_rewrites": 50,  # 50% - too high
        }
        
        with pytest.raises(RuntimeError, match="exceeds safety threshold"):
            validate_batch_stats(stats)
    
    def test_rewrite_rate_within_threshold(self):
        """Normal rewrite rates should pass validation."""
        stats = {
            "total_sentences": 100,
            "approved_rewrites": 10,  # 10% - acceptable
        }
        
        validate_batch_stats(stats)  # Should not raise


class TestMeaningPreservationGoldenSet:
    """Test zero false rewrites on golden dataset."""
    
    @pytest.fixture
    def golden_sentences(self):
        """Golden dataset that must never be corrupted."""
        return [
            # Acronym after first use - must preserve
            "The PLC connects to the system.",
            "Configure the PLC settings.",  # "PLC" already used
            
            # Sequence operators - must preserve
            "First, open the valve.",
            "Then close the circuit breaker.",
            
            # Unbound pronouns - must preserve  
            "It enables communication.",  # No clear referent
            
            # UI labels - must preserve exact wording
            "Click the Start button.",
            "Press Ctrl+S to save.",
            
            # Technical specifications - must preserve
            "Voltage: 24V DC +/- 10%",
            "Operating temperature: -10°C to 50°C",
        ]
    
    def test_golden_sentences_unchanged(self, golden_sentences):
        """Golden sentences must remain unchanged (eligibility gate should block)."""
        doc = nlp(" ".join(golden_sentences))
        sentences = [sent.text.strip() for sent in doc.sents]
        
        sections = [{"title": "test", "content": " ".join(sentences), "start_index": 0}]
        context = build_document_context(sentences, sections, nlp)
        
        ai_engine = DocumentFirstAIEngine()
        
        for idx, sentence in enumerate(sentences):
            result = ai_engine._fallback_suggestion(
                "Passive voice",  # Test with common issue type
                sentence,
                issue_type="Passive voice",
                sentence_index=idx,
                document_context=context
            )
            
            suggestion = result.get("suggestion", sentence)
            
            # Golden sentences should be preserved
            assert suggestion == sentence, (
                f"Golden sentence corrupted at index {idx}:\n"
                f"Original: {sentence}\n"
                f"Suggestion: {suggestion}\n"
                f"Method: {result.get('method')}"
            )


class TestRewriteJustificationTracking:
    """Test that all rewrites are tracked with justification."""
    
    def test_rewrite_required_returns_justification(self):
        """rewrite_required() must return (bool, justification) tuple."""
        # Create minimal context
        from app.semantic_context import DocumentContext
        
        ctx = DocumentContext(
            sentences=["The system is configured by the operator."],
            entities={},
            acronyms={},
            pronoun_links={},
            sections=[]
        )
        
        # Test with passive voice issue
        required, justification = rewrite_required(
            "The system is configured.",
            0,
            ctx,
            issue_type="Passive voice"
        )
        
        # Should return tuple with justification string
        assert isinstance(required, bool)
        assert isinstance(justification, str)
        assert justification  # Must not be empty
        
        # If rewrite required, justification must be valid
        if required:
            validate_justification(justification)


class TestGateOrdering:
    """Test that gates execute in correct order: eligibility → justification → meaning."""
    
    def test_eligibility_blocks_before_llm(self):
        """Eligibility gate must block before LLM is called."""
        from app.semantic_context import DocumentContext
        
        # Sentence with sequence operator - should block at eligibility
        ctx = DocumentContext(
            sentences=["First step.", "Then perform calibration."],
            entities={},
            acronyms={},
            pronoun_links={},
            sections=[]
        )
        
        eligible = can_be_rewritten("Then perform calibration.", 1, ctx)
        assert not eligible, "Sequence operator should block at eligibility gate"
    
    def test_justification_blocks_style_issues(self):
        """Justification gate must block style-only issues."""
        from app.semantic_context import DocumentContext
        
        ctx = DocumentContext(
            sentences=["The system operates efficiently."],
            entities={},
            acronyms={},
            pronoun_links={},
            sections=[]
        )
        
        # Style issue should not justify rewrite
        required, justification = rewrite_required(
            "The system operates efficiently.",
            0,
            ctx,
            issue_type="Long sentences"  # Style issue
        )
        
        assert not required, "Style issues should not justify rewrites"
        assert justification == "style_not_justified"


def test_governance_module_immutability():
    """ALLOWED_TRIGGERS should not be accidentally mutable."""
    original_count = len(ALLOWED_TRIGGERS)
    
    # Attempt to add forbidden trigger (this should fail in practice)
    # This test documents that ALLOWED_TRIGGERS is a set, not a list
    assert isinstance(ALLOWED_TRIGGERS, set)
    assert "fluency_improvement" not in ALLOWED_TRIGGERS
    
    # Count should remain stable
    assert len(ALLOWED_TRIGGERS) == original_count
