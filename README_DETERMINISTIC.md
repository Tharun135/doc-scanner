# Deterministic Suggestion System

## Executive Summary

This implementation shifts the document scanner from **asking LLMs to figure things out** to **making decisions in code and using LLMs only for phrasing**.

### The Core Problem (Before)

```
Issue Detected → Ask LLM "What should I do?" → Often vague/useless answer
```

- LLM tries to decide what's wrong AND how to fix it
- Weak ChromaDB retrieval hurts quality
- Conservative models (phi3:mini) hedge and avoid committing
- No guarantee of useful output

### The Solution (After)

```
Issue Detected → Classify deterministically → Resolution class
              → Get deterministic template + fallback
              → Try RAG enhancement (optional)
              → Try LLM phrasing (optional)
              → Validate quality
              → Return fallback if insufficient
              → Actionable guidance (GUARANTEED)
```

## What You Built

### 1. Deterministic Decision Engine

**File:** `core/issue_resolution_engine.py`

- Maps every issue to exactly one resolution class
- Provides deterministic fallback for each
- Filters unmapped issues (don't show to user)
- Validates output quality

**Key Principle:** Never ask the LLM to decide what to do.

### 2. Narrow LLM Phrasing Module  

**File:** `core/llm_phrasing.py`

- LLM adapts pre-written templates ONLY
- LLM does NOT decide what issue exists
- LLM does NOT decide how to fix it
- Automatic fallback on failure (10s timeout)

**Key Principle:** LLM is a translator, not a thinker.

### 3. Integrated Suggestion Generator

**File:** `core/deterministic_suggestions.py`

- Combines resolution engine + LLM + RAG
- RAG used as enhancer, not dependency
- Quality validation at every step
- Guaranteed actionable output

**Key Principle:** Always return useful guidance.

## The 10 Issues & Resolutions

| Issue | Resolution | LLM? | Severity |
|-------|-----------|------|----------|
| Passive Voice | Rewrite Active | Yes | Advisory |
| Long Sentence | Simplify | Yes | Advisory |
| Vague Term | Replace Specific | Yes | Advisory |
| Missing Prerequisite | Ask For Prerequisites | No | **Blocking** |
| Dense Step | Break Into Steps | No | Advisory |
| Step Order Problem | Reorder Guidance | No | **Blocking** |
| Undefined Acronym | Define Acronym | No | Advisory |
| Inconsistent Terminology | Standardize Term | No | Advisory |
| Mixed Tense | Unify Tense | No | Advisory |
| Missing Introduction | Add Introduction | No | Advisory |

**Only 3 of 10 issues need LLM** - and only for content adaptation, not decision-making.

## Quick Start

### Run Tests

```bash
python test_deterministic_system.py
```

Expected output:
- ✅ All 10 issue types work
- ✅ Deterministic fallbacks function
- ✅ Unmapped issues filtered
- ✅ All suggestions actionable

### Use in Code

```python
from core.deterministic_suggestions import generate_suggestion_for_issue

# Detect issue (existing rule system)
issue = {
    'feedback': 'Avoid passive voice',
    'context': 'The file was opened.',
    'rule_id': 'passive_voice',
    'document_type': 'manual',
}

# Generate deterministic suggestion
suggestion = generate_suggestion_for_issue(issue)

if suggestion:
    print(f"Issue: {suggestion['issue_type']}")
    print(f"Severity: {suggestion['severity']}")
    print(f"Guidance: {suggestion['guidance']}")
    print(f"Action: {suggestion['action_required']}")
    
    if suggestion['rewrite']:
        print(f"Rewrite: {suggestion['rewrite']}")
```

### Batch Processing

```python
from core.deterministic_suggestions import generate_suggestions_for_issues

# Process multiple issues
issues = [...]  # List of issue dicts
suggestions = generate_suggestions_for_issues(issues)

# Only cleanly-mapped issues are returned
# All suggestions are actionable
```

## Integration

See **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** for:

- Step-by-step integration into existing app
- Updating routes and UI
- Configuration options
- Adding custom issues
- Monitoring quality

## Key Benefits

### Reliability

- ✅ Works without LLM (deterministic fallbacks)
- ✅ Works without RAG (not a dependency)
- ✅ Works with weak ChromaDB (optional enhancement)
- ✅ Works with conservative models (narrow role)

### Quality

- ✅ Every suggestion is actionable
- ✅ No vague or useless output
- ✅ Clear next steps always provided
- ✅ Validated for value

### Maintainability

- ✅ Easy to add new issues (just mapping + template)
- ✅ Easy to update guidance (edit templates)
- ✅ Easy to test (deterministic logic)
- ✅ Clear separation of concerns

## Architecture Principles

### 1. Decisions in Code, Not Prompts

```python
# ❌ Bad: Let LLM decide
"Here's an issue with passive voice. What should I do?"

# ✅ Good: Decide in code
ISSUE_TO_RESOLUTION = {
    IssueType.PASSIVE_VOICE: ResolutionClass.REWRITE_ACTIVE
}
```

### 2. LLM Only Phrases, Never Decides

```python
# ❌ Bad: LLM creativity
"Suggest improvements for this sentence"

# ✅ Good: LLM adaptation
"Adapt this template to this sentence:
Template: {template}
Sentence: {sentence}
Be direct. No hedging."
```

### 3. RAG as Enhancer, Not Dependency

```python
# ❌ Bad: Depend on RAG
if not rag_result:
    return "Unable to help"

# ✅ Good: RAG enhances
rag_result = try_rag_enhancement()
return rag_result if good else deterministic_fallback
```

### 4. Filter Unmapped Issues

```python
# ❌ Bad: Show everything
return all_detected_issues

# ✅ Good: Only show cleanly-mapped
return [i for i in issues if classify(i) is not None]
```

### 5. Validate Output Quality

```python
# ❌ Bad: Trust LLM output
return llm_response

# ✅ Good: Validate or fallback
if is_value_added(llm_response):
    return llm_response
else:
    return deterministic_fallback
```

## Files Reference

### Core System
- `core/issue_resolution_engine.py` - Deterministic decision logic
- `core/llm_phrasing.py` - Narrow LLM role (phrasing only)
- `core/deterministic_suggestions.py` - Main integration point

### Documentation
- `DETERMINISTIC_SYSTEM_SUMMARY.md` - Implementation summary
- `ISSUE_CLASSIFICATION_REFERENCE.md` - All 10 issues documented
- `INTEGRATION_GUIDE.md` - How to integrate into app
- `README_DETERMINISTIC.md` - This file

### Testing
- `test_deterministic_system.py` - Comprehensive test suite

## Results

### Before Implementation

| Metric | Status |
|--------|--------|
| LLM decides what to do | ❌ Often fails |
| Weak ChromaDB impact | ❌ Hurts quality |
| Conservative model output | ❌ Vague hedging |
| Quality guarantee | ❌ None |
| User clarity | ❌ Confused |

### After Implementation

| Metric | Status |
|--------|--------|
| Code decides what to do | ✅ Always works |
| Weak ChromaDB impact | ✅ None (optional) |
| Conservative model output | ✅ Constrained role |
| Quality guarantee | ✅ Deterministic fallbacks |
| User clarity | ✅ Clear actions |

## Performance

- **Deterministic mode:** Instant (no AI calls)
- **LLM phrasing:** <10 seconds (with timeout)
- **RAG enhancement:** <3 seconds (short timeout)
- **Fallback guarantee:** Always returns useful output

## Monitoring

Track which methods are used:

```python
from core.deterministic_suggestions import generate_suggestions_for_issues

suggestions = generate_suggestions_for_issues(issues)

methods = {
    'deterministic': len([s for s in suggestions if s['method'] == 'deterministic']),
    'llm_phrased': len([s for s in suggestions if s['method'] == 'llm_phrased']),
    'rag_enhanced': len([s for s in suggestions if s['method'] == 'rag_enhanced']),
}

print(f"Deterministic: {methods['deterministic']}")
print(f"LLM Phrased: {methods['llm_phrased']}")
print(f"RAG Enhanced: {methods['rag_enhanced']}")
```

## Adding New Issues

To add a new issue type:

1. Add to `IssueType` enum
2. Add to `ResolutionClass` enum (if new type needed)
3. Add mapping to `ISSUE_TO_RESOLUTION`
4. Add template to `RESOLUTION_TEMPLATES`
5. Add severity to `ISSUE_SEVERITY`
6. Update classification logic in `classify_issue()`

See `INTEGRATION_GUIDE.md` for detailed example.

## Philosophy

> **If you rely on LLM creativity, RAG coverage, or prompt cleverness, you will never get consistent value.**
>
> **If you rely on deterministic classification, fixed resolution strategies, and LLM only for phrasing, you will.**

This is how you build **review authority**.

## Support

Issues? Check:

1. **Unmapped issues** - Are they being filtered correctly?
2. **Fallback usage** - Is deterministic mode working?
3. **LLM timeout** - Is LLM responding in <10 seconds?
4. **RAG enhancement** - Is ChromaDB accessible?

All components are designed to fail gracefully and fall back to deterministic guidance.

## Next Steps

1. ✅ Run test suite: `python test_deterministic_system.py`
2. ✅ Review templates in `issue_resolution_engine.py`
3. ✅ Follow `INTEGRATION_GUIDE.md` to integrate
4. ✅ Update UI to show blocking vs advisory
5. ✅ Monitor suggestion quality
6. ✅ Iterate on templates based on user feedback

---

**Built following the principle:** Never ask the LLM to decide. Force decisions in code. Use LLM only to express them well.
