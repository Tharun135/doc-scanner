import pytest
from app.rules.tone_voice import check

def test_tone_voice():
    # SG-TV-001
    s1 = "You can't do that."
    res1 = check(s1)
    assert any(r['rule_id'] == 'SG-TV-001' for r in res1)

    # SG-TV-002
    s2 = "We'll see about that."
    res2 = check(s2)
    assert any(r['rule_id'] == 'SG-TV-002' for r in res2)

    # SG-TV-003
    s3 = "Every salesman knows his territory."
    res3 = check(s3)
    rule_ids3 = [r['rule_id'] for r in res3]
    # "salesman" and "his"
    assert rule_ids3.count('SG-TV-003') == 2

    # SG-TV-004
    s4 = "Simply click the button."
    res4 = check(s4)
    assert any(r['rule_id'] == 'SG-TV-004' for r in res4)

    # SG-TV-005
    s5 = "One should always be careful."
    res5 = check(s5)
    assert any(r['rule_id'] == 'SG-TV-005' for r in res5)

def test_no_false_positives():
    s = "You cannot do that. We will see about that. Every salesperson knows their territory. Click the button. You should always be careful."
    res = check(s)
    assert len(res) == 0
