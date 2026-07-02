# Test Suite Diagnostic Report

## Executive Summary

**Status:** Tests are working correctly. Failures reveal architectural gaps in rules.

## What the Tests Revealed

### ✓ Working
- Rules fire for tense, passive voice, adverbs
- Test framework correctly identifies missing behaviors
- Document gate blocks properly

### ✗ Missing (Critical)
1. **No decision_type field** - Rules don't set rewrite/explain/guide/no_change
2. **No reviewer_rationale** - Rules don't explain decisions
3. **No context awareness** - Rules treat all passives/tenses the same
4. **No AI rewrites** - Rules only give generic advice, no concrete fixes

## Current Rule Output vs. Expected

### Example: Passive Voice Rule

**Current Output:**
```python
{
    'message': 'Avoid passive voice - consider using active voice',
    'rule': 'unknown',
    'decision_type': NOT SET,
    'reviewer_rationale': NOT SET,
    'ai_suggestion': None
}
```

**Expected Output:**
```python
{
    'message': 'Passive voice detected',
    'rule': 'passive_voice',
    'decision_type': 'rewrite',  # OR 'no_change' if intentional
    'reviewer_rationale': 'Actor is known - active voice clearer',  # OR 'Actor intentionally omitted'
    'ai_suggestion': {
        'suggestion': 'The system created the file.',
        'confidence': 'high'
    }
}
```

## What Needs Implementation

### 1. Decision Type System (High Priority)

Each rule must classify its findings:
- **rewrite**: Safe, deterministic improvement → AI provides concrete fix
- **explain**: Complex case → Semantic explanation, no rewrite
- **guide**: Structural issue → Reviewer guidance
- **no_change**: Intentional choice → Rationale for preservation

### 2. Context-Aware Logic (High Priority)

Rules must consider:
- **Historical context**: "In version 3.0, was redesigned" → no_change + rationale
- **Intentional passive**: "Access is restricted" → no_change + rationale
- **Subjective style**: "properly configured" → no_change + rationale
- **Compliance language**: "must include... or... if..." → explain, not split

### 3. AI Integration (Medium Priority)

For `decision_type: rewrite`, rules must:
- Call AI suggestion engine
- Validate rewrite preserves meaning
- Provide concrete replacement text

### 4. Reviewer Rationale (High Priority)

Every non-rewrite decision must answer:
> "Why didn't the system change this?"

## Test-Driven Development Approach

### Phase 1: Add Decision Types to Existing Rules
1. Update `passive_voice.py` to set decision_type based on actor presence
2. Update `simple_present_normalization.py` to check for historical context
3. Update `style_rules.py` to provide rationale for subjective terms

### Phase 2: Add Context Detection
1. Historical markers: "In version", "Previously", "Originally"
2. Intentional passive: No "by [actor]" present
3. Compliance language: "must... or... if..."

### Phase 3: Integrate AI Rewrites
1. Connect rules to AI suggestion engine
2. Only for decision_type: rewrite
3. Validate outputs

## Running Tests Iteratively

```powershell
# 1. Run diagnostic to see current state
python test_diagnostic.py

# 2. Fix one rule (e.g., passive_voice.py)
# Add decision_type logic

# 3. Run tests again
python test_reviewer_behavior.py

# 4. Watch specific tests turn green
# e.g., Test 5.1 and 5.2 should pass after fixing passive_voice
```

## Success Criteria

When tests pass, it means:
- ✓ Rules make explicit editorial decisions
- ✓ Context-aware logic prevents false positives
- ✓ AI rewrites only when safe and appropriate
- ✓ Rationale explains every non-rewrite decision

## Current Scorecard

| Rule | Fires? | decision_type? | rationale? | AI rewrite? |
|------|--------|----------------|------------|-------------|
| passive_voice | ✓ | ✗ | ✗ | ✗ |
| simple_present_normalization | ✓ | ✗ | ✗ | ✗ |
| style_rules (adverbs) | ✓ | ✗ | ✗ | ✗ |
| long_sentence | ✗ | ✗ | ✗ | ✗ |

## Next Steps

1. **Read this report** - Understand gap between current vs. expected
2. **Pick one rule** - Start with passive_voice (clearest logic)
3. **Add decision logic** - Implement context-aware decision_type
4. **Run tests** - Watch specific tests turn green
5. **Repeat** - One rule at a time

---

**Remember:** These test failures are not bugs. They're **architectural requirements** that weren't yet implemented. The tests are doing their job - showing you exactly what needs to be built.
