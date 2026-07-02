# Atomic Rules Quick Reference

## 🎯 Quick Start

### Run Tests
```powershell
# Python unit tests
python test_atomic_rules.py

# Upload test (requires running server)
.\test-atomic-rules-upload.ps1
```

### View Rules
```python
from app.rules.loader import load_rules
rules = load_rules()
print(f"Loaded {len(rules)} rules")
```

## 📋 All Rules at a Glance

| Rule ID | Category | Severity | What It Catches | Example Violation |
|---------|----------|----------|-----------------|-------------------|
| **TENSE_001** | tense | 🔴 error | Future tense | "will start" |
| **TENSE_002** | tense | 🟡 warn | Modal verbs | "can click" |
| **UI_001** | ui-label | 🔴 error | "button" with UI labels | "Click the Save button" |
| **UI_002** | ui-label | 🔴 error | "on" after UI verbs | "Click on Save" |
| **SAFETY_001** | safety | 🔴 error | NOTICE with symbol | "NOTICE ⚠️" |
| **SAFETY_002** | safety | 🔴 error | WARNING without symbol | "WARNING text" |
| **PERSON_001** | voice | 🔴 error | Personal pronouns | "you should" |
| **IMPERATIVE_001** | voice | 🟡 warn | Non-imperative start | "To save, click..." |
| **ADV_001** | adverb | 🟡 warn | Weak adverbs | "simply", "easily" |
| **OXFORD_001** | punctuation | 🟡 warn | Missing Oxford comma | "A, B and C" |
| **PVERB_001** | phrasal-verb | 🟡 warn | Phrasal verbs | "set up" |
| **VAGUE_001** | clarity | 🟡 warn | Vague terms | "stuff", "things" |
| **ACTION_001** | procedure | 🔴 error | Multiple actions | "Do X. Then Y." |
| **PASSIVE_001** | voice | 🟡 warn | Passive voice | "is saved" |
| **CONDITIONAL_001** | procedure | 🔵 info | Conditional statements | "if X, do Y" |
| **PLURAL_001** | ui-label | 🟡 warn | Plural UI references | "buttons" |
| **ARTICLE_001** | article | 🟡 warn | Unnecessary articles | "the following" |
| **GENDER_001** | inclusivity | 🟡 warn | Gender-specific language | "his settings" |
| **CONTRACTION_001** | formality | 🟡 warn | Contractions | "don't" |
| **JARGON_001** | clarity | 🔵 info | Corporate jargon | "utilize" |

## 🔴 Critical Errors (Must Fix)

These **block document approval**:

1. **Future Tense** (TENSE_001)
   - ❌ "The system will display results"
   - ✅ "The system displays results"

2. **UI Label Violations** (UI_001, UI_002)
   - ❌ "Click the Save button"
   - ✅ "Click Save"
   - ❌ "Click on Settings"
   - ✅ "Click Settings"

3. **Personal Pronouns** (PERSON_001)
   - ❌ "You should configure your settings"
   - ✅ "Configure the settings"

4. **Safety Symbols** (SAFETY_001, SAFETY_002)
   - ❌ "NOTICE ⚠️ Handle carefully" (NOTICE must not have symbol)
   - ✅ "NOTICE Handle carefully"
   - ❌ "WARNING High voltage" (WARNING must have symbol)
   - ✅ "⚠️ WARNING High voltage"

5. **Multiple Actions** (ACTION_001)
   - ❌ "Click Save. Then close the dialog."
   - ✅ "1. Click Save.\n2. Close the dialog."

## 🟡 Warnings (Suggestions)

These are **soft recommendations**:

### Writing Style
- **Adverbs** (ADV_001): Remove "simply", "easily", "quickly", "very"
- **Passive Voice** (PASSIVE_001): Prefer active constructions
- **Phrasal Verbs** (PVERB_001): Use single verbs for translation
- **Vague Terms** (VAGUE_001): Replace "stuff", "things" with specifics

### Grammar & Punctuation
- **Oxford Comma** (OXFORD_001): Use serial comma
- **Contractions** (CONTRACTION_001): Write out "don't" → "do not"

### Clarity
- **Articles** (ARTICLE_001): Remove unnecessary "the"
- **Plural UI** (PLURAL_001): Name specific buttons, not "buttons"
- **Imperative** (IMPERATIVE_001): Start steps with verbs

### Inclusivity
- **Gender** (GENDER_001): Use "their" not "his/her"

## 🔵 Info (Helpful Hints)

These provide **visibility only**:

- **Jargon** (JARGON_001): Simpler alternatives for corporate speak
- **Conditionals** (CONDITIONAL_001): Consider restructuring if/then statements

## 🚀 Adding New Rules

Edit `app/rules/rules.json`:

```json
{
  "rule_id": "NEW_001",
  "category": "custom",
  "regex": "\\byour pattern\\b",
  "severity": "error|warn|info",
  "message": "Describe the violation",
  "suggestion": "How to fix it",
  "example_violation": "Bad example",
  "example_correction": "Good example"
}
```

Rules auto-load on next analysis (cached in memory).

## 🎨 UI Color Coding

- 🔴 **Red text + ERROR badge** = Must fix before approval
- 🟡 **Yellow text + WARNING badge** = Consider improving
- 🔵 **Blue text + INFO badge** = Nice to know

## 📊 Severity Decision Tree

```
Is it a safety issue? → 🔴 error
Is it a procedure error? → 🔴 error
Is it a UI label mistake? → 🔴 error
Is it future tense in steps? → 🔴 error
Is it a personal pronoun? → 🔴 error

Is it a translation problem? → 🟡 warn
Is it a style issue? → 🟡 warn
Is it a punctuation suggestion? → 🟡 warn

Is it informational only? → 🔵 info
```

## 🔧 Troubleshooting

### Rules not loading
```python
from app.rules.loader import reload_rules
reload_rules()  # Force reload
```

### Check which rules apply
```python
from app.rules.loader import get_rules_by_severity
errors = get_rules_by_severity("error")
print([r['rule_id'] for r in errors])
```

### Test specific rule
```python
from app.rules.matcher import apply_rules
from app.rules.loader import load_rules

rules = load_rules()
sentence = "You will click the Save button."
violations = apply_rules(sentence, rules)
print(violations)
```

## 📚 Further Reading

- `ATOMIC_RULES_SYSTEM.md` - Complete documentation
- `ATOMIC_RULES_COMPLETE.md` - Implementation summary
- `rules.json` - Full rule definitions
- `test_atomic_rules.md` - Test document with examples

---

**Version**: 1.0.0  
**Rules**: 20 atomic rules  
**Coverage**: All major technical writing categories  
**Status**: ✅ Production Ready
