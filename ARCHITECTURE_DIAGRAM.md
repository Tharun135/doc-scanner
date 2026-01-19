# Architecture Diagram: Deterministic Suggestion System

## Traditional Flow (Problem)

```
┌─────────────────┐
│  Issue Detected │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  "Here's an issue, suggest something"   │
│          (Ask LLM to decide)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  LLM tries to figure out:               │
│  - What the problem is                  │
│  - How to fix it                        │
│  - What to say                          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  RAG tries to find inspiration          │
│  (Weak retrieval → weak output)         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Conservative model hedges               │
│  "Consider...", "Might...", "Perhaps..." │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  ❌ Vague or useless suggestion          │
│  ❌ User asks: "What should I do?"       │
└──────────────────────────────────────────┘
```

## New Flow (Solution)

```
┌─────────────────┐
│  Issue Detected │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  Classify Deterministically                  │
│  (Pattern matching in code)                  │
│                                              │
│  if 'passive' in feedback:                   │
│      return IssueType.PASSIVE_VOICE          │
│                                              │
│  If no clean match → return None             │
│  (Don't show unmapped issues)                │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  Map to Resolution Class                     │
│  (Deterministic lookup)                      │
│                                              │
│  ISSUE_TO_RESOLUTION = {                     │
│    PASSIVE_VOICE: REWRITE_ACTIVE,            │
│    LONG_SENTENCE: SIMPLIFY_SENTENCE,         │
│    ...                                       │
│  }                                           │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  Get Deterministic Template + Fallback       │
│                                              │
│  ResolutionTemplate(                         │
│    fallback="Active voice is clearer...",    │
│    action_required="Rewrite in active voice",│
│    template="{explanation}",                 │
│  )                                           │
│                                              │
│  ✅ GUARANTEE: Always useful                 │
└────────┬─────────────────────────────────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────────┐            ┌─────────────────────┐
│  Try RAG Enhancement│            │  Try LLM Phrasing   │
│  (Optional)         │            │  (Optional)         │
│                     │            │                     │
│  Query: "Example of │            │  Prompt: "Adapt     │
│  rewriting passive  │            │  this template:     │
│  to active"         │            │  {template}         │
│                     │            │  to this sentence:  │
│  Timeout: 3s        │            │  {sentence}"        │
│  Fail → Continue    │            │                     │
└─────────┬───────────┘            │  Timeout: 10s       │
          │                        │  Fail → Continue    │
          │                        └─────────┬───────────┘
          │                                  │
          └──────────┬───────────────────────┘
                     │
                     ▼
         ┌────────────────────────────────────┐
         │  Select Best Guidance              │
         │                                    │
         │  Priority:                         │
         │  1. RAG (has concrete example)     │
         │  2. LLM (adapted to content)       │
         │  3. Fallback (always works)        │
         └────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────────────────────────┐
         │  Validate Quality                  │
         │                                    │
         │  - Different from original?        │
         │  - Contains action?                │
         │  - Not just hedging?               │
         │                                    │
         │  If NO → Use fallback              │
         └────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────────────────────────┐
         │  ✅ Actionable Guidance             │
         │  ✅ Clear next step                 │
         │  ✅ Guaranteed useful               │
         │                                    │
         │  {                                 │
         │    issue_type: "passive_voice",    │
         │    severity: "advisory",           │
         │    guidance: "...",                │
         │    action_required: "...",         │
         │    rewrite: "...",                 │
         │    method: "deterministic",        │
         │    confidence: "high"              │
         │  }                                 │
         └────────────────────────────────────┘
```

## Component Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│  ISSUE RESOLUTION ENGINE (issue_resolution_engine.py)           │
│  Role: Make ALL decisions                                       │
│                                                                 │
│  ✅ Classify issues deterministically                           │
│  ✅ Map to resolution classes                                   │
│  ✅ Provide deterministic fallbacks                             │
│  ✅ Validate output quality                                     │
│  ✅ Filter unmapped issues                                      │
│                                                                 │
│  ❌ Does NOT ask LLM what to do                                 │
│  ❌ Does NOT depend on RAG                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LLM PHRASING MODULE (llm_phrasing.py)                          │
│  Role: Phrase decisions (NOT make them)                         │
│                                                                 │
│  ✅ Adapt templates to specific content                         │
│  ✅ Maintain natural language flow                              │
│  ✅ Ensure consistent tone                                      │
│  ✅ Timeout protection (10s)                                    │
│  ✅ Automatic fallback on failure                               │
│                                                                 │
│  ❌ Does NOT decide what issue exists                           │
│  ❌ Does NOT decide how to fix                                  │
│  ❌ Does NOT invent structure                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DETERMINISTIC SUGGESTION GENERATOR (deterministic_suggestions) │
│  Role: Integrate and guarantee output                           │
│                                                                 │
│  ✅ Combine resolution engine + LLM + RAG                       │
│  ✅ RAG as enhancer (not dependency)                            │
│  ✅ Quality validation at every step                            │
│  ✅ Batch processing                                            │
│  ✅ Guaranteed actionable output                                │
│                                                                 │
│  ❌ Never returns vague suggestions                             │
│  ❌ Never fails to provide guidance                             │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Detail

```
Issue Detection (Existing Rules)
    │
    │  {'feedback': 'Avoid passive voice',
    │   'context': 'The file was opened.',
    │   'rule_id': 'passive_voice',
    │   'document_type': 'manual'}
    │
    ▼
Classify Issue
    │
    │  IssueType.PASSIVE_VOICE
    │
    ▼
Map to Resolution
    │
    │  ResolutionClass.REWRITE_ACTIVE
    │
    ▼
Get Template
    │
    │  ResolutionTemplate(
    │    fallback="Active voice is clearer...",
    │    action_required="Rewrite in active voice",
    │    template="This uses passive voice...",
    │  )
    │
    ▼
Try Enhancements (Parallel)
    │
    ├─► RAG (3s timeout)     ─► Example found? → Add to guidance
    │                          Timeout/fail? → Continue
    │
    └─► LLM (10s timeout)    ─► Good phrasing? → Use it
                               Timeout/fail? → Continue
    │
    ▼
Select Best
    │
    │  Priority: RAG > LLM > Fallback
    │
    ▼
Validate
    │
    │  Different? Has action? Not vague?
    │  NO → Use fallback
    │  YES → Use enhanced
    │
    ▼
Return
    │
    │  {
    │    issue_type: "passive_voice",
    │    severity: "advisory",
    │    resolution_class: "rewrite_active",
    │    guidance: "This sentence uses passive voice...",
    │    rewrite: "The system opens the file.",
    │    action_required: "Rewrite in active voice",
    │    method: "deterministic",
    │    confidence: "high"
    │  }
    │
    ▼
Display to User
    │
    │  Clear issue ✓
    │  Clear action ✓
    │  Clear next step ✓
```

## Failure Modes & Guarantees

```
┌─────────────────┬─────────────────┬──────────────────┐
│  Component      │  Failure Mode   │  Guarantee       │
├─────────────────┼─────────────────┼──────────────────┤
│  LLM            │  Timeout        │  Use fallback    │
│                 │  Error          │  Use fallback    │
│                 │  Vague output   │  Use fallback    │
├─────────────────┼─────────────────┼──────────────────┤
│  RAG            │  No results     │  Continue        │
│                 │  Timeout        │  Continue        │
│                 │  Error          │  Continue        │
├─────────────────┼─────────────────┼──────────────────┤
│  Classification │  Unmapped issue │  Return None     │
│                 │  Ambiguous      │  Return None     │
├─────────────────┼─────────────────┼──────────────────┤
│  Output         │  Any failure    │  Deterministic   │
│                 │                 │  fallback always │
│                 │                 │  works           │
└─────────────────┴─────────────────┴──────────────────┘

CORE GUARANTEE:
Every classified issue gets actionable guidance.
No classified issue returns vague or useless output.
```

## Issue Classification Decision Tree

```
Issue Detected
    │
    ├─► Contains 'passive'? ──────────► PASSIVE_VOICE
    │                                   └─► REWRITE_ACTIVE
    │
    ├─► Contains 'prerequisite'? ─────► MISSING_PREREQUISITE
    │                                   └─► ASK_FOR_PREREQUISITES
    │
    ├─► Contains 'long' + 'sentence'? ► LONG_SENTENCE
    │                                   └─► SIMPLIFY_SENTENCE
    │
    ├─► Contains 'vague' + term? ─────► VAGUE_TERM
    │                                   └─► REPLACE_WITH_SPECIFIC
    │
    ├─► Contains 'acronym'? ──────────► UNDEFINED_ACRONYM
    │                                   └─► DEFINE_ACRONYM
    │
    ├─► Contains 'terminology'? ──────► INCONSISTENT_TERMINOLOGY
    │                                   └─► STANDARDIZE_TERM
    │
    ├─► Contains 'mixed' + 'tense'? ──► MIXED_TENSE
    │                                   └─► UNIFY_TENSE
    │
    ├─► Contains 'dense' + 'step'? ───► DENSE_STEP
    │                                   └─► BREAK_INTO_STEPS
    │
    ├─► Contains 'order' + 'step'? ───► STEP_ORDER_PROBLEM
    │                                   └─► REORDER_GUIDANCE
    │
    ├─► Contains 'introduction'? ─────► MISSING_INTRODUCTION
    │                                   └─► ADD_INTRODUCTION
    │
    └─► No clean match? ──────────────► None (filter out)
```

## Quality Validation Flow

```
LLM Output Received
    │
    ▼
Is output non-empty?
    │
    ├─► NO ──► Use Fallback
    │
    └─► YES
        │
        ▼
    Is it different from original?
    (Similarity < 80%)
        │
        ├─► NO ──► Use Fallback
        │
        └─► YES
            │
            ▼
        Contains action words?
        (rewrite, replace, change, etc.)
            │
            ├─► NO ──► Use Fallback
            │
            └─► YES
                │
                ▼
            Only hedges without action?
            (consider/might without concrete step)
                │
                ├─► YES ──► Use Fallback
                │
                └─► NO
                    │
                    ▼
                ✅ Use LLM Output
```

## Summary

The architecture ensures:

1. **Decisions are deterministic** - Made in code, not by LLM
2. **Fallbacks are guaranteed** - Always useful output
3. **LLM role is narrow** - Only phrasing, never deciding
4. **RAG is optional** - Enhances but not required
5. **Quality is validated** - Multi-stage checks
6. **Unmapped issues filtered** - Only show what we can handle well

Result: **Consistent, actionable, reliable suggestions**
