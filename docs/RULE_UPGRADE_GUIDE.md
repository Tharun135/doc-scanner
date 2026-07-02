# Rule Upgrade Guide: From Detectors to Decision-Makers

## The Pattern

Every rule must evolve from:
```python
# OLD: Detector (just flags issues)
return [{
    'message': 'Issue detected - consider fixing',
    'text': sentence,
    'start': 0,
    'end': len(sentence)
}]
```

To:
```python
# NEW: Decision-maker (analyzes, decides, explains)
return [{
    'message': 'Issue detected',
    'text': sentence,
    'start': 0,
    'end': len(sentence),
    'decision_type': 'rewrite',  # or 'explain', 'guide', 'no_change'
    'reviewer_rationale': 'Why this decision was made',
    'rule': 'rule_name',
    'ai_suggestion': get_ai_suggestion() if decision_type == 'rewrite' else None
}]
```

## Decision Type Framework

| Type | When to Use | Must Include | Example |
|------|-------------|--------------|---------|
| **rewrite** | Safe, deterministic improvement | AI suggestion | Passive with actor → active |
| **explain** | Complex, needs context | Semantic explanation | Long conditional sentence |
| **guide** | Structural issue | Actionable guidance | Wall of text, unclear goal |
| **no_change** | Intentional choice | Rationale for preservation | Historical context, intentional passive |

## Step-by-Step Upgrade Process

### Phase 1: Add Decision Framework to Each Rule

For each rule file in `app/rules/`:

1. **Import decision helper** (we'll create this)
2. **Analyze context** before returning
3. **Set decision_type** based on context
4. **Provide rationale** for decisions
5. **Call AI for rewrites** only

### Phase 2: Upgrade Priority Order

Start with these (clearest logic, most impact):

1. ✅ **passive_voice.py** - Clear actor detection logic
2. ✅ **simple_present_normalization.py** - Clear historical context logic
3. ✅ **style_rules.py** (adverbs) - Subjective term handling
4. ✅ **long_sentence.py** - Split vs. explain logic
5. ⏸️ Other rules as needed

---

## Concrete Examples

### Example 1: Passive Voice Rule Upgrade

**File:** `app/rules/passive_voice.py`

**Before:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    doc = nlp(sentence)
    issues = []
    
    for token in doc:
        if token.dep_ == "nsubjpass":
            issues.append({
                "text": sentence,
                "start": 0,
                "end": len(sentence),
                "message": "Avoid passive voice - consider using active voice"
            })
            break
    
    return issues
```

**After:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    doc = nlp(sentence)
    issues = []
    
    for token in doc:
        if token.dep_ == "nsubjpass":
            # CONTEXT ANALYSIS
            has_actor = " by " in sentence.lower()
            
            if has_actor:
                # DECISION: Rewrite (actor known)
                issues.append({
                    "text": sentence,
                    "start": 0,
                    "end": len(sentence),
                    "message": "Passive voice with known actor detected",
                    "decision_type": "rewrite",
                    "rule": "passive_voice",
                    "reviewer_rationale": "Actor is known - active voice provides clearer, more direct communication",
                    "ai_suggestion": None  # Will be filled by enrichment service
                })
            else:
                # DECISION: No change (actor intentionally omitted)
                issues.append({
                    "text": sentence,
                    "start": 0,
                    "end": len(sentence),
                    "message": "Passive voice detected",
                    "decision_type": "no_change",
                    "rule": "passive_voice",
                    "reviewer_rationale": "Actor intentionally omitted - passive voice appropriate for system state descriptions or when the actor is unknown/irrelevant"
                })
            break
    
    return issues
```

**Tests that will pass:** 5.1, 5.2

---

### Example 2: Simple Present Normalization Upgrade

**File:** `app/rules/simple_present_normalization.py`

**Before:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    # Detect non-simple present
    if has_future_tense(sentence) or has_past_tense(sentence):
        return [{
            'message': 'Non-simple present tense detected - consider converting to present tense',
            'text': sentence,
            'start': 0,
            'end': len(sentence)
        }]
    return []
```

**After:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    # Detect non-simple present
    if has_future_tense(sentence):
        # DECISION: Rewrite (future → present for consistency)
        return [{
            'message': 'Future tense detected',
            'text': sentence,
            'start': 0,
            'end': len(sentence),
            'decision_type': 'rewrite',
            'rule': 'simple_present_tense',
            'reviewer_rationale': 'Technical documentation uses simple present for consistency and clarity',
            'ai_suggestion': None  # Will be filled
        }]
    
    elif has_past_tense(sentence):
        # CONTEXT ANALYSIS: Check for historical markers
        historical_markers = ['in version', 'previously', 'originally', 'was redesigned', 'was introduced']
        is_historical = any(marker in sentence.lower() for marker in historical_markers)
        
        if is_historical:
            # DECISION: No change (historical context must be preserved)
            return [{
                'message': 'Past tense detected in historical context',
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'no_change',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'Historical context preserved - past tense appropriate when describing previous versions or design decisions'
            }]
        else:
            # DECISION: Rewrite (convert to present)
            return [{
                'message': 'Past tense detected',
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'rewrite',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'Convert to simple present for consistency with documentation standards',
                'ai_suggestion': None
            }]
    
    return []
```

**Tests that will pass:** 3.1, 3.2

---

### Example 3: Style Rules (Adverbs) Upgrade

**File:** `app/rules/style_rules.py`

**Before:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    adverbs = find_adverbs(sentence)
    issues = []
    
    for adverb in adverbs:
        issues.append({
            'message': f"Consider removing or replacing the adverb '{adverb}'",
            'text': sentence,
            'start': 0,
            'end': len(sentence)
        })
    
    return issues
```

**After:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    adverbs = find_adverbs(sentence)
    issues = []
    
    # Subjective/technical adverbs that may be intentional
    subjective_adverbs = ['properly', 'correctly', 'appropriately', 'specifically', 'exactly']
    
    for adverb in adverbs:
        if adverb.lower() in subjective_adverbs:
            # DECISION: No change (subjective/technical term)
            issues.append({
                'message': f"Adverb '{adverb}' detected",
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'no_change',
                'rule': 'style_adverbs',
                'reviewer_rationale': f"'{adverb}' may be intentional and domain-specific. In technical contexts, terms like 'properly configured' or 'correctly installed' convey specific technical meaning. Consider if removal would reduce clarity."
            })
        else:
            # DECISION: Guide (suggest consideration)
            issues.append({
                'message': f"Adverb '{adverb}' detected",
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'guide',
                'rule': 'style_adverbs',
                'reviewer_rationale': f"Consider if '{adverb}' adds value. Adverbs like '{adverb}' can often be removed or replaced with more specific verbs for stronger, more direct writing."
            })
    
    return issues
```

**Tests that will pass:** 6.1

---

### Example 4: Long Sentence Upgrade

**File:** `app/rules/long_sentence.py`

**Before:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    word_count = len(sentence.split())
    
    if word_count > 25:
        return [{
            'message': 'Consider breaking this long sentence into shorter ones',
            'text': sentence,
            'start': 0,
            'end': len(sentence)
        }]
    
    return []
```

**After:**
```python
def check(sentence, previous_sentence=None, next_sentence=None):
    word_count = len(sentence.split())
    
    if word_count > 25:
        # CONTEXT ANALYSIS: Check if it's a complex compliance/conditional sentence
        compliance_markers = ['must', 'shall', 'required', 'if', 'or', 'unless', 'provided that']
        is_compliance = sum(1 for marker in compliance_markers if marker in sentence.lower()) >= 3
        
        if is_compliance:
            # DECISION: Explain (complex requirement, don't split)
            return [{
                'message': 'Long conditional/compliance sentence detected',
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'explain',
                'rule': 'long_sentence',
                'reviewer_rationale': 'This sentence defines a complex requirement with multiple conditions. Splitting it could separate logically connected requirements and reduce clarity. The length is justified by the semantic complexity.',
                'explanation': 'Compliance and conditional sentences often need multiple clauses to express requirements accurately. Consider if the conditions are truly inseparable before splitting.'
            }]
        else:
            # DECISION: Rewrite (simple long sentence, can be split)
            return [{
                'message': 'Long sentence detected',
                'text': sentence,
                'start': 0,
                'end': len(sentence),
                'decision_type': 'rewrite',
                'rule': 'long_sentence',
                'reviewer_rationale': 'Long sentences reduce readability. Breaking into 2-3 focused sentences improves clarity.',
                'ai_suggestion': None  # Will be filled
            }]
    
    return []
```

**Tests that will pass:** 4.1, 4.2

---

## Implementation Checklist

For each rule:

- [ ] Add `decision_type` field
- [ ] Add `reviewer_rationale` field
- [ ] Add `rule` field (rule name)
- [ ] Add context analysis logic
- [ ] Implement decision branching:
  - [ ] `rewrite`: Safe changes
  - [ ] `explain`: Complex cases
  - [ ] `guide`: Structural issues
  - [ ] `no_change`: Intentional choices
- [ ] For `rewrite` decisions: prepare for AI integration
- [ ] Run `python test_diagnostic.py` to verify
- [ ] Run `python test_reviewer_behavior.py` to see tests pass

## AI Integration (Optional Enhancement)

When decision_type is `rewrite`, the enrichment service will automatically call the AI suggestion engine. The rule just needs to:

1. Set `decision_type: 'rewrite'`
2. Set `ai_suggestion: None` (placeholder)
3. The enrichment service fills it in

No need to call AI directly from rules.

---

## Quick Start: Upgrade One Rule Now

**Pick one:**
```powershell
# 1. Open the rule file
code app/rules/passive_voice.py

# 2. Add context analysis and decision logic (see examples above)

# 3. Test it
python test_diagnostic.py

# 4. Check which tests pass
python test_reviewer_behavior.py
```

**Success = specific tests turn green**

---

## Summary

**Old way (Detector):**
- Finds problem ✓
- Says "consider fixing" ✗
- No context ✗
- No decision ✗
- No concrete help ✗

**New way (Decision-maker):**
- Finds problem ✓
- Analyzes context ✓
- Makes explicit decision ✓
- Explains reasoning ✓
- Provides concrete help (if appropriate) ✓

This transforms your app from a **linter** to a **reviewer**.
