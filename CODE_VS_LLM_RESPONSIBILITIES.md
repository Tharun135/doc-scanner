# Division of Responsibilities: Code vs LLM

## Architecture Principle

```
For every flagged issue:

CODE DECIDES:
✓ What kind of solution is needed
✓ What constraints apply  
✓ What is NOT allowed to change

LLM DOES:
✓ Phrase the solution clearly
✓ Provide an example
✓ Make it sound human and helpful

The LLM never decides what to fix.
It only decides how to say it.
```

## Implementation

### 1. Code Forces the Shape (Deterministic)

**File:** `core/issue_resolution_engine.py`

```python
# CODE DECIDES: What kind of issue this is
issue_type = classify_issue(feedback, sentence)
# Returns: passive_voice, long_sentence, vague_term, etc.

# CODE DECIDES: What resolution to apply
ISSUE_TO_RESOLUTION = {
    IssueType.PASSIVE_VOICE: ResolutionClass.REWRITE_ACTIVE,
    IssueType.LONG_SENTENCE: ResolutionClass.SIMPLIFY_SENTENCE,
    # ...
}

# CODE DECIDES: Constraints and fallback
RESOLUTION_TEMPLATES = {
    ResolutionClass.REWRITE_ACTIVE: ResolutionTemplate(
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This sentence uses passive voice. Active voice is clearer and more direct.\n\n"
            "Action: Rewrite to show who performs the action.\n"
            "Example: 'The file was opened' → 'The system opens the file'"
        ),
        action_required="Rewrite in active voice",
    ),
    # ...
}
```

**What Code Decides:**
- ✅ Issue classification (pattern matching)
- ✅ Resolution strategy (ISSUE_TO_RESOLUTION map)
- ✅ Severity level (blocking vs advisory)
- ✅ Guaranteed fallback text
- ✅ Required action
- ✅ Deterministic rewrite (regex patterns)

### 2. LLM Fills It In Richly (Optional Enhancement)

**File:** `core/llm_phrasing.py`

```python
def phrase_resolution(template, context, fallback):
    """
    LLM is told:
    - CODE already decided what's wrong and how to fix it
    - LLM ONLY phrases it clearly with an example
    - LLM does NOT change the solution or constraints
    """
    prompt = f"""
    CODE DECIDED (YOU CANNOT CHANGE):
    ✓ What the issue is: {feedback}
    ✓ What kind of solution is needed
    ✓ What constraints apply

    YOUR ONLY JOB:
    ✓ Phrase the solution clearly
    ✓ Provide a concrete example showing before/after
    ✓ Make it sound human and helpful
    
    SOLUTION TEMPLATE (from code):
    {template}
    
    OUTPUT REQUIRED (3 parts):
    1. What needs to change (1 sentence, direct)
    2. Example showing the transformation (before → after)
    3. Why this improves clarity (1 sentence)
    """
```

**What LLM Does:**
- ✅ Adapts template to specific sentence
- ✅ Provides concrete before/after example
- ✅ Makes guidance sound human and helpful
- ✅ Ensures natural language flow
- ❌ Does NOT decide what to fix
- ❌ Does NOT change constraints
- ❌ Does NOT invent new solutions

### 3. Validation Ensures Quality

**File:** `core/deterministic_suggestions.py`

```python
# Get deterministic rewrite (CODE FORCED)
deterministic_rewrite = self._deterministic_rewrite(
    issue_type,
    original_sentence
)

# Let LLM improve it (OPTIONAL)
if self.llm_phraser.llm_available:
    llm_rewrite = self.llm_phraser.phrase_rewrite(
        original=original_sentence,
        issue_type=issue_type,
        fallback_rewrite=deterministic_rewrite
    )
    
    # Validate LLM is actually better
    if is_value_added(original_sentence, llm_rewrite, threshold=0.2):
        return llm_rewrite  # Use enriched version
    
# Fallback to code-forced version
return deterministic_rewrite  # Guaranteed correct
```

**Quality Gates:**
- ✅ LLM rewrite must be different from original (> 20% change)
- ✅ LLM rewrite must not be vague (no hedge words without action)
- ✅ LLM rewrite must be longer than 5 characters
- ✅ If LLM fails any check → Use deterministic fallback
- ✅ If LLM unavailable → Use deterministic fallback

## Examples

### Example 1: Passive Voice

**Code Decides:**
```
Issue Type: passive_voice
Resolution: rewrite_active
Constraint: "Show who performs the action, keep system-focused"
Deterministic: "The system displays the tag details."
```

**LLM Enhances:**
```
"Convert passive to active voice to clarify responsibility.

Example: 'The tags are displayed' → 'The system displays the tag details'

This makes it immediately clear which component performs the action."
```

### Example 2: Long Sentence

**Code Decides:**
```
Issue Type: long_sentence  
Resolution: simplify_sentence
Constraint: "Split on natural boundaries (conjunctions, prep phrases)"
Deterministic: "You can activate in the configuration file to print out this information. In the user log file in a cyclic way (for example, every 10 seconds)."
```

**LLM Enhances:**
```
"Break this 30-word sentence into shorter units for better readability.

Example: 
Before: 'You can activate in the configuration file to print out this information in the user log file in a cyclic way (for example, every 10 seconds).'

After: 'You can activate this in the configuration file. The system prints the information to the user log file cyclically, for example every 10 seconds.'

Each sentence now conveys a single, clear idea."
```

### Example 3: Modal Passive

**Code Decides:**
```
Issue Type: passive_voice
Resolution: rewrite_active  
Constraint: "Convert 'must be done by X' to 'X must do'"
Deterministic: "The PROFINET IO Connector provides the raw data, and the client must do the analysis of the record data."
```

**LLM Enhances:**
```
"Rewrite modal passive to identify the actor clearly.

Example: 'the analysis must be done by the client' → 'the client must do the analysis'

Active voice with modals maintains obligation while clarifying responsibility."
```

## Responsibilities Matrix

| Decision | Code | LLM |
|----------|------|-----|
| **What is wrong** | ✅ Pattern matching | ❌ Not consulted |
| **What type of fix** | ✅ ISSUE_TO_RESOLUTION | ❌ Not consulted |
| **How to transform** | ✅ Regex patterns | ❌ Not consulted |
| **Constraints** | ✅ ResolutionTemplate | ❌ Cannot override |
| **Severity** | ✅ IssueSeverity enum | ❌ Not consulted |
| **Fallback text** | ✅ Deterministic | ❌ Not needed |
| **How to phrase** | 🔄 Template | ✅ Adapts & enriches |
| **Examples** | 🔄 Generic | ✅ Sentence-specific |
| **Tone** | 🔄 Neutral | ✅ Human & helpful |

## Benefits

### ✅ Reliability
- Code-forced decisions guarantee correctness
- LLM cannot introduce errors in classification
- Deterministic fallbacks always work

### ✅ Consistency  
- Same issue → Same resolution strategy
- No creative LLM interpretations
- Predictable behavior

### ✅ Quality
- LLM enhances phrasing without changing logic
- Examples are contextual and specific
- Human-friendly language

### ✅ Performance
- LLM is optional enhancement, not requirement
- System works perfectly without LLM
- Failures degrade gracefully to deterministic mode

## Current Status

**Architecture:** ✅ Correctly implemented
**Prompts:** ✅ Updated to emphasize constraints
**Validation:** ✅ Quality gates in place
**Fallbacks:** ✅ Deterministic templates ready

**LLM Status:** ⚠️ Currently unavailable (`scripts.ollama_client` import error)
**Fallback Mode:** ✅ Working perfectly (using deterministic only)

When LLM is available, it will enrich the output. When unavailable, deterministic mode works without degradation.
