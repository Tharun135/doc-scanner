"""
Regression tests for Simple Present Tense Normalization

These tests ensure that the tense detection and sentence classification
logic correctly identifies which sentences can be safely converted to
simple present tense.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.simple_present_normalization import (
    detect_verb_tense,
    classify_sentence_for_tense,
    can_convert_to_simple_present,
    validate_simple_present_rewrite,
    is_non_sentential,
    is_metadiscourse
)


# =============================================================================
# NON-SENTENTIAL TEXT DETECTION TESTS
# =============================================================================

def test_detect_title_gerund_phrase():
    """Test detection of gerund phrases used as titles."""
    assert is_non_sentential("Configuring KEPware server with certificates") is True
    assert is_non_sentential("Installing the client") is True
    assert is_non_sentential("Setting up the database") is True


def test_detect_short_title():
    """Test detection of short titles and fragments."""
    assert is_non_sentential("Prerequisites") is True
    assert is_non_sentential("Server configuration") is True
    assert is_non_sentential("Getting Started") is True


def test_detect_noun_phrase_title():
    """Test detection of noun phrase titles."""
    assert is_non_sentential("Certificate requirements") is True
    assert is_non_sentential("Database connection settings") is True


def test_allow_complete_sentences():
    """Test that complete sentences are NOT flagged as non-sentential."""
    assert is_non_sentential("The system validates the input.") is False
    assert is_non_sentential("Configure the server before starting.") is False
    assert is_non_sentential("The application processes requests.") is False


# =============================================================================
# METADISCOURSE DETECTION TESTS
# =============================================================================

def test_detect_metadiscourse_example_introducers():
    """Test detection of sentences that introduce examples."""
    assert is_metadiscourse("Here's an example of a properly configured certificate:") is True
    assert is_metadiscourse("Here is an example of the output:") is True
    assert is_metadiscourse("Below is a sample configuration:") is True
    assert is_metadiscourse("The following shows the correct format:") is True


def test_detect_metadiscourse_figure_references():
    """Test detection of sentences that reference figures/tables."""
    assert is_metadiscourse("The figure shows the architecture:") is True
    assert is_metadiscourse("Figure 1 shows the workflow.") is True
    assert is_metadiscourse("The table shows the supported values:") is True


def test_detect_metadiscourse_section_introducers():
    """Test detection of section introduction sentences."""
    assert is_metadiscourse("This section describes the installation process.") is True
    assert is_metadiscourse("This chapter covers advanced configuration.") is True
    assert is_metadiscourse("This guide explains the setup procedure.") is True


def test_allow_non_metadiscourse_sentences():
    """Test that regular content sentences are NOT flagged as metadiscourse."""
    assert is_metadiscourse("The system validates the input.") is False
    assert is_metadiscourse("Configure the server before starting.") is False
    assert is_metadiscourse("The certificate must be valid.") is False
    assert is_metadiscourse("Click OK to save the settings.") is False


# =============================================================================
# TENSE DETECTION TESTS
# =============================================================================

def test_detect_past_tense():
    """Test detection of past tense verbs."""
    assert detect_verb_tense("The system was configured.") == "past"
    assert detect_verb_tense("The client was initially untrusted.") == "past"
    assert detect_verb_tense("The module worked correctly.") == "past"


def test_detect_future_tense():
    """Test detection of future tense markers."""
    assert detect_verb_tense("The system will validate the input.") == "future"
    assert detect_verb_tense("The server shall process requests.") == "future"
    assert detect_verb_tense("The application is going to start.") == "future"


def test_detect_present_tense():
    """Test detection of present tense verbs."""
    assert detect_verb_tense("The server processes incoming requests.") == "present"
    assert detect_verb_tense("The system validates input.") == "present"
    assert detect_verb_tense("The application runs on port 5000.") == "present"


def test_detect_mixed_tense():
    """Test detection of sentences with mixed tenses."""
    s = "The system was configured but now works correctly."
    result = detect_verb_tense(s)
    assert result in ["mixed", "past", "present"]  # Acceptable variations


# =============================================================================
# SENTENCE CLASSIFICATION TESTS
# =============================================================================

def test_classify_instructional():
    """Test classification of instructional sentences."""
    assert classify_sentence_for_tense("Click the Save button.") == "instructional"
    assert classify_sentence_for_tense("Configure the server settings.") == "instructional"
    assert classify_sentence_for_tense("Run the installation script.") == "instructional"


def test_classify_descriptive():
    """Test classification of descriptive system behavior."""
    assert classify_sentence_for_tense("The server processes incoming requests.") == "descriptive"
    assert classify_sentence_for_tense("The application validates user input.") == "descriptive"


def test_classify_explanatory():
    """Test classification of explanatory examples."""
    assert classify_sentence_for_tense("For example, the client was initially untrusted.") == "explanatory"
    assert classify_sentence_for_tense("For instance, the server returned an error.") == "explanatory"
    assert classify_sentence_for_tense("In this setup, the configuration was invalid.") == "explanatory"
    assert classify_sentence_for_tense("In this case, the connection failed.") == "explanatory"


def test_classify_historical():
    """Test classification of historical/temporal text."""
    assert classify_sentence_for_tense("In version 3.0, the module was redesigned.") == "historical"
    assert classify_sentence_for_tense("Previously, the system used a different algorithm.") == "historical"
    assert classify_sentence_for_tense("The feature was introduced in version 2.1.") == "historical"
    assert classify_sentence_for_tense("Earlier, the system was less efficient.") == "historical"


def test_classify_compliance_conditional():
    """Test classification of compliance statements with conditions."""
    assert classify_sentence_for_tense("The certificate must be generated after installation.") == "compliance_conditional"
    assert classify_sentence_for_tense("The system shall validate input if the user is authenticated.") == "compliance_conditional"
    assert classify_sentence_for_tense("Configuration is required before the server starts.") == "compliance_conditional"


# =============================================================================
# ELIGIBILITY TESTS (THE GATEKEEPER)
# =============================================================================

def test_instructional_future_eligible():
    """Instructional sentences with future tense should be eligible."""
    s = "The system will validate the input."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is True
    assert reason == "descriptive"


def test_explanatory_past_eligible():
    """Explanatory sentences with past tense should be eligible."""
    s = "For example, the client was initially untrusted."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is True
    assert reason == "explanatory"


def test_descriptive_past_eligible():
    """Descriptive sentences with past tense should be eligible."""
    s = "The application was processing the request."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is True


def test_historical_blocked():
    """Historical sentences should NEVER be eligible."""
    s = "In version 3.0, the module was redesigned."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "historical"


def test_compliance_conditional_blocked():
    """Compliance statements with conditions should NEVER be eligible."""
    s = "The certificate must be generated after installation."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "compliance_conditional"


def test_already_present_skipped():
    """Sentences already in present tense should be skipped."""
    s = "The server processes incoming requests."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "already_present"


# =============================================================================
# VALIDATION TESTS (STRICT SAFETY CHECKS)
# =============================================================================

def test_validate_successful_conversion():
    """Test validation of a successful tense conversion."""
    original = "The system will validate the input."
    rewritten = "The system validates the input."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is True
    assert reason == "ok"


def test_validate_explanatory_conversion():
    """Test validation of explanatory sentence conversion."""
    original = "For example, the client was initially untrusted."
    rewritten = "For example, the client is initially untrusted."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is True


def test_validate_reject_empty():
    """Validator should reject empty output."""
    original = "The system will validate the input."
    rewritten = ""
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is False
    assert reason == "empty_output"


def test_validate_reject_no_change():
    """Validator should reject output identical to input."""
    original = "The system validates the input."
    rewritten = "The system validates the input."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is False
    assert reason == "no_change"


def test_validate_reject_not_present_tense():
    """Validator should reject output not in present tense."""
    original = "The system will validate the input."
    rewritten = "The system validated the input."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is False
    assert reason == "not_simple_present"


def test_validate_reject_obligation_removed():
    """Validator should reject when obligation terms are removed or passive construction used."""
    original = "The certificate must be generated."
    rewritten = "The certificate is generated."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is False
    # Could fail on either check - both are correct rejections
    assert reason in ["obligation_changed", "not_simple_present"]


def test_validate_reject_meaning_drift():
    """Validator should reject when semantic similarity is too low."""
    original = "The system will validate the input."
    rewritten = "The application performs security checks on data."
    valid, reason = validate_simple_present_rewrite(original, rewritten)
    assert valid is False
    assert reason in ["meaning_drift", "new_content_introduced"]


# =============================================================================
# END-TO-END REALISTIC TEST CASES
# =============================================================================

def test_realistic_case_1_simple_future():
    """Test realistic conversion of simple future to present."""
    s = "The server will process the request."
    allowed, _ = can_convert_to_simple_present(s)
    assert allowed is True
    
    # Simulate conversion
    converted = "The server processes the request."
    valid, _ = validate_simple_present_rewrite(s, converted)
    assert valid is True


def test_realistic_case_2_explanatory_past():
    """Test realistic conversion of explanatory past tense."""
    s = "For example, in this setup, the client was initially untrusted. Only after manually trusting it did the communication work."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is True
    assert reason == "explanatory"


def test_realistic_case_3_historical_block():
    """Test that historical context blocks conversion."""
    s = "In version 2.1, the authentication module was completely rewritten."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "historical"


def test_realistic_case_4_compliance_block():
    """Test that compliance with conditions blocks conversion."""
    s = "The SSL certificate must be installed before the server starts."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "compliance_conditional"


def test_realistic_case_5_already_present():
    """Test that present tense is recognized and skipped."""
    s = "The application validates user credentials against the database."
    allowed, reason = can_convert_to_simple_present(s)
    assert allowed is False
    assert reason == "already_present"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
