# AI Rewrite Block Rule - Implementation Summary

**Date:** January 21, 2026  
**Status:** ✅ Implemented and tested

---

## Problem Statement

The system was allowing AI to rewrite sentences that combined:
- Normative language (`must`, `shall`, `required`)
- Conditional/alternative logic (`if`, `or`, `in case`)

This is **unsafe** because:
1. Changes normative strength (mandatory → ambiguous)
2. Collapses conditional logic (loses "if" clauses)
3. Removes technical precision (loses definitions)

**Example of unsafe rewrite:**

**Original:**
> "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."

**AI output (WRONG):**
> "Include the server's IP address in the SAN field or its registered FQDN."

**Problems:**
- ❌ Lost normative strength: "must include" → "Include"
- ❌ Lost conditional: "in case it is already registered" → implicit assumption
- ❌ Lost technical definition: "(Subject Alternative Name)" removed

---

## Solution: Hard Block Rule

### Policy Statement

> **AI must never rewrite sentences that combine normative language with conditional or alternative logic. These sentences require human judgment.**

### Implementation

**Location:** `app/intelligent_ai_improvement.py`

**Three pure functions:**

```python
def contains_normative_language(sentence: str) -> bool:
    """Detect mandatory requirements."""
    s = sentence.lower()
    return any(word in s for word in [
        " must ", " shall ", " required ", " mandatory ", " prohibited "
    ])

def contains_conditional_or_alternative(sentence: str) -> bool:
    """Detect conditional or alternative logic."""
    s = sentence.lower()
    return any(word in s for word in [
        " if ", " in case ", " unless ", " provided that ",
        " or ", " and/or ", " either ", " neither "
    ])

def blocks_ai_rewrite(sentence: str) -> bool:
    """Hard block rule."""
    return (
        contains_normative_language(sentence)
        and contains_conditional_or_alternative(sentence)
    )
```

**Enforcement points (TWO layers of protection):**

**Layer 1: Entry point check (PRIMARY - runs FIRST)**
```python
# Located at ~line 2228 in get_enhanced_ai_suggestion()
# Runs BEFORE pre-flight checks, BEFORE fallbacks, BEFORE AI attempts

if blocks_ai_rewrite(sentence_context):
    logger.warning("🛑 POLICY BLOCK: Normative + conditional sentence")
    return {
        "semantic_explanation": build_semantic_explanation_for_blocked_sentence(...),
        "is_semantic_explanation": True,
        "decision_type": "semantic_explanation",
        "block_reason": "normative_conditional"
    }
```

**Layer 2: Post-validation check (SAFETY NET)**
```python
# Located at ~line 2430
# Runs AFTER AI generates rewrite and validation passes, but BEFORE returning

if blocks_ai_rewrite(sentence_context):
    # Return semantic explanation instead
    return {
        "semantic_explanation": build_semantic_explanation_for_blocked_sentence(...),
        "is_semantic_explanation": True,
        "decision_type": "semantic_explanation"
    }
```

**Layer 3: Hard assertion (CATCH VIOLATIONS)**

Catches any bypass attempts:

```python
# Located at ~line 2440
if suggestion != sentence_context:
    assert not blocks_ai_rewrite(sentence_context), (
        "POLICY VIOLATION: AI rewrite for normative + conditional"
    )
```

---

## Test Results

All 6 test cases pass:

| Test | Sentence Type | Expected | Result |
|------|---------------|----------|--------|
| 1 | must + or/in case | BLOCKED | ✅ BLOCKED |
| 2 | should (not normative) | ALLOWED | ✅ ALLOWED |
| 3 | must (no conditional) | ALLOWED | ✅ ALLOWED |
| 4 | either/or (no normative) | ALLOWED | ✅ ALLOWED |
| 5 | shall + either/or/if | BLOCKED | ✅ BLOCKED |
| 6 | must + unless | BLOCKED | ✅ BLOCKED |

---

## What Happens When Blocked

Instead of showing an AI rewrite, the system returns:

**🧠 Semantic Explanation**

With content explaining:
1. Why the sentence is risky (normative + conditional)
2. What could go wrong (change compliance meaning, alter conditions)
3. What to consider if revising manually (checklist)

Example output:

> This sentence contains mandatory requirement language (must/shall/required). It includes conditional or alternative logic (if/or/in case) that creates multiple execution paths or options.
>
> Rewriting this sentence automatically could change its compliance meaning or alter the logical conditions. Even small word changes can shift requirement scope or change which conditions apply to which alternatives.
>
> **What to consider if revising manually:**
> - Does each condition apply to the correct alternative?
> - Is the normative strength (must/should/may) appropriate?
> - Are all technical terms defined or clear from context?
> - Does addressing 'passive voice' require structural change, or is the current structure necessary for accuracy?

---

## Global Application

This rule applies to **ALL issue types:**
- Passive voice
- Long sentence
- Wording/clarity
- Any future issue type

Cannot be bypassed by:
- Prompt engineering
- Model confidence
- Validation passing
- User preferences

---

## Documentation

**Architecture guardrails:** [ARCHITECTURE_GUARDRAILS.md](ARCHITECTURE_GUARDRAILS.md)  
Section: "Critical Policy Guardrails (Added January 21, 2026)"

**Test file:** [test_block_rule.py](test_block_rule.py)

---

## Design Principles

1. **False positives are acceptable** - Over-caution is safe
2. **False negatives are NOT acceptable** - Risk is unacceptable
3. **Understanding ≠ authority** - We explain, not prescribe
4. **Transparency over confidence** - Show why we're not rewriting

---

## Status

✅ **Implemented**  
✅ **Tested**  
✅ **Documented**  
✅ **Enforced at code level**

This guardrail is now non-bypassable.
