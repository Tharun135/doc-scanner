# Quick Reference: Deterministic Suggestion System

## Core Principle

```
┌──────────────────────────────────────────────────────────┐
│  NEVER ask the LLM to decide what to do.                 │
│  Force the decision in code.                             │
│  Use the LLM only to express it well.                    │
└──────────────────────────────────────────────────────────┘
```

## Usage

### Single Issue

```python
from core.deterministic_suggestions import generate_suggestion_for_issue

issue = {
    'feedback': 'Avoid passive voice',
    'context': 'The file was opened.',
    'rule_id': 'passive_voice',
    'document_type': 'manual',
}

suggestion = generate_suggestion_for_issue(issue)
# Returns actionable suggestion or None (if unmapped)
```

### Batch Processing

```python
from core.deterministic_suggestions import generate_suggestions_for_issues

issues = [...]  # List of issue dicts
suggestions = generate_suggestions_for_issues(issues)
# Returns only cleanly-mapped, actionable suggestions
```

## 10 Issue Types (Quick Lookup)

| Issue | Severity | LLM? | Fallback Works? |
|-------|----------|------|-----------------|
| Passive Voice | Advisory | Yes | ✅ |
| Long Sentence | Advisory | Yes | ✅ |
| Vague Term | Advisory | Yes | ✅ |
| Missing Prerequisite | **Blocking** | No | ✅ |
| Dense Step | Advisory | No | ✅ |
| Step Order Problem | **Blocking** | No | ✅ |
| Undefined Acronym | Advisory | No | ✅ |
| Inconsistent Terminology | Advisory | No | ✅ |
| Mixed Tense | Advisory | No | ✅ |
| Missing Introduction | Advisory | No | ✅ |

## Suggestion Object Structure

```python
{
    'issue_type': str,           # 'passive_voice', 'long_sentence', etc.
    'severity': str,             # 'blocking' or 'advisory'
    'resolution_class': str,     # 'rewrite_active', 'simplify_sentence', etc.
    'guidance': str,             # Actionable guidance (guaranteed)
    'rewrite': str | None,       # Rewritten sentence (if applicable)
    'action_required': str,      # Clear next step
    'method': str,               # 'deterministic', 'llm_phrased', 'rag_enhanced'
    'confidence': str,           # 'high' or 'medium'
}
```

## Classification Patterns

```python
# In your rule detection, include these fields:
{
    'feedback': str,     # Description of issue (used for classification)
    'context': str,      # Original sentence/content
    'rule_id': str,      # Rule identifier (helps classification)
    'document_type': str,  # 'manual', 'procedure', etc.
}
```

## Key Files

```
core/
  issue_resolution_engine.py     # Decision logic
  llm_phrasing.py                # LLM narrow role
  deterministic_suggestions.py   # Main entry point

test_deterministic_system.py     # Run this to test

Documentation:
  IMPLEMENTATION_COMPLETE.md     # Start here
  INTEGRATION_GUIDE.md           # How to integrate
  ISSUE_CLASSIFICATION_REFERENCE.md  # All 10 issues
  ARCHITECTURE_DIAGRAM.md        # Visual diagrams
```

## Adding New Issue Type

```python
# 1. Add to IssueType enum
class IssueType(Enum):
    NEW_ISSUE = "new_issue"

# 2. Add to ResolutionClass enum (if needed)
class ResolutionClass(Enum):
    NEW_RESOLUTION = "new_resolution"

# 3. Map issue to resolution
ISSUE_TO_RESOLUTION = {
    IssueType.NEW_ISSUE: ResolutionClass.NEW_RESOLUTION,
}

# 4. Add template
RESOLUTION_TEMPLATES = {
    ResolutionClass.NEW_RESOLUTION: ResolutionTemplate(
        resolution_class=ResolutionClass.NEW_RESOLUTION,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback="Clear guidance here...",
        action_required="Specific action",
        explanation_template="Template for LLM",
    ),
}

# 5. Add severity
ISSUE_SEVERITY = {
    IssueType.NEW_ISSUE: IssueSeverity.ADVISORY,
}

# 6. Update classification logic
def classify_issue(issue_data):
    if 'new_issue_pattern' in feedback:
        return IssueType.NEW_ISSUE
```

## Testing

```bash
# Run full test suite
python test_deterministic_system.py

# Expected output:
# ✓ All 10 issue types work
# ✓ Deterministic fallbacks function
# ✓ Unmapped issues filtered
# ✓ All suggestions actionable
```

## Failure Modes

| Component | Fails | Result |
|-----------|-------|--------|
| LLM | Timeout/Error | Use deterministic fallback ✅ |
| RAG | No results | Continue without it ✅ |
| Classification | Unmapped | Return None (don't show) ✅ |
| All AI | Both fail | Deterministic fallback works ✅ |

**Guarantee:** Always useful output or filtered out.

## Configuration

```python
from core.deterministic_suggestions import DeterministicSuggestionGenerator

# Default (all features)
generator = DeterministicSuggestionGenerator()

# Disable LLM (pure deterministic)
generator.llm_phraser.llm_available = False

# Disable RAG
generator.rag_available = False

# Still works! Fallbacks guarantee value.
```

## Quality Validation

Output rejected if:
- ❌ Too similar to original (>80% similarity)
- ❌ Lacks action words
- ❌ Only hedges without concrete step
- ❌ Too short (<20 characters)

→ Falls back to deterministic template

## Performance

| Mode | Time | Quality |
|------|------|---------|
| Deterministic only | <1ms | High |
| + LLM phrasing | <10s | Higher |
| + RAG enhancement | <13s | Highest |

All modes guarantee actionable output.

## Integration Checklist

- [ ] Run `python test_deterministic_system.py`
- [ ] Review templates in `issue_resolution_engine.py`
- [ ] Update `app/routes.py` to use new system
- [ ] Update UI to show blocking vs advisory
- [ ] Add severity indicators
- [ ] Deploy and monitor
- [ ] Track method usage (deterministic/LLM/RAG)
- [ ] Iterate on templates based on feedback

## Common Patterns

### Display Blocking Issues

```python
if suggestion['severity'] == 'blocking':
    show_error_banner(suggestion['guidance'])
    require_fix_before_continue()
```

### Display Advisory Suggestions

```python
if suggestion['severity'] == 'advisory':
    show_improvement_tip(suggestion['guidance'])
    show_action_button(suggestion['action_required'])
```

### Show Rewrite

```python
if suggestion['rewrite']:
    show_before_after(
        before=original_sentence,
        after=suggestion['rewrite']
    )
```

### Monitor Quality

```python
suggestions = generate_suggestions_for_issues(issues)

methods = {}
for s in suggestions:
    methods[s['method']] = methods.get(s['method'], 0) + 1

print(f"Deterministic: {methods.get('deterministic', 0)}")
print(f"LLM Phrased: {methods.get('llm_phrased', 0)}")
print(f"RAG Enhanced: {methods.get('rag_enhanced', 0)}")
```

## Troubleshooting

### "No suggestions generated"
→ Check if issues are being classified
→ Review patterns in `classify_issue()`

### "Suggestions are vague"
→ Check templates in `issue_resolution_engine.py`
→ Adjust `deterministic_fallback` text

### "LLM timeout"
→ System automatically falls back (no user impact)
→ Adjust timeout in `llm_phrasing.py` if needed

### "Want to add custom issue"
→ Follow "Adding New Issue Type" section above
→ Test with `test_deterministic_system.py`

## Philosophy

```
❌ Don't: "LLM, what should I do about this issue?"
✅ Do:    "This is REWRITE_ACTIVE. LLM, phrase this template."

❌ Don't: Depend on RAG for decisions
✅ Do:    Use RAG to enhance pre-made decisions

❌ Don't: Show unmapped issues
✅ Do:    Only show what you can handle well

❌ Don't: Trust LLM output blindly
✅ Do:    Validate, then fallback if insufficient
```

## Success Indicators

- ✅ Users know exactly what to do
- ✅ No "consider" or "might" without action
- ✅ Blocking issues clearly marked
- ✅ System works even when LLM/RAG fail
- ✅ Every suggestion is actionable

---

**Remember:** Make decisions in code. Use LLM only to phrase them.

This is how you build **review authority**.
