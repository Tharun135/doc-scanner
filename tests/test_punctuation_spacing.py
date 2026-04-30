import pytest
from app.rules.punctuation_spacing import check

def test_punctuation_spacing():
    # SG-PS-001
    s1 = "We have 50 % efficiency."
    res1 = check(s1)
    assert len(res1) == 1
    assert res1[0]['rule_id'] == 'SG-PS-001'

    # SG-PS-002
    s2 = "The weight is 11kg and 5g."
    res2 = check(s2)
    assert len(res2) == 2
    assert res2[0]['rule_id'] == 'SG-PS-002'

    # SG-PS-003
    s3 = "Settings & config are here."
    res3 = check(s3)
    assert len(res3) == 1
    assert res3[0]['rule_id'] == 'SG-PS-003'

    # SG-PS-004
    s4 = "Do this; then do that."
    res4 = check(s4)
    assert len(res4) == 1
    assert res4[0]['rule_id'] == 'SG-PS-004'

    # SG-PS-005
    s5 = "Enter the value [optional]."
    res5 = check(s5)
    assert len(res5) == 2  # one for [, one for ]
    assert res5[0]['rule_id'] == 'SG-PS-005'

    # SG-PS-006
    s6 = "This is a list item without a period"
    res6 = check(s6, block_type='li')
    assert len(res6) == 1
    assert res6[0]['rule_id'] == 'SG-PS-006'

def test_no_false_positives():
    s = "We have 50% efficiency. The weight is 11 kg. Settings and config. Do this, then do that."
    res = check(s)
    assert len(res) == 0
