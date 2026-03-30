# Simple Present Tense Normalization - Feature Documentation

**Status:** ✅ Implemented and tested  
**Date:** January 22, 2026

---

## Overview

This feature automatically converts sentences to simple present tense when appropriate, according to documentation style guide standards. This is **documentation normalization**, not grammar correction.

### Key Principle

> **Tense conversion is allowed only when it preserves time, obligation, and intent.**

---

## How It Works

### 1. Sentence Classification

Every sentence is classified into one of five categories:

| Category | Description | Auto-Convert? |
|----------|-------------|---------------|
| **Instructional** | Procedures, steps ("Click", "Configure") | ✅ Yes |
| **Descriptive** | System behavior ("The server processes...") | ✅ Yes |
| **Explanatory** | Examples ("For example, the client was...") | ✅ Yes |
| **Historical** | Past events ("In version 3.0, was redesigned") | ❌ No |
| **Compliance + Conditional** | Requirements with conditions ("must be...after") | ❌ No |

### 2. Tense Detection

Uses spaCy NLP to detect verb tense:
- Past tense: "was", "were", "worked", "had been"
- Future tense: "will", "shall", "going to"
- Present tense: "is", "are", "processes"
- Mixed tense: combination of above

### 3. Eligibility Check

Before any conversion:
- ✅ **Allow** if: instructional, descriptive, or explanatory
- ❌ **Block** if: historical context or compliance with conditions
- ⏭️ **Skip** if: already in present tense

### 4. AI Conversion

If eligible, AI rewrites using this strict prompt:

```
Rewrite the following sentence in simple present tense.

Rules (MANDATORY):
- Preserve the original meaning exactly.
- Do NOT add or remove conditions.
- Do NOT change obligation strength (must, shall, required).
- Do NOT remove technical terms or qualifiers.
- Do NOT introduce new actions.
- Do NOT explain your answer.
- Output only the rewritten sentence.

Sentence:
"[original sentence]"
```

### 5. Strict Validation

AI output is **rejected** if:
- Not in simple present tense
- Obligation terms removed ("must" → "is")
- New verbs introduced
- Semantic similarity < 60%
- Subject changed

If validation fails → show reviewer guidance instead

---

## Examples

### ✅ Successful Conversion

**Input:**
```
The system will validate the input.
```

**Output:**
```
The system validates the input.
```

**UI Display:** `ai_enhanced` with note "Converted to simple present tense"

---

### ✅ Explanatory Conversion

**Input:**
```
For example, in the setup, the client "SE" was initially untrusted. 
Only after manually trusting it did the communication work.
```

**Output:**
```
For example, in this setup, the client "SE" is initially untrusted, 
and communication works only after you manually trust it.
```

**UI Display:** `ai_enhanced`

---

### ❌ Blocked: Historical Context

**Input:**
```
In version 3.0, the module was redesigned.
```

**Output:** *No conversion attempted*

**UI Display:** 
```
Reviewer Rationale
This sentence describes a past event or historical context. 
Present tense is not appropriate here.
```

---

### ❌ Blocked: Compliance with Conditions

**Input:**
```
The certificate must be generated after installation.
```

**Output:** *No conversion attempted*

**UI Display:**
```
Semantic Explanation
This sentence expresses a mandatory requirement with conditional logic. 
Automatic tense conversion could alter the compliance meaning.
```

---

### ⚠️ Validation Failed

**AI Output (incorrect):**
```
The certificate is generated after installation.
```
*(Dropped "must")*

**System Action:** Discard AI output

**UI Display:**
```
Reviewer Guidance
This sentence does not use simple present tense. 
Rewrite it manually if doing so does not change the meaning.
```

---

## File Locations

### Core Module
```
app/rules/simple_present_normalization.py
```

**Key Functions:**
- `detect_verb_tense(sentence)` - Detects tense using spaCy
- `classify_sentence_for_tense(sentence)` - Classifies semantic category
- `can_convert_to_simple_present(sentence)` - Eligibility gate
- `build_simple_present_prompt(sentence)` - AI prompt builder
- `validate_simple_present_rewrite(original, rewritten)` - Strict validator

### Integration Points

1. **Eligibility Check:**
   ```python
   # app/intelligent_ai_improvement.py:should_attempt_rewrite()
   if 'tense' in issue_lower or 'non_simple_present' in issue_lower:
       from app.rules.simple_present_normalization import can_convert_to_simple_present
       allowed, reason = can_convert_to_simple_present(sentence)
       return allowed, reason
   ```

2. **Decision Handler:**
   ```python
   # app/intelligent_ai_improvement.py:get_enhanced_ai_suggestion()
   # Lines ~2277-2417 handle tense normalization logic
   ```

3. **Tests:**
   ```
   tests/test_simple_present_normalization.py
   ```
   27 comprehensive tests covering all scenarios

---

## Testing

Run all tests:
```bash
python -m pytest tests/test_simple_present_normalization.py -v
```

Expected result: **27 passed**

Test coverage:
- ✅ Tense detection (past, present, future, mixed)
- ✅ Sentence classification (all 5 categories)
- ✅ Eligibility checks (allow/block decisions)
- ✅ Validation (success and all failure modes)
- ✅ End-to-end realistic scenarios

---

## Usage in DocScanner

### Automatic Detection

When analyzing a document, the system automatically:
1. Detects sentences not in simple present tense
2. Classifies them semantically
3. Attempts conversion if safe
4. Validates AI output
5. Falls back to guidance if needed

### Manual Trigger

You can also manually request tense normalization by:
1. Flagging a sentence issue with type: `non_simple_present_tense`
2. Calling AI suggestion endpoint with feedback containing "tense"

### Configuration

No configuration needed - the feature uses:
- Existing Ollama AI infrastructure
- spaCy NLP models (if available)
- Style guide alignment (built-in)

---

## Safety Guarantees

### What This Feature NEVER Does

❌ Rewrite historical descriptions  
❌ Change compliance requirements  
❌ Alter temporal meaning  
❌ Remove obligation terms  
❌ Guess when uncertain  

### What This Feature ALWAYS Does

✅ Check eligibility before conversion  
✅ Validate AI output strictly  
✅ Preserve meaning and intent  
✅ Provide clear fallback guidance  
✅ Maintain trust with users  

---

## Troubleshooting

### Issue: "simple_present_normalization module not available"

**Cause:** Module not found in Python path

**Fix:**
```bash
# Verify module exists
ls app/rules/simple_present_normalization.py

# Restart server to reload modules
```

### Issue: spaCy not available warnings

**Cause:** spaCy not installed or model not downloaded

**Fix:**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Note:** Feature works without spaCy (uses fallback detection)

### Issue: All conversions showing "reviewer guidance"

**Cause:** Ollama AI not available or not responding

**Check:**
```bash
curl http://localhost:11434/api/generate -d '{"model":"llama3.2:1b","prompt":"test"}'
```

**Note:** This is expected behavior if AI is unavailable - system falls back safely

---

## Performance Impact

- **Detection:** <10ms per sentence (spaCy)
- **Classification:** <1ms (rule-based)
- **AI Conversion:** 1-3 seconds (Ollama LLM)
- **Validation:** <5ms (difflib similarity)

**Optimization:** Classification and eligibility checks run before AI, preventing unnecessary LLM calls.

---

## Future Enhancements (Optional)

Potential improvements (not required):

1. **Caching:** Cache classification results for repeated sentences
2. **Batch Processing:** Convert multiple sentences in one AI call
3. **Learning:** Track which conversions users accept/reject
4. **Context-Aware:** Use surrounding sentences for better decisions

---

## References

- **Guardrails:** `ARCHITECTURE_GUARDRAILS.md` (Addendum: January 22, 2026)
- **Tests:** `tests/test_simple_present_normalization.py`
- **Core Module:** `app/rules/simple_present_normalization.py`
- **Integration:** `app/intelligent_ai_improvement.py`

---

## Questions?

For implementation questions, refer to:
- Code comments in `simple_present_normalization.py`
- Test examples in `test_simple_present_normalization.py`
- Decision flow in `ARCHITECTURE_GUARDRAILS.md`

**Remember:** When in doubt, block the conversion and show guidance. Trust is more valuable than automation.
