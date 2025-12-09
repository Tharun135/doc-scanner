# Rewrite Governance Checklist

## Purpose
This checklist must be followed for ANY changes to the AI rewrite system. The rewrite engine is safety-governed and operates under strict contracts.

## Pre-Merge Requirements

Before merging ANY pull request that touches these files:
- `app/semantic_context.py`
- `app/document_first_ai.py`
- `app/intelligent_ai_improvement.py`
- `app/rewrite_governance.py`
- `tests/test_rewrite_governance.py`
- `tests/test_meaning_preservation.py`

Complete this checklist:

### ✅ 1. Governance Tests Pass
```bash
pytest tests/test_rewrite_governance.py -v
```
All tests must pass. No exceptions.

### ✅ 2. Rewrite Rate Within Threshold
Run batch validation:
```bash
python batch_context_preservation_test.py
```

**Required:**
- Rewrite rate ≤ 30%
- False rewrites = 0
- All rewrites have justification in `ALLOWED_TRIGGERS`

### ✅ 3. No New Triggers Without Review
Check if `ALLOWED_TRIGGERS` was modified:
```bash
git diff app/rewrite_governance.py | grep ALLOWED_TRIGGERS
```

**If modified:**
- [ ] New trigger documented with necessity criteria
- [ ] Test coverage added for new trigger
- [ ] Explicit governance review approval obtained
- [ ] Validation that trigger does NOT enable style/fluency rewrites

### ✅ 4. Golden Set Unchanged
Run golden dataset test:
```bash
pytest tests/test_rewrite_governance.py::TestMeaningPreservationGoldenSet -v
```

All golden sentences must remain unchanged.

### ✅ 5. No Direct LLM Bypasses
Search for direct LLM calls:
```bash
grep -r "ollama" app/ | grep -v "_fallback_suggestion"
```

All LLM calls must go through gated entry points, not direct API calls.

### ✅ 6. Justification Histogram Valid
Check that all rewrites map to `ALLOWED_TRIGGERS`:
```bash
python batch_context_preservation_test.py 2>&1 | grep "Triggers:"
```

**(no_justification): 0** is mandatory.

### ✅ 7. No Config-Driven Gates
Verify that gates are NOT made configurable:
```bash
grep -r "rewrite_aggressiveness\|gate_threshold\|style_level" config/ app/
```

Should return no matches. Gates belong in code, not config files.

---

## What is NOT Permitted

❌ **Style improvements** - readability, fluency, elegance, tone  
❌ **Rewrite rate increases** - without demonstrated necessity  
❌ **New triggers** - without explicit governance review  
❌ **Gate loosening** - eligibility or justification criteria  
❌ **Config-driven gates** - no toggles for safety rules  
❌ **Direct LLM calls** - must go through governed entry points  

---

## The Core Contract

**The rewrite engine may only:**
1. Resolve ambiguity (passive referent, pronoun, sequence)
2. Fix objective grammar errors (tense)
3. Address vague quantifiers (some, various, many)

**The rewrite engine must never:**
1. Perform style-only or fluency-only changes
2. Rewrite without documented justification
3. Exceed 30% rewrite rate on typical documentation
4. Alter meaning or technical accuracy

---

## Emergency Rollback Criteria

If deployed code exhibits:
- Rewrite rate > 30% on production docs
- Any rewrites with justification not in `ALLOWED_TRIGGERS`
- False rewrites reported by users
- Meaning corruption detected

**→ Immediate rollback required. No debate.**

---

## Review Signoff

Before merging, the following must approve:

- [ ] Code owner review completed
- [ ] All checklist items verified
- [ ] Governance tests passing
- [ ] No regression in golden dataset
- [ ] Justification histogram validated

**Reviewer signature:** _________________________  
**Date:** _________________________

---

## Philosophy

> "Clarity belongs to writers. Safety belongs to the engine."

The rewrite engine is not here to make docs elegant.  
Its job is to prevent damage.

We built a validator, not a stylist.  
That's what makes it production-safe.
