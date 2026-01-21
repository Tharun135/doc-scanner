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
