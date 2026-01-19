# Issue Classification Reference

## Real Issues Detected by the System

This document lists the 10 core issues the document scanner already flags, along with their deterministic resolutions.

---

## 1. PASSIVE_VOICE

**Detection Pattern:**
- spaCy dependency: `auxpass` (auxiliary passive)
- Pattern: "was/were/is/are + past participle"

**Issue Type:** `IssueType.PASSIVE_VOICE`

**Resolution Class:** `ResolutionClass.REWRITE_ACTIVE`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This sentence uses passive voice. Active voice is clearer and more direct.

Action: Rewrite to show who performs the action.
Example: 'The file was opened' → 'The system opens the file'
```

**LLM Role:** Adapt rewrite to specific sentence structure

**RAG Query:** "Example of rewriting passive voice to active voice in technical writing"

---

## 2. LONG_SENTENCE

**Detection Pattern:**
- Sentence length > 25 words
- Excludes titles, headings, and markdown tables

**Issue Type:** `IssueType.LONG_SENTENCE`

**Resolution Class:** `ResolutionClass.SIMPLIFY_SENTENCE`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This sentence combines more than one idea, making it harder to follow.

Action: Break this into 2-3 shorter sentences.
Each sentence should convey one clear idea.
```

**LLM Role:** Suggest specific breakpoints in the sentence

**RAG Query:** "Example of breaking a complex sentence into simpler ones"

---

## 3. VAGUE_TERM

**Detection Pattern:**
- Words: "some", "several", "various", "stuff", "things"
- Detected in sentence context

**Issue Type:** `IssueType.VAGUE_TERM`

**Resolution Class:** `ResolutionClass.REPLACE_WITH_SPECIFIC`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This uses a vague term that doesn't give the reader specific information.

Action: Replace with a concrete term or number.
Example: 'several times' → 'three times' or 'every 5 seconds'
```

**LLM Role:** Suggest appropriate specific replacement based on context

**RAG Query:** "Example of replacing vague terms with specific terms"

---

## 4. MISSING_PREREQUISITE

**Detection Pattern:**
- Document type: 'manual' or 'procedure'
- No section matching: "prerequisite", "before you begin", "requirement"

**Issue Type:** `IssueType.MISSING_PREREQUISITE`

**Resolution Class:** `ResolutionClass.ASK_FOR_PREREQUISITES`

**Severity:** `BLOCKING`

**Deterministic Fallback:**
```
This procedure lacks a Prerequisites section. Users need to know what's required before starting.

Action: Add a 'Prerequisites' section at the start listing:
- Required permissions or access
- Necessary tools or software
- Required knowledge or prior steps
```

**LLM Role:** Not applicable (document-level issue, no LLM needed)

**RAG Query:** N/A

---

## 5. DENSE_STEP

**Detection Pattern:**
- Step contains multiple actions (detected by multiple verbs/commands)
- Common in procedure documents

**Issue Type:** `IssueType.DENSE_STEP`

**Resolution Class:** `ResolutionClass.BREAK_INTO_STEPS`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This step combines multiple actions. As a first-time user, this is hard to follow.

Action: Split into separate numbered steps.
Each step should contain:
1. One clear action
2. Expected result or verification
```

**LLM Role:** Identify natural breakpoints and suggest sub-steps

**RAG Query:** "Example of breaking a complex step into numbered substeps"

---

## 6. STEP_ORDER_PROBLEM

**Detection Pattern:**
- Prerequisite actions appear after dependent actions
- Detected via section ordering analysis

**Issue Type:** `IssueType.STEP_ORDER_PROBLEM`

**Resolution Class:** `ResolutionClass.REORDER_GUIDANCE`

**Severity:** `BLOCKING`

**Deterministic Fallback:**
```
These steps appear out of logical order. Users may fail if they follow them as written.

Action: Reorder steps to match dependencies.
Rule: Prerequisites must come before dependent actions.
```

**LLM Role:** Not needed (ordering is structural)

**RAG Query:** N/A

---

## 7. UNDEFINED_ACRONYM

**Detection Pattern:**
- Pattern: 2+ consecutive capital letters
- Not in predefined list (API, SQL, etc.)
- Not defined in text (no "Full Term (ACRONYM)" pattern)

**Issue Type:** `IssueType.UNDEFINED_ACRONYM`

**Resolution Class:** `ResolutionClass.DEFINE_ACRONYM`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This acronym appears without definition. First-time users may not know what it means.

Action: Define on first use in this format:
Full Term (ACRONYM)
Example: 'Application Programming Interface (API)'
```

**LLM Role:** Not needed (format is standard)

**RAG Query:** N/A

---

## 8. INCONSISTENT_TERMINOLOGY

**Detection Pattern:**
- Same concept referred to by different terms
- Detected via terminology mapping in document context

**Issue Type:** `IssueType.INCONSISTENT_TERMINOLOGY`

**Resolution Class:** `ResolutionClass.STANDARDIZE_TERM`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This document uses multiple terms for the same concept, which can confuse readers.

Action: Choose one canonical term and use it consistently.
Example: Always use 'user' instead of mixing 'user', 'customer', 'client'
```

**LLM Role:** Not needed (replacement is mechanical)

**RAG Query:** N/A

---

## 9. MIXED_TENSE

**Detection Pattern:**
- Document uses mixed verb tenses (past/present/future)
- Detected via spaCy verb tense analysis

**Issue Type:** `IssueType.MIXED_TENSE`

**Resolution Class:** `ResolutionClass.UNIFY_TENSE`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This document mixes verb tenses, which can confuse the reader about timing.

Action: Choose one tense and use it consistently.
For procedures: Use present tense ('Click the button')
For reports: Use past tense ('The system processed the request')
```

**LLM Role:** Suggest appropriate tense based on document type

**RAG Query:** N/A

---

## 10. MISSING_INTRODUCTION

**Detection Pattern:**
- No section matching: "introduction", "overview"
- Document type: not 'reference' or 'api'

**Issue Type:** `IssueType.MISSING_INTRODUCTION`

**Resolution Class:** `ResolutionClass.ADD_INTRODUCTION`

**Severity:** `ADVISORY`

**Deterministic Fallback:**
```
This document lacks an introduction. Users need context before diving into details.

Action: Add an Introduction section that answers:
- What is this document about?
- Who should read it?
- What will the reader accomplish?
```

**LLM Role:** Not needed (structure is standard)

**RAG Query:** N/A

---

## Summary: LLM Usage

Of the 10 issues:

- **3 use LLM** for content adaptation:
  - Passive voice (rewrite)
  - Long sentence (break points)
  - Vague term (specific replacement)

- **7 use deterministic logic only**:
  - Missing prerequisite
  - Dense step
  - Step order problem
  - Undefined acronym
  - Inconsistent terminology
  - Mixed tense
  - Missing introduction

This dramatically reduces LLM dependency while maintaining high quality guidance.

---

## Value Guarantee

Every resolution has:

1. **Clear issue classification** - No ambiguity about what's wrong
2. **Deterministic fallback** - Always useful guidance even if LLM fails
3. **Actionable next step** - User always knows what to do
4. **Validation threshold** - Output must meet quality bar

This ensures consistent, actionable feedback regardless of:
- RAG database quality
- LLM availability
- Model conservativeness
