# DocScanner AI - Reviewer-Grade Test Plan

**This is not unit testing. This is behavioral validation.**

## Overview

This test suite validates that DocScanner AI behaves like a **human reviewer**, not an overly aggressive AI assistant. The restraint is a feature, not a bug.

## Test Files

### 1. `test_reviewer_behavior.py`
**Primary behavioral validation suite**

Runs systematic tests across all reviewer decision types:

- **Document-Level Review (1.x)**: Validates gatekeeping and document intent classification
- **Sentence Eligibility (2.x)**: Confirms titles/headings/fragments are skipped
- **Verb Tense (3.x)**: Tests safe conversion vs. historical context preservation
- **Long Sentences (4.x)**: Validates auto-split vs. semantic explanation for complex sentences
- **Passive Voice (5.x)**: Tests active conversion vs. intentional passive preservation
- **Adverbs & Style (6.x)**: Confirms subjective terms get rationale, not blind removal
- **RAG Behavior (7.x)**: Validates no hallucination and graceful degradation

**Usage:**
```powershell
python test_reviewer_behavior.py
```

### 2. `tests/test_golden_document.py`
**Regression safety net**

Runs a comprehensive golden document containing all edge cases through the analyzer.

Run after **every major change** to detect unexpected behavior shifts.

**Usage:**
```powershell
python tests/test_golden_document.py
```

### 3. `tests/test_ui_consistency.py`
**UI label and rationale validation**

Validates:
- Decision labels match expected types (8.1)
- Reviewer rationale is always visible for non-rewrite outcomes (8.2)
- No "AI failed" or validation errors exposed to users

**Usage:**
```powershell
python tests/test_ui_consistency.py
```

### 4. `tests/golden_document.txt`
**Reference document for regression testing**

Contains all edge cases that must remain stable across releases.

## Running All Tests

```powershell
# Run full behavioral suite
python test_reviewer_behavior.py

# Run regression test
python tests/test_golden_document.py

# Run UI consistency validation
python tests/test_ui_consistency.py
```

## Test Philosophy

### What Makes a Test Pass?

A test passes when the system demonstrates **reviewer-grade restraint**:

- ✓ Titles and headings are **not** analyzed as sentences
- ✓ Historical context is **preserved**, not rewritten to present tense
- ✓ Complex compliance sentences get **explanation**, not automatic splitting
- ✓ Intentional passive voice is **preserved** with rationale
- ✓ Subjective terms get **rationale**, not blind removal
- ✓ RAG does **not hallucinate** or copy examples

### What Makes a Test Fail?

A test fails when the system behaves like a **noisy AI assistant**:

- ✗ Rewrites everything automatically
- ✗ Changes meaning to "improve" style
- ✗ Provides generic advice without specific rationale
- ✗ Analyzes non-sentences (titles, fragments)
- ✗ Invents information not present in the original

## Decision Type Mapping

| Decision Type | UI Label              | When to Use                                    |
|---------------|-----------------------|------------------------------------------------|
| `rewrite`     | AI-Enhanced Rewrite   | Safe, deterministic improvements               |
| `explain`     | Semantic Explanation  | Complex sentences requiring context            |
| `guide`       | Reviewer Guidance     | Structural issues, unclear intent              |
| `no_change`   | Reviewer Rationale    | Intentional choices, preserved context         |

## Expected Test Results

### Baseline Expectations

For a **stable implementation**, you should see:

- **Test 1.1** (Clean Procedural): Selective analysis, no heading rewrites
- **Test 2.1** (Title/Heading): No feedback, classified as title
- **Test 3.2** (Historical Context): Preserved past tense with rationale
- **Test 4.2** (Conditional Sentence): Semantic explanation, not split
- **Test 5.2** (Intentional Passive): Preserved with rationale
- **Test 6.1** (Subjective Adverb): Rationale explaining intentional use
- **Test 7.1** (RAG): No hallucination, domain terms preserved

### When to Stop

If outcomes shift unexpectedly after a code change:
1. **Stop adding features**
2. Run the golden document test
3. Compare before/after behavior
4. Fix the regression
5. Document the stability requirement

## Test Categories

### Document-Level Review (Gatekeeping)
Tests that validate document structure analysis before sentence-level processing.

**Why this matters:**
- Prevents analyzing non-documents (e.g., wall of text)
- Sets correct expectations for document type
- Enables selective rule application

### Sentence Eligibility Filtering
Tests that validate which text segments qualify as "sentences" for analysis.

**Why this matters:**
- Prevents false positives on titles, headings, fragments
- Reduces noise in reviewer feedback
- Maintains focus on actual prose

### Verb Tense Normalization
Tests that validate when to enforce simple present tense vs. preserve context.

**Why this matters:**
- Technical docs need consistent tense
- Historical/temporal context must be preserved
- Rewrites must not change meaning

### Long Sentence Handling
Tests that validate when to split vs. explain complex sentences.

**Why this matters:**
- Simple compound sentences → auto-split
- Complex conditional/compliance → explain
- Prevents breaking precise technical language

### Passive Voice
Tests that validate when to convert passive → active vs. preserve passive.

**Why this matters:**
- Known actor → active voice preferred
- Unknown/intentional → passive preserved
- RAG must not invent actors

### Adverbs & Style
Tests that validate subjective style choices get rationale, not blind rules.

**Why this matters:**
- "Properly", "correctly" may be intentional
- Context determines appropriateness
- Reviewer must explain, not dictate

### RAG Behavior
Tests that validate LLM integration doesn't hallucinate or copy examples.

**Why this matters:**
- Domain-specific terms must be preserved
- No invented content
- Graceful degradation when RAG unavailable

## Adding New Tests

When adding a test case, include:

1. **Test ID**: Category.number (e.g., 6.1)
2. **Name**: Brief description
3. **Input**: Exact text to analyze
4. **Expected Outcome**: Decision type
5. **Expected Behaviors**: What should happen
6. **Fail Conditions**: What must NOT happen
7. **Validation Keywords**: Domain terms that must be preserved (optional)

Example:

```python
TestCase(
    test_id="9.1",
    name="New Edge Case",
    category="New Category",
    input_text="Your test sentence here.",
    expected_outcome=OutcomeType.REVIEWER_RATIONALE,
    expected_behaviors=[
        "Specific behavior 1",
        "Specific behavior 2"
    ],
    fail_conditions=[
        "This should NOT happen",
        "This would be wrong"
    ],
    validation_keywords=["domain", "terms"]
)
```

## Continuous Validation

### Daily Development
Run `test_reviewer_behavior.py` before committing changes.

### Before Release
1. Run all test suites
2. Run golden document test
3. Compare with previous baseline
4. Document any intentional behavior changes

### After Bug Fixes
1. Add regression test for the bug
2. Verify all existing tests still pass
3. Update golden document if needed

## Final Reality Check

If all tests pass:
- ✓ Your app is **not a writing assistant**
- ✓ It is a **reviewer simulator**
- ✓ The restraint is a **feature**, not a failure

If something feels "too quiet":
- ✓ That's usually **correct**
- ✓ Reviewers are **selective**, not noisy
- ✓ Less feedback = more trust

---

**Remember:** You're building a reviewer, not a rewriter.
