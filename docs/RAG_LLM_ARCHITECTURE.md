# RAG + LLM Architecture (No Hard-Coded Rules)

## Overview
The AI suggestion system now prioritizes **RAG (Retrieval-Augmented Generation) + LLM** over hard-coded pattern matching. This makes the system flexible, context-aware, and able to handle ANY passive voice pattern without manual coding.

## Architecture Flow

```
User Sentence (Passive Voice)
    ↓
PRIORITY 1: Document-First Search
    ├─ Search ChromaDB for relevant writing examples
    ├─ Find passive→active examples from YOUR uploaded docs
    └─ If found relevant context:
        ├─ Return context_documents[]
        └─ Pass to Priority 3 (Ollama)
    ↓
PRIORITY 3: Ollama with RAG Context
    ├─ Receive prepared context from Priority 1
    ├─ Build enhanced prompt with examples
    ├─ Ollama (phi3:mini) generates active voice rewrite
    ├─ Uses YOUR writing style from uploaded docs
    └─ Returns: Improved sentence + explanation
    ↓
Result: Context-aware AI suggestion (no hard-coded patterns!)
```

## Key Changes (November 11, 2025)

### 1. **Document-First Delegates to LLM**
**File**: `app/document_first_ai.py`, lines ~525-555

**Before** (Hard-coded):
```python
if "passive voice" in feedback_lower:
    # Try to match hard-coded patterns
    if "have been verified" in sentence:
        return "We verified..."  # Limited to this one pattern!
```

**After** (RAG-driven):
```python
if "passive voice" in feedback_lower:
    # Search for relevant examples
    relevant_docs = query_chromadb("passive voice examples")
    
    # Prepare context for LLM
    return {
        "success": False,  # Let LLM handle it
        "context_documents": relevant_docs  # Pass examples to Ollama
    }
```

### 2. **Ollama Enhanced with Prepared Context**
**File**: `app/intelligent_ai_improvement.py`, lines ~220-235

**Flow**:
1. Priority 1 searches documents → finds 5 relevant passive voice examples
2. Passes `context_documents[]` to Priority 3
3. Ollama receives examples in the prompt
4. Generates conversion based on YOUR style guide

**Benefits**:
- No need to code every pattern ("have been verified", "was configured", etc.)
- Adapts to YOUR writing style from uploaded documents
- Handles complex sentences with multiple passive constructions
- Can learn from new documents without code changes

### 3. **Enhanced Prompt with Issue-Specific Guidance**
**File**: `app/intelligent_ai_improvement.py`, lines ~990-1080

**New prompt structure**:
```
📋 ISSUE: Avoid passive voice
📝 ORIGINAL: "The test setups have been verified..."

📚 RELEVANT EXAMPLES from your uploaded docs:
Example 1: [Your style guide showing passive→active conversion]
Example 2: [Another example from your documents]

🎯 PASSIVE VOICE FIX INSTRUCTIONS:
- Identify who performs the action
- Make that the subject
- Use active verbs
- Examples: "Settings are configured" → "You configure settings"

Now rewrite: ...
```

## What You Upload

### Writing Style Guide (Example: `data/writing_style_guide.md`)
```markdown
## Passive Voice Examples

❌ BAD (Passive):
"The configuration was completed by the user."

✅ GOOD (Active):
"You completed the configuration."

---

❌ BAD (Passive):
"Test setups have been verified in the environment."

✅ GOOD (Active):
"We verified test setups in the environment."
```

### How It Works
1. **You upload** style guide with examples
2. **ChromaDB indexes** the content
3. **Priority 1 searches** for relevant examples when user hits "AI Suggestion"
4. **Ollama receives** your examples in the prompt
5. **Generates rewrite** following YOUR style

## Benefits of RAG + LLM vs Hard-Coded

| Aspect | Hard-Coded Rules | RAG + LLM |
|--------|------------------|-----------|
| **Flexibility** | Must code each pattern | Handles any pattern from examples |
| **Maintenance** | Add code for every new case | Upload more examples, no code change |
| **Context Awareness** | Generic conversions | Adapts to YOUR writing style |
| **Complex Sentences** | Often breaks or produces errors | LLM understands context and nuance |
| **Scalability** | Hundreds of if/else statements | Unlimited patterns via RAG |
| **User Control** | Developer must update code | Users upload their own style guides |

## Example Comparison

### Sentence:
> "The following test setups have been verified in the test environment defined above to achieve nominal performance (e.g., acceptable latency, zero data loss, etc.) and stable operation."

### Hard-Coded Approach:
```python
# Must manually handle each pattern
if "have been verified" in sentence:
    return "We verified the test setups..."  
# What about "has been verified"?
# What about "were verified"?
# What about "had been verified"?
# Need to code EVERY variation!
```

### RAG + LLM Approach:
```
1. Search: "passive voice examples active voice"
2. Found examples showing various passive→active patterns
3. Ollama prompt:
   - Original: "...have been verified..."
   - Example 1: "is configured" → "You configure"
   - Example 2: "was tested" → "We tested"
   - Example 3: "have been verified" → "We verified"
4. Ollama generates: "We verified the following test setups..."
```

**Result**: Works for ANY passive pattern without coding!

## Current Status

✅ **Implemented**:
- Document-first delegates to LLM with context
- Ollama accepts prepared context from Priority 1
- Enhanced prompts with issue-specific instructions
- RAG searches for relevant writing examples
- 14 documents in ChromaDB knowledge base

⚙️ **In Testing**:
- Ollama response quality (phi3:mini)
- Context relevance from RAG search
- Fallback behavior if Ollama times out

🔜 **Future Enhancements**:
- Fine-tune RAG search queries for better context
- Add more example documents to knowledge base
- Experiment with llama3:8b for complex sentences
- Implement caching for frequently converted patterns

## How to Add New Patterns

### Old Way (Hard-Coded):
1. Find the bug/pattern
2. Open `document_first_ai.py`
3. Add 50+ lines of regex and string manipulation
4. Test extensively
5. Deploy code update

### New Way (RAG + LLM):
1. Create a markdown file with examples
2. Upload via RAG interface: http://localhost:5000/rag/upload_knowledge
3. Done! System now handles that pattern

## Testing

To test the new RAG + LLM system:

1. **Upload a document** with the problematic sentence
2. **Click AI Suggestion**
3. **Watch Flask terminal** for logs:
   ```
   🔍 PRIORITY 1: Searching your 14 uploaded documents...
   📚 Document-first prepared 5 context docs for LLM
   🔍 PRIORITY 3: Ollama (with 14 documents, context prepared by document-first)...
   📚 Using 5 pre-prepared context documents from document-first
   ✅ Ollama provided suggestion
   ```

4. **Verify result** shows proper active voice conversion

## Troubleshooting

### Issue: Still using rule-based fallback
**Symptom**: Interface shows "intelligent_analysis" instead of "contextual_rag"
**Solution**: 
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Check RAG has documents: `curl http://localhost:5000/rag/stats`
- Enable detailed logging to see which priority failed

### Issue: Ollama timeout
**Symptom**: Logs show "⏱️ Ollama request timed out after 30s"
**Solution**:
- Increase timeout in `intelligent_ai_improvement.py` line 445
- Use smaller model: `phi3:mini` instead of `llama3:8b`
- Check Ollama resource usage

### Issue: Poor suggestions
**Symptom**: Ollama returns but suggestion is wrong/verbose
**Solution**:
- Upload more relevant examples to RAG
- Refine prompt in `_build_ollama_rag_prompt()`
- Try different model (llama3 vs phi3)

## Files Modified

| File | Lines | Purpose |
|------|-------|---------|
| `app/document_first_ai.py` | 525-555 | Delegate to LLM with context |
| `app/intelligent_ai_improvement.py` | 175-235 | Pass context from P1 to P3 |
| `app/intelligent_ai_improvement.py` | 400-500 | Accept prepared context |
| `app/intelligent_ai_improvement.py` | 990-1080 | Enhanced RAG prompt |
| `app/intelligent_ai_improvement.py` | 710-730 | Fix sentence splitting bug |

## Summary

**The system now uses RAG + LLM instead of hard-coded patterns!**

✅ Flexible - handles any passive voice pattern  
✅ Maintainable - no code changes for new patterns  
✅ Context-aware - uses YOUR writing style  
✅ Scalable - just upload more examples  
✅ User-controlled - upload your own style guides  

**Next step**: Test with various passive voice sentences and verify Ollama provides quality suggestions!
