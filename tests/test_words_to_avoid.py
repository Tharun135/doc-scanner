import pytest
from app.rules.words_to_avoid import check

def test_words_to_avoid():
    # Test a few banned words
    sentence = "Therefore, you should simply click the button."
    suggestions = check(sentence)
    
    assert len(suggestions) == 3
    
    # Map out the found rules
    found_words = [s['message'].split("'")[1].lower() for s in suggestions]
    assert "therefore" in found_words
    assert "should" in found_words
    assert "simply" in found_words
    
    # Test boundary conditions for "e.g."
    sentence2 = "This is an example, e.g. for testing."
    suggestions2 = check(sentence2)
    assert len(suggestions2) == 1
    assert "e.g." in suggestions2[0]['message'].lower()

def test_no_false_positives():
    # "justice" contains "just", shouldn't trigger
    # "mastery" contains "master"
    sentence = "His mastery of justice is impressive."
    suggestions = check(sentence)
    assert len(suggestions) == 0
