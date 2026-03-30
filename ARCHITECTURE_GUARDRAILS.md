# Architecture Guardrails - Document Review Gate

**Date Locked:** January 20, 2026  
**System State:** Reviewer-first architecture implemented

---

## Critical Architectural Decisions (DO NOT REGRESS)

### 1. Gate Placement is Non-Negotiable

**Decision:** Document review gate runs AFTER parsing, BEFORE sentence extraction

**Why this matters:**
- Extracting sentences first = sentence-first bias
- Gate after parse = document-first thinking
- This single choice determines everything downstream

**Protected in code:**
- `app/app.py` line ~763 with ⚠️ NON-NEGOTIABLE comment
- If anyone suggests "let's extract sentences earlier for convenience" → **HARD NO**

**Validation:**
```python
# Correct order (LOCKED):
1. Parse file → HTML content
2. 🚧 DOCUMENT REVIEW GATE ← YOU ARE HERE
3. Extract sentences (conditional on gate result)
4. Analyze sentences (only flagged ones)

# FORBIDDEN order:
1. Parse file
2. Extract sentences
3. Try to gate analysis ← TOO LATE, bias already introduced
```

---

### 2. Gate Responsibility is Frozen

**What the gate does:**
- ✅ Identifies document-level issues
- ✅ Determines analysis scope (minimal/targeted/full)
- ✅ Flags confusion zones
- ✅ Blocks on fundamental problems

**What the gate must NEVER do:**
- ❌ Suggest fixes or rewrites
- ❌ Generate phrasing alternatives
- ❌ Compete with deterministic resolution
- ❌ Become a "second reviewer"

**Protected in code:**
- `core/document_review_gate.py` lines 1-10 with CRITICAL CONSTRAINT docstring

**Rule:**
> If the gate starts suggesting solutions, it has crossed the line.

---

### 3. Confusion Zones Stay Coarse-Grained

**Current scope (correct):**
- Dense paragraphs (>150 words)
- Jargon clusters (>3 technical terms)
- Structural breaks (missing sections)

**Forbidden scope creep:**
- ❌ Per-sentence confusion scoring (0.73 confusing)
- ❌ Fine-grained NLP heuristics
- ❌ Threshold tuning per rule
- ❌ ML-based complexity metrics

**Rule of thumb:**
> If a confusion zone can't be explained in one English sentence, it's too detailed.

**Example:**
- ✅ "This section feels heavy with jargon"
- ❌ "Sentence 4.2.3 has 0.73 confusion score due to syntactic complexity and lexical density"

---

### 4. Silence ≠ Perfection

**Old behavior (WRONG):**
```python
if not should_analyze:
    quality_score = 100  # Perfect!
```

**New behavior (CORRECT):**
```python
if not should_analyze:
    quality_score = None  # Not scored
    analysis_skipped = True  # Transparency
```

**Why this matters:**
- quality_score=100 will be displayed as "perfect"
- Users will chase scores
- Reintroduces sentence-first thinking

**Philosophy:**
> Silence = reviewer chose not to comment  
> Not = sentence is perfect

**Protected in code:**
- `app/app.py` line ~900 with "Silence ≠ perfection" comment
- `analysis_skipped` flag added to sentence data for transparency

---

### 5. Document Type Detection is a Hint, Not Gospel

**Current implementation:**
```python
document_type = "procedure"  # Treated as fact
```

**Required refinement:**
```python
document_type = {
    "type": "procedure",
    "confidence": 0.65  # Treat as hint
}
```

**Why:**
- Real documents are messy
- False confidence → false blocking
- Structure checks should only apply above confidence threshold (>0.6)

**Action needed:**
- Add confidence scoring to `detect_document_type()`
- Gate strict checks behind confidence threshold
- Be conservative on low confidence

---

### 6. ZIP Handling Decision (Pending)

**Current behavior:**
- ZIPs are merged into one document
- Review happens on merged content
- Feedback is not per-file

**Question to answer:**
> Are ZIP contents separate documents or one review unit?

**Options:**
1. **Separate reviews:** Each file gets its own document gate + sentence analysis
2. **Collection review:** ZIP gets summary with collection-level issues
3. **Hybrid:** Gate at collection level, detailed analysis per file

**What NOT to do:**
- ❌ Blend feedback silently across files
- ❌ Leave this ambiguous

**Decision deadline:** Before ZIPs become a major use case

**Protected in code:**
- `app/app.py` line ~284 with ⚠️ REVIEWER DECISION NEEDED comment

---

## Noise Reduction Validation

**Expected behavior:**
- Clean document → 20-40% sentences analyzed (targeted scope)
- Messy document → 40-60% sentences analyzed (full scope)
- Broken document → 0% sentences analyzed (blocking, early return)

**If analysis creeps above ~60% of sentences:**
→ Something is wrong with gating logic
→ Audit `should_analyze_sentence()` immediately

**Why 60% is the red line:**
- Above 60% = barely filtering
- Defeats the purpose of having a gate
- Signals drift back to sentence-first thinking

---

## Human Validation Checklist

**Do this next (not automated tests):**

Take 3 documents:
1. **Clean procedure doc** (steps, prerequisites, outcome)
2. **Messy concept doc** (wall of text, no structure)
3. **Incomplete doc** (no title, no goal)

For each, ask:
> "Did the reviewer stop me where a human would?"

**If YES for all 3:**
- ✅ Architecture is locked in
- ✅ Everything else is refinement
- ✅ Focus on UI and polish

**If NO for any:**
- ❌ Fix the gate, not the rules
- ❌ Do not add more sentence-level checks
- ❌ The problem is upstream (document understanding)

---

## Regression Indicators (Monitor These)

Any future change that does this is a regression:

1. **Extracts sentences before gate**
   - Even "just for counting"
   - Even "just for display"
   - **NO EXCEPTIONS**

2. **Increases default analysis scope**
   - "Let's be more thorough"
   - "Users want more feedback"
   - **Push back: This defeats the design**

3. **Adds "quick checks" before gate**
   - "Just one small rule check"
   - "Won't hurt to check this first"
   - **This is how it starts**

4. **Makes gate suggest fixes**
   - "It already knows the problem"
   - "Why not suggest the solution?"
   - **Gate identifies, downstream resolves**

5. **Fine-tunes confusion zone thresholds**
   - "Let's make this more precise"
   - "ML can improve this"
   - **Coarse-grained is intentional**

---

## The Litmus Test

Before approving any change to the upload pipeline, ask:

> "Would a human reviewer pause here?"

If NO → Don't build it

This simple question protects the architecture better than any test suite.

---

## System Philosophy (Never Forget)

**Old system:**
> "Analyze everything, surface everything, let users filter"

**New system:**
> "Earn the right to analyze sentences by understanding the document first"

This is the hard leap.

The system crossed from:
- "Interesting NLP project"

To:
- **"Opinionated review system"**

---

## Critical Policy Guardrails (Added January 21, 2026)

### 3. AI Rewrite Block Rule - HARD INVARIANT

**Policy Statement:**
> **AI must never rewrite sentences that combine normative language with conditional or alternative logic. These sentences require human judgment.**

**Why this is non-negotiable:**
- Normative language defines mandatory requirements (`must`, `shall`, `required`)
- Conditional/alternative logic creates multiple execution paths (`if`, `or`, `in case`)
- Even small word changes can shift requirement scope or alter which conditions apply to which alternatives
- Understanding is not the same as authority

**Enforcement:**
```python
# Located in: app/intelligent_ai_improvement.py

def blocks_ai_rewrite(sentence: str) -> bool:
    return (
        contains_normative_language(sentence)
        and contains_conditional_or_alternative(sentence)
    )
```

**Detection criteria:**
- Normative: ` must `, ` shall `, ` required `, ` mandatory `, ` prohibited `
- Conditional: ` if `, ` in case `, ` unless `, ` provided that `, ` or `, ` and/or `, ` either `, ` neither `

**What happens when blocked:**
- AI rewrite is prevented entirely
- System returns semantic explanation instead
- Explanation clarifies why no rewrite is safe
- User gets transparency, not false confidence

**Protected in code:**
- Policy functions: Lines ~125-175 of `intelligent_ai_improvement.py`
- Enforcement point: After validation, before result return (~Line 2395)
- Hard assertion: Catches any bypasses (~Line 2440)

**Example of blocked sentence:**
> "The server certificate must include the IP address of the server in the SAN field or the FQDN in case it is already registered in the DNS server."

This sentence:
- ✅ Contains `must` (normative)
- ✅ Contains `or` + `in case` (conditional/alternative)
- 🛑 **BLOCKED from AI rewrite**
- ✅ Gets semantic explanation instead

**Validation:**
```python
# Hard assertion catches violations:
if suggestion != sentence_context:
    assert not blocks_ai_rewrite(sentence_context), (
        "POLICY VIOLATION: AI rewrite for normative + conditional"
    )
```

**Impact:**
- False positives are acceptable (over-caution is safe)
- False negatives are not acceptable (risk is unacceptable)
- Applies globally to ALL issue types (passive voice, long sentence, wording, etc.)
- Cannot be bypassed by prompt engineering or model confidence

---

## Remaining Work (NOT Architecture)

These are refinements, not structural changes:

1. ✅ Gate implementation complete
2. ✅ Conditional sentence analysis working
3. ✅ Early return on blocking issues working
4. 🔄 Progress tracker stages (cosmetic)
5. 🔄 Frontend handling of document_review UI format
6. 🔄 ZIP handling decision
7. 🔄 Document type confidence scoring
8. 🔄 Quality index rethinking (formula is still wrong)

**Priority:** Human validation with 3 real documents

---

## Sign-off

This document locks in the architectural decisions made on January 20, 2026.

Any change that violates these guardrails must be explicitly justified and documented here.

**The danger is not technical gaps. The danger is feature creep.**

---

**Status:** 🔒 Architecture locked, pending validation

## Addendum: Simple Present Tense Normalization (January 22, 2026)

### Feature: Non-Simple Present Tense Detection & Conversion

**Classification:** Documentation normalization (NOT grammar correction)

**Three Frozen Invariants:**

> **1. Non-Sentential Gate: Titles, headings, gerund phrases, and fragments NEVER reach sentence-level rules.**

> **2. Metadiscourse Gate: Structural sentences that introduce examples, figures, or guide readers are NEVER rewritten.**

> **3. Tense conversion is allowed only when it preserves time, obligation, and intent.**

These rules prevent 90% of future bugs. Never relax them.

---

### Eligibility Gate (Non-Negotiable)

Every sentence is classified into ONE of five semantic classes:

| Class                    | Auto-Convert | Rationale                                    |
| ------------------------ | ------------ | -------------------------------------------- |
| Instructional            |             | Procedures should be timeless                |
| Descriptive              |             | System behavior is present-tense            |
| Explanatory              |             | Examples normalized to present explanations |
| Historical               |             | Past events stay in past tense              |
| Compliance + Conditional |             | Requirements with conditions never auto-converted |

**Code Location:** `app/rules/simple_present_normalization.py`  `can_convert_to_simple_present()`

---

### Validation Contract (Strict)

AI rewrite is REJECTED if:

- Output not in simple present tense
- Obligation terms removed (`must`  `is`)
- New verbs introduced
- Semantic similarity < 0.6
- Subject changed

**If validation fails:** Discard rewrite, show reviewer guidance (never "AI failed")

**Code Location:** `app/rules/simple_present_normalization.py`  `validate_simple_present_rewrite()`

---

### Decision Flow (Locked)

`python
# 1. Classify sentence
classification = classify_sentence_for_tense(sentence)

# 2. Check eligibility
if classification in {"historical", "compliance_conditional"}:
    return BLOCKED  # Show semantic_explanation or reviewer_rationale

# 3. Execute AI conversion (only if eligible)
prompt = build_simple_present_prompt(sentence)
rewrite = call_llm(prompt)

# 4. Validate (strict)
if not validate_simple_present_rewrite(original, rewrite):
    return reviewer_guidance  # Discard AI output

# 5. Return validated rewrite
return ai_enhanced(rewrite)
`

---

### Examples (Expected Behavior)

####  Safe Conversion

**Input:** "The system will validate the input."  
**Output:** "The system validates the input."  
**Decision:** `ai_enhanced`

---

####  Blocked: Historical Context

**Input:** "In version 3.0, the module was redesigned."  
**Output:** *No conversion attempted*  
**Decision:** `reviewer_rationale` ("This sentence describes a past event.")

---

####  Blocked: Compliance + Condition

**Input:** "The certificate must be generated after installation."  
**Output:** *No conversion attempted*  
**Decision:** `semantic_explanation` ("Changing tense could alter compliance meaning.")

---

####  Validation Failed

**AI Output:** "The certificate is generated after installation." *(dropped "must")*  
**System Action:** Discard rewrite  
**User Sees:** `reviewer_guidance` ("Rewrite manually if appropriate")

---

### UI Copy (Trust-Preserving)

Never expose validation failures as errors. Use this copy:

> **Reviewer guidance**  
> This sentence does not use simple present tense.  
> Rewrite it manually if doing so does not change the meaning.

This preserves trust even when AI cannot safely convert.

---

### Integration Points

1. **Rule Registration:** `app/rules/simple_present_normalization.py`
2. **Eligibility Check:** `app/intelligent_ai_improvement.py`  `should_attempt_rewrite()`
3. **Decision Handler:** `app/intelligent_ai_improvement.py`  `get_enhanced_ai_suggestion()`
4. **Tests:** `tests/test_simple_present_normalization.py`

---

### Why This Feature is Safe

-  Deterministic eligibility (no AI decides "should I?")
-  Strict validation (AI output is disposable)
-  Clear fallbacks (guidance, not guesses)
-  Aligned with style guide (Level 1 rule)
-  Does NOT rewrite events, only explanations

This is **reviewer-grade behavior**, not chatbot behavior.

---

## Critical Addition: Non-Sentential Text Gate (2026-01-22)

**Problem Identified:** Titles and headings ("Configuring KEPware server with certificates") were being incorrectly flagged for tense normalization because the system assumed all text units were complete sentences.

**Solution Implemented:** Added `is_non_sentential()` gate that runs BEFORE all sentence-level rules:

- Detects gerund phrases (VBG-starting fragments with no finite verb)
- Detects noun phrase titles (short text with no verb)
- Detects title-case patterns
- Detects fragments (<5 words with no complete verb phrase)

**Integration Points:**
- `simple_present_normalization.py:check()` - Returns empty issues list for non-sentential text
- `intelligent_ai_improvement.py` - Returns `reviewer_rationale` explaining it's a heading/title

**Test Coverage:** 4 dedicated tests in `test_simple_present_normalization.py`:
- `test_detect_title_gerund_phrase()`
- `test_detect_short_title()`
- `test_detect_noun_phrase_title()`
- `test_allow_complete_sentences()`

**Architectural Impact:** This reinforces the invariant that **sentence-level rules only apply to complete sentences**. Future rules must include this gate.

---

## Critical Addition: Metadiscourse Gate (2026-01-22)

**Problem Identified:** Metadiscourse sentences ("Here's an example of a properly configured certificate:") were being incorrectly flagged for tense normalization even though they are already in simple present and serve a structural purpose.

**Solution Implemented:** Added `is_metadiscourse()` gate that runs BEFORE tense analysis:

- Detects sentences that introduce examples ("Here's an example of...")
- Detects figure/table/code references ("The following figure shows...")
- Detects section introducers ("This section describes...")
- Detects structural colons used for content introduction

**Integration Points:**
- `simple_present_normalization.py:check()` - Returns empty issues list for metadiscourse
- `intelligent_ai_improvement.py` - Returns `reviewer_rationale` explaining metadiscourse is exempt

**Test Coverage:** 4 dedicated tests in `test_simple_present_normalization.py`:
- `test_detect_metadiscourse_example_introducers()`
- `test_detect_metadiscourse_figure_references()`
- `test_detect_metadiscourse_section_introducers()`
- `test_allow_non_metadiscourse_sentences()`

**Architectural Impact:** This reinforces the invariant that **tense rules apply only to content sentences, not structural text**. Metadiscourse is always exempt from rewriting.

**User Trust Impact:** Before this fix, the system would say "Consider converting to present tense" and then echo the same sentence back, which felt broken. Now it correctly says "This sentence introduces an example. Tense normalization does not apply."

---
