# Sentence Split Eligibility System - Implementation Complete

## Overview

This document describes the complete implementation of the three-part sentence splitting eligibility system that determines **when AI should automatically split long sentences** and **when manual guidance is more appropriate**.

## Philosophy

> **AI should rewrite only when correctness is more important than completeness.**

The system prioritizes:
- **Safety over convenience** - False negatives are acceptable, false positives are not
- **Reviewer discipline** - Decisions are framed as "reviewer decided", never "AI failed"
- **Risk-based logic** - Conservative approach to protect meaning

---

## The Three-Tier Decision System

### 1. **ALWAYS SPLIT** - Low-risk, high-reward
Sentences that should **always** be auto-split:
- Descriptive process chains (X does A and B and C and D)
- Explanation + consequence patterns (X does Y, which results in Z)
- Long introductory/descriptive sentences

**Characteristics:**
- No conditionals (if, unless, when)
- No normative language (must, shall, required)
- Clear sequential actions
- Safe to split without manual review

**Example:**
> "The cache stores frequently accessed responses in memory, which significantly improves system performance and reduces database load during peak usage times."

**Decision:** `always_split` → Auto-rewrite immediately

---

### 2. **ELIGIBLE SPLIT** - Safe to attempt
Sentences that are safe for AI to split:
- Simple conjunctions with "and"
- Temporal connectors (before, after, then)
- No high-risk elements present

**Characteristics:**
- Safe connectors present
- No conditional logic
- No compliance language
- Medium complexity

**Example:**
> "The system validates the input data and then processes the transaction and finally generates a confirmation receipt for the user."

**Decision:** `eligible_split` → AI provides suggestion

---

### 3. **GUIDANCE ONLY** - Manual review required
Sentences with high semantic risk:
- Conditional logic (if, in case, unless, when)
- Logical alternatives (or, either, neither)
- Normative/compliance statements (must, shall, required)
- Technical parentheticals (SAN, i.e., e.g.)

**Characteristics:**
- Conditions that could break if split
- Legal/compliance implications
- Technical definitions that bind tightly
- Multiple obligations or alternatives

**Example:**
> "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."

**Decision:** `guidance_only` → Provide manual guidance, no auto-split

---

## Implementation Files

### Core Module: `sentence_split_eligibility.py`
Location: `d:\doc-scanner\app\rules\sentence_split_eligibility.py`

**Key Functions:**

1. **`can_split_long_sentence(sentence) -> (bool, str)`**
   - Returns `True` if safe to split (no blockers present)
   - Checks for conditionals, logical alternatives, normative language, parentheticals
   - Conservative by design

2. **`always_split_long_sentence(sentence) -> (bool, str)`**
   - Returns `True` for low-risk, high-reward categories
   - Identifies process chains, consequence clauses, long intros
   - Only returns True if sentence is 20+ words AND no risk factors

3. **`get_split_decision(sentence) -> (str, str)`**
   - Master function that returns: `"always_split"`, `"eligible_split"`, or `"guidance_only"`
   - Used by AI engines to make split decisions

4. **`get_ui_message(decision, word_count) -> dict`**
   - Returns reviewer-centric UI messaging
   - No "AI failed" language - always "reviewer decided"

---

### Integration Points

#### 1. `intelligent_ai_improvement.py`
**Function:** `should_attempt_rewrite()`
- Uses `get_split_decision()` to determine if AI should attempt rewrite
- Respects eligibility decisions for long sentences

#### 2. `ai_improvement.py`
**Function:** `_generate_smart_suggestion()`
- Checks eligibility before attempting sentence split
- Returns guidance-only for risky sentences
- Includes decision metadata in response

#### 3. `index.html` (UI Template)
- Updated to show reviewer-centric language
- Different styling for guidance vs suggestions
- Icons and titles reflect intentional decisions

---

## Decision Matrix

| Risk Factor | ALWAYS | ELIGIBLE | GUIDANCE |
|-------------|--------|----------|----------|
| Conditionals (if, unless, when) | ❌ | ❌ | ✅ |
| Logical OR/AND | ❌ | ❌ | ✅ |
| Normative (must, shall) | ❌ | ⚠️ | ✅ |
| Technical parentheticals | ❌ | ❌ | ✅ |
| Process chain (3+ "and") | ✅ | | |
| "which" clause | ✅ | | |
| Simple "and" connector | | ✅ | |
| Temporal connectors | | ✅ | |

---

## UI Messaging Framework

### Principle
> **Never imply AI "failed". Always imply reviewer "decided".**

### Message Types

**ALWAYS_SPLIT:**
- Title: "✅ Suggested rewrite (reviewer-approved)"
- Explanation: "This sentence was split to improve readability while preserving meaning."
- Styling: Green checkmark, success indicator

**ELIGIBLE_SPLIT:**
- Title: "💡 AI Suggestion"
- Explanation: "This sentence can be split into shorter sentences for better readability."
- Styling: Info icon, suggestion indicator

**GUIDANCE_ONLY:**
- Title: "📋 Reviewer Guidance"
- Explanation: "This sentence contains complex logic that requires careful manual review."
- Details: "Splitting it automatically could change its meaning."
- Recommendation: Step-by-step manual splitting guidance
- Styling: Info badge, guidance indicator

---

## Test Coverage

**Test Suite:** `tests/test_sentence_split_eligibility.py`

**Coverage:**
- ✅ 9/9 tests passing (100%)
- Group 1: Guidance only (4 tests) - Complex sentences
- Group 2: Always split (3 tests) - Safe categories
- Group 3: Eligible split (2 tests) - Medium complexity
- Group 4: UI messaging verification

**Run tests:**
```powershell
python tests\test_sentence_split_eligibility.py
```

---

## Real-World Examples

### Example 1: Safe to Auto-Split ✅
**Input:**
> "This section provides information on how to transfer an IE app from the IE Hub to the IEM catalog of one or more IEM instances."

**Decision:** `always_split` (Long introductory sentence)

**Output:**
> "This section provides information. It explains how to transfer an IE app from the IE Hub to the IEM catalog of one or more IEM instances."

**UI:** "✅ Suggested rewrite (reviewer-approved)"

---

### Example 2: Risky - Guidance Only ⚠️
**Input:**
> "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."

**Decision:** `guidance_only` (Conditional logic + technical parenthetical)

**Output:** [Original unchanged]

**UI:** "📋 Reviewer Guidance: This sentence contains complex logic that requires careful manual review. Split it manually into one sentence for the requirement and one for the condition."

---

### Example 3: Eligible for AI Split 💡
**Input:**
> "The application processes incoming requests and validates user credentials before forwarding data to the backend service."

**Decision:** `eligible_split` (Safe connectors)

**Output:**
> "The application processes incoming requests. It validates user credentials before forwarding data to the backend service."

**UI:** "💡 AI Suggestion"

---

## Benefits

1. **User Trust** - Intentional restraint builds confidence
2. **Accuracy** - Conservative approach prevents meaning corruption
3. **Clarity** - Users understand why decisions were made
4. **Flexibility** - Three-tier system handles different risk levels
5. **Transparency** - Decision reasons are logged and shown

---

## Key Principles (Lock These In)

1. ✅ **AI rewrites only when correctness > convenience**
2. ✅ **Conservative: false negatives acceptable, false positives not**
3. ✅ **UI says "reviewer decided", never "AI failed"**
4. ✅ **Three-tier system: always/eligible/guidance**
5. ✅ **Risk-based logic, not NLP cleverness**

---

## Usage in Code

```python
from app.rules.sentence_split_eligibility import get_split_decision, get_ui_message

# Determine if sentence should be split
sentence = "The server certificate must include..."
decision, reason = get_split_decision(sentence)

# decision will be: "always_split", "eligible_split", or "guidance_only"
# reason explains why

# Get UI messaging
word_count = len(sentence.split())
ui_msg = get_ui_message(decision, word_count)

# ui_msg contains:
# - title: Display title
# - explanation: Why this decision was made
# - recommendation: (guidance_only only) Step-by-step advice
# - action_label: Button/badge text
```

---

## Future Enhancements

Potential improvements (not yet implemented):
1. User preference overrides (allow aggressive splitting mode)
2. Learning from manual edits (track which guidance led to successful splits)
3. Domain-specific rules (medical vs legal vs technical)
4. Confidence scoring for borderline cases

---

## Maintenance

**When to update:**
- New risk patterns discovered
- User feedback on incorrect decisions
- Changes to style guide requirements

**What to test:**
- Run full test suite after any changes
- Add new test cases for edge cases
- Verify UI messaging still feels intentional

---

## Conclusion

This system transforms sentence splitting from an "AI limitation" into **editorial judgment**.

The restraint is the feature, not a bug.

---

*Implementation completed: January 21, 2026*
*All tests passing: ✅ 9/9 (100%)*
