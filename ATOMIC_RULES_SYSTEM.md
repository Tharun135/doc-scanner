# Atomic Rule Enforcement System

## Overview

The DocScanner application now includes an **atomic rule-based enforcement system** that provides deterministic, severity-based feedback for technical writing.

## Architecture

```
/app/rules
  ├── rules.json          # Atomic rule definitions (JSON)
  ├── loader.py           # Rule loading and caching
  ├── matcher.py          # Pattern matching and violation detection
  ├── atomic_rules.py     # Integration with existing rule system
  └── __init__.py         # Rule function registry
```

## Severity Levels

The system uses **three severity levels** based on your choice (C - Mixed):

| Severity | Color  | Behavior | Use Case |
|----------|--------|----------|----------|
| `error`  | 🔴 Red  | **Must fix** - blocks approval | Safety wording, future tense in procedures, UI-label violations, personal pronouns |
| `warn`   | 🟡 Yellow | **Suggestion only** - no block | Adverbs, phrasal verbs, Oxford comma, passive voice |
| `info`   | 🔵 Blue | **Visibility only** - informational | Translation hints, consistency tips, jargon |

## Rule Categories

### 1. **Tense Rules** (`error` / `warn`)
- **TENSE_001**: Future tense forbidden in procedures
  - ❌ "The system will start..."
  - ✅ "The system starts..."
- **TENSE_002**: Modal verbs weaken clarity
  - ❌ "You can click Save"
  - ✅ "Click Save"

### 2. **UI Label Rules** (`error`)
- **UI_001**: No articles or "button" with UI labels
  - ❌ "Click the Save button"
  - ✅ "Click Save"
- **UI_002**: No "on" after UI action verbs
  - ❌ "Click on Save"
  - ✅ "Click Save"

### 3. **Safety Rules** (`error`)
- **SAFETY_001**: NOTICE must not contain symbols
  - ❌ "NOTICE ⚠️ Handle carefully"
  - ✅ "NOTICE Handle carefully"
- **SAFETY_002**: WARNING/DANGER/CAUTION must have symbols
  - ❌ "WARNING High voltage"
  - ✅ "⚠️ WARNING High voltage"

### 4. **Voice Rules** (`error` / `warn`)
- **PERSON_001**: No personal pronouns
  - ❌ "You should configure..."
  - ✅ "Configure..."
- **IMPERATIVE_001**: Start with imperative verbs
  - ❌ "To save, click Save"
  - ✅ "Click Save"
- **PASSIVE_001**: Prefer active voice
  - ❌ "The file is saved..."
  - ✅ "The system saves the file..."

### 5. **Adverb Rules** (`warn`)
- **ADV_001**: Avoid precision-reducing adverbs
  - Blacklist: simply, easily, quickly, basically, very, really, extremely
  - ❌ "Simply click the button"
  - ✅ "Click the button"

### 6. **Punctuation Rules** (`warn`)
- **OXFORD_001**: Oxford comma in series
  - ❌ "Save, compile and deploy"
  - ✅ "Save, compile, and deploy"

### 7. **Phrasal Verb Rules** (`warn`)
- **PVERB_001**: Avoid translation-hostile phrasal verbs
  - ❌ "Set up the device"
  - ✅ "Configure the device"

### 8. **Clarity Rules** (`warn`)
- **VAGUE_001**: No vague terms
  - Blacklist: stuff, things, something, somehow, etc.
  - ❌ "Configure settings and stuff"
  - ✅ "Configure network, display, and security settings"

### 9. **Procedure Rules** (`error`)
- **ACTION_001**: One action per step
  - ❌ "Click Save. Then close the dialog."
  - ✅ "1. Click Save.\n2. Close the dialog."

### 10. **Inclusivity Rules** (`warn`)
- **GENDER_001**: Gender-neutral language
  - ❌ "The user can update his settings"
  - ✅ "Users can update their settings"

### 11. **Formality Rules** (`warn`)
- **CONTRACTION_001**: No contractions
  - ❌ "Don't close the window"
  - ✅ "Do not close the window"

### 12. **Jargon Rules** (`info`)
- **JARGON_001**: Simpler alternatives to corporate speak
  - ❌ "Utilize the robust API"
  - ✅ "Use the strong API"

## Rule Structure

Each rule in `rules.json` follows this atomic structure:

```json
{
  "rule_id": "TENSE_001",
  "category": "tense",
  "regex": "\\bwill\\b|\\bgoing to\\b|\\bshall\\b",
  "severity": "error",
  "message": "Future tense not allowed in procedures.",
  "suggestion": "Rewrite in simple present.",
  "example_violation": "The system will start automatically.",
  "example_correction": "The system starts automatically."
}
```

### Key Fields:
- **rule_id**: Unique identifier (e.g., `TENSE_001`)
- **category**: Logical grouping (tense, ui-label, safety, etc.)
- **regex**: Pattern to detect violations (case-insensitive)
- **severity**: `error` | `warn` | `info`
- **message**: What's wrong
- **suggestion**: How to fix it
- **example_violation**: Bad example (optional, for documentation)
- **example_correction**: Good example (optional, for documentation)

## UI Display

The system displays violations with color-coded badges:

### Error (Red)
```
🔴 Future tense not allowed in procedures. [ERROR]
Rule: TENSE_001
💡 Suggestion: Rewrite in simple present.
```

### Warning (Yellow)
```
🟡 Avoid adverbs. They reduce clarity. [WARNING]
Rule: ADV_001
💡 Suggestion: Remove or replace with measurable detail.
```

### Info (Blue)
```
🔵 Corporate jargon detected. [INFO]
Rule: JARGON_001
💡 Suggestion: Prefer simpler alternatives.
```

## Integration

The atomic rule checker integrates seamlessly with existing rules:

```python
# In app/rules/__init__.py
from app.rules.atomic_rules import check as check_atomic_rules

rule_functions = [
    check_atomic_rules,      # Runs FIRST for severity enforcement
    check_grammar_rules,
    check_style_rules,
    # ... other rules
]
```

## Usage

### For Developers

**Add a new rule:**
1. Edit `app/rules/rules.json`
2. Add new rule object with all required fields
3. Test with `test_atomic_rules.md`

**Reload rules at runtime:**
```python
from app.rules.loader import reload_rules
reload_rules()  # Force reload from disk
```

**Filter by severity:**
```python
from app.rules.loader import get_rules_by_severity
error_rules = get_rules_by_severity("error")
```

**Filter by category:**
```python
from app.rules.loader import get_rules_by_category
ui_rules = get_rules_by_category("ui-label")
```

### For Users

1. **Upload document** via web interface
2. **View violations** with color coding:
   - 🔴 Red = Must fix
   - 🟡 Yellow = Suggestion
   - 🔵 Blue = Informational
3. **Click AI button** for contextualized suggestions
4. **Fix errors** before document approval

## Testing

Use the provided test document:

```bash
# Upload test_atomic_rules.md through the web interface
# Expected results:
# - Multiple ERROR violations (red)
# - Multiple WARNING violations (yellow)
# - Multiple INFO violations (blue)
```

## Benefits

✅ **Deterministic**: Same input = same output, always  
✅ **Fast**: Regex-based, no LLM overhead  
✅ **Scalable**: Add rules without code changes  
✅ **Severity-aware**: Block critical issues, suggest improvements  
✅ **Translation-friendly**: Enforces patterns that translate well  
✅ **Consistent**: No subjective interpretation  

## What This System Does NOT Do

❌ Does not show the PDF/DOCX style guide to users  
❌ Does not store prose paragraphs  
❌ Does not make non-deterministic decisions  
❌ Does not require manual interpretation  

## Future Enhancements

- [ ] Rule priority/ordering system
- [ ] Custom rule sets per document type
- [ ] Rule exception handling (ignore specific instances)
- [ ] Batch rule updates from central repository
- [ ] Rule effectiveness analytics

## Related Files

- `test_atomic_rules.md` - Comprehensive test document
- `app/app.py` - Main Flask app with analysis integration
- `app/templates/index.html` - UI with severity color coding
- `rules.json` - Complete atomic rule set

---

**Status**: ✅ Fully Integrated  
**Last Updated**: December 9, 2025  
**Version**: 1.0
