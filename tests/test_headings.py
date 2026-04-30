import pytest
from app.rules.headings import check

def test_headings():
    # SG-HE-001: not -ing form
    s1 = "Add a new element"
    res1 = check(s1, tag_name='h2')
    # Should have SG-HE-001
    rule_ids = [r['rule_id'] for r in res1]
    assert 'SG-HE-001' in rule_ids

    # SG-HE-002: title case
    s2 = "Go To Settings"
    res2 = check(s2, tag_name='h3')
    rule_ids2 = [r['rule_id'] for r in res2]
    assert 'SG-HE-002' in rule_ids2

    # SG-HE-003: length > 6
    s3 = "This is a very long heading that has more than six words"
    res3 = check(s3, tag_name='h1')
    rule_ids3 = [r['rule_id'] for r in res3]
    assert 'SG-HE-003' in rule_ids3

    # SG-HE-004: H4 or below
    s4 = "Minor section"
    res4 = check(s4, tag_name='h4')
    rule_ids4 = [r['rule_id'] for r in res4]
    assert 'SG-HE-004' in rule_ids4

def test_no_false_positives():
    # Valid heading
    s = "Adding a new element"
    res = check(s, tag_name='h2')
    assert len(res) == 0
    
    # Not a heading
    s2 = "Add a new element."
    res2 = check(s2, tag_name='p')
    assert len(res2) == 0
