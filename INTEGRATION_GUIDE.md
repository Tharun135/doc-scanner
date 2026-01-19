# Integration Guide: Deterministic Suggestion System

## Overview

This guide shows how to integrate the new deterministic suggestion system into the existing document scanner.

## Architecture Change

### Before (Problem)

```
Issue Detected
    ↓
Ask LLM: "What should I do about this?"
    ↓
LLM tries to figure it out (often fails)
    ↓
Vague or useless suggestion
```

### After (Solution)

```
Issue Detected
    ↓
Classify deterministically → Resolution Class
    ↓
Get deterministic template + fallback
    ↓
Try RAG enhancement (optional)
    ↓
Try LLM phrasing (optional)
    ↓
Validate quality
    ↓
Return fallback if quality insufficient
    ↓
Actionable guidance (guaranteed)
```

## Key Files Created

1. **`core/issue_resolution_engine.py`**
   - Issue → Resolution Class mapping
   - Deterministic templates
   - Fallback responses
   - Quality validation

2. **`core/llm_phrasing.py`**
   - Narrow LLM role (phrasing only)
   - Timeout and error handling
   - Automatic fallback

3. **`core/deterministic_suggestions.py`**
   - Main integration point
   - Combines resolution engine + LLM phraser + RAG
   - Batch processing
   - Guaranteed actionable output

4. **`ISSUE_CLASSIFICATION_REFERENCE.md`**
   - Documents all 10 issues
   - Shows resolution classes
   - Defines LLM usage

5. **`test_deterministic_system.py`**
   - Demonstrates the system
   - Tests all issue types
   - Shows filtering behavior

## Integration Steps

### Step 1: Update AI Improvement Module

Modify `app/ai_improvement.py` to use the deterministic system:

```python
from core.deterministic_suggestions import generate_suggestion_for_issue

def generate_contextual_suggestion(
    self,
    feedback_text: str,
    sentence_context: str = "",
    document_type: str = "general",
    writing_goals: Optional[List[str]] = None,
    document_content: str = "",
    option_number: int = 1,
    issue: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate suggestion using deterministic system."""
    
    # Build issue data
    issue_data = {
        'feedback': feedback_text,
        'context': sentence_context,
        'rule_id': issue.get('rule_id', '') if issue else '',
        'document_type': document_type,
    }
    
    # Use deterministic suggestion generator
    suggestion = generate_suggestion_for_issue(issue_data)
    
    if not suggestion:
        # Issue doesn't map cleanly - skip it
        return None
    
    # Convert to expected format
    return {
        'suggestion': suggestion.get('rewrite', sentence_context),
        'ai_answer': suggestion['guidance'],
        'confidence': suggestion['confidence'],
        'method': suggestion['method'],
        'severity': suggestion['severity'],
        'action_required': suggestion['action_required'],
    }
```

### Step 2: Update Routes

Modify `app/routes.py` to filter out unmapped issues:

```python
from core.deterministic_suggestions import generate_suggestions_for_issues

@app.route('/analyze', methods=['POST'])
def analyze_document():
    """Analyze document with deterministic suggestions."""
    
    # ... existing code to detect issues ...
    
    # Generate suggestions using deterministic system
    suggestions = generate_suggestions_for_issues(detected_issues)
    
    # Separate blocking vs advisory
    blocking = [s for s in suggestions if s['severity'] == 'blocking']
    advisory = [s for s in suggestions if s['severity'] == 'advisory']
    
    return jsonify({
        'blocking_issues': blocking,
        'advisory_suggestions': advisory,
        'total_issues': len(detected_issues),
        'actionable_suggestions': len(suggestions),
        'filtered_out': len(detected_issues) - len(suggestions),
    })
```

### Step 3: Update Rule Helpers

Modify rule detection to include classification hints:

```python
# In app/rules/passive_voice.py
def check(content):
    suggestions = []
    
    # ... existing detection logic ...
    
    for passive_instance in detected_passives:
        suggestions.append({
            'feedback': 'Avoid passive voice',
            'context': sentence_text,
            'rule_id': 'passive_voice',  # ← Important for classification
            'position': position,
        })
    
    return suggestions
```

### Step 4: Add Severity to UI

Update frontend to show blocking vs advisory:

```javascript
// Show blocking issues prominently
if (issue.severity === 'blocking') {
    showBlockingIssue(issue);
} else {
    showAdvisorySuggestion(issue);
}

// Display action required
if (issue.action_required) {
    showActionButton(issue.action_required);
}
```

## Configuration

### Enable/Disable Components

```python
# In core/deterministic_suggestions.py

class DeterministicSuggestionGenerator:
    def __init__(self, use_llm=True, use_rag=True):
        self.use_llm = use_llm
        self.use_rag = use_rag
        # ...
```

### Adjust Quality Thresholds

```python
# In core/issue_resolution_engine.py

RESOLUTION_TEMPLATES = {
    ResolutionClass.REWRITE_ACTIVE: ResolutionTemplate(
        # ...
        value_threshold=0.3,  # Adjust this
    ),
}
```

### Add Custom Issues

To add a new issue type:

1. Add to `IssueType` enum
2. Add to `ResolutionClass` enum if needed
3. Add mapping to `ISSUE_TO_RESOLUTION`
4. Add template to `RESOLUTION_TEMPLATES`
5. Add severity to `ISSUE_SEVERITY`

Example:

```python
# 1. Add issue type
class IssueType(Enum):
    # ... existing ...
    MISSING_EXAMPLE = "missing_example"

# 2. Add resolution class
class ResolutionClass(Enum):
    # ... existing ...
    ADD_EXAMPLE = "add_example"

# 3. Map issue to resolution
ISSUE_TO_RESOLUTION = {
    # ... existing ...
    IssueType.MISSING_EXAMPLE: ResolutionClass.ADD_EXAMPLE,
}

# 4. Add template
RESOLUTION_TEMPLATES = {
    # ... existing ...
    ResolutionClass.ADD_EXAMPLE: ResolutionTemplate(
        resolution_class=ResolutionClass.ADD_EXAMPLE,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This instruction lacks an example.\n\n"
            "Action: Add a concrete example showing the expected result.\n"
            "Example: 'Enter your email' → 'Enter your email (e.g., user@example.com)'"
        ),
        action_required="Add example",
        explanation_template="...",
    ),
}

# 5. Add severity
ISSUE_SEVERITY = {
    # ... existing ...
    IssueType.MISSING_EXAMPLE: IssueSeverity.ADVISORY,
}
```

## Testing

### Run Test Suite

```bash
python test_deterministic_system.py
```

Expected output:
- 10 issue types tested
- Deterministic classification working
- Fallbacks functioning
- Unmapped issues filtered
- All suggestions actionable

### Test Individual Issue

```python
from core.deterministic_suggestions import generate_suggestion_for_issue

issue = {
    'feedback': 'Avoid passive voice',
    'context': 'The file was opened.',
    'rule_id': 'passive_voice',
    'document_type': 'manual',
}

suggestion = generate_suggestion_for_issue(issue)
print(suggestion['guidance'])
```

### Test Without AI

Disable LLM and RAG to test pure deterministic mode:

```python
from core.deterministic_suggestions import DeterministicSuggestionGenerator

# Pure deterministic mode
generator = DeterministicSuggestionGenerator()
generator.llm_phraser.llm_available = False
generator.rag_available = False

suggestion = generator.generate_suggestion(issue)
# Should still produce actionable guidance using fallback
```

## Benefits

### Before Integration

- ❌ LLM decides what to do (often fails)
- ❌ Weak ChromaDB hurts quality
- ❌ Conservative model produces vague output
- ❌ No guarantees about usefulness
- ❌ Users ask "okay, but what should I do?"

### After Integration

- ✅ Code decides what to do (always works)
- ✅ Weak ChromaDB doesn't matter (optional enhancement)
- ✅ Conservative model only phrases (narrow role)
- ✅ Guaranteed actionable guidance
- ✅ Users know exactly what to do

## Monitoring

Track suggestion quality:

```python
from core.deterministic_suggestions import generate_suggestions_for_issues

def analyze_with_monitoring(issues):
    suggestions = generate_suggestions_for_issues(issues)
    
    # Track methods used
    methods = {
        'deterministic': 0,
        'llm_phrased': 0,
        'rag_enhanced': 0,
    }
    
    for s in suggestions:
        methods[s['method']] += 1
    
    print(f"Deterministic: {methods['deterministic']}")
    print(f"LLM Phrased: {methods['llm_phrased']}")
    print(f"RAG Enhanced: {methods['rag_enhanced']}")
    
    # Track filtering
    filtered = len(issues) - len(suggestions)
    print(f"Filtered unmapped: {filtered}")
    
    return suggestions
```

## Rollback Plan

If issues arise, easy rollback:

1. Keep old `ai_improvement.py` as `ai_improvement_legacy.py`
2. Switch import in routes:
   ```python
   # New system
   from core.deterministic_suggestions import generate_suggestion_for_issue
   
   # Rollback
   from app.ai_improvement_legacy import AISuggestionEngine
   ```

## Next Steps

1. ✅ Test system with `python test_deterministic_system.py`
2. ✅ Integrate into routes
3. ✅ Update UI to show severity
4. ✅ Monitor suggestion quality
5. ✅ Iterate on templates based on user feedback

## Support

Issues? Check:

1. **Unmapped issues** - Are they being filtered correctly?
2. **Fallback usage** - Is deterministic mode working?
3. **LLM timeout** - Is LLM responding in <10 seconds?
4. **RAG enhancement** - Is ChromaDB accessible?

All components are designed to fail gracefully and fall back to deterministic guidance.
