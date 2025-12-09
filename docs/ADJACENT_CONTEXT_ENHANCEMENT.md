# Adjacent Context Enhancement for AI Suggestions

## 🎯 Overview

This enhancement adds **adjacent sentence context** to the AI suggestion system, enabling the LLM to generate more contextually appropriate suggestions by understanding the surrounding sentences.

## ❓ Problem Statement

Previously, the AI system analyzed sentences in isolation without considering their context. This led to issues like:

### Example Issue:
**Context:**
- Previous sentence: "The following requirement must be met:"
- Current sentence: "Access to the IED on which the IE app is installed."
- Issue: Passive voice detected

**Old AI Suggestion (without context):**
"You access the IED where the IE app installs it."

**Problem:** The AI converted a requirement statement into a description, losing the requirement context.

**New AI Suggestion (with adjacent context):**
"You must have access to the IED on which the IE app is installed."

**Improvement:** The AI now understands it's a requirement (from the previous sentence) and maintains that style.

## ✨ What Changed

### 1. **Backend Changes**

#### `app/app.py`
- Added `current_sentences_list` global variable to store all sentences from the uploaded document
- Modified `/ai_suggestion` endpoint to extract adjacent sentences based on `sentence_index`
- Passes `adjacent_context` dictionary containing `previous_sentence` and `next_sentence` to AI functions

#### `app/intelligent_ai_improvement.py`
- Updated `generate_contextual_suggestion()` to accept `adjacent_context` parameter
- Updated `_generate_ollama_rag_suggestion()` to accept and use adjacent context
- Enhanced `_build_ollama_rag_prompt()` to include adjacent context in the prompt
- Modified all prompt templates (passive voice, long sentences, adverbs) to leverage adjacent context

#### `app/hybrid_intelligence_integration.py`
- Updated `enhance_ai_suggestion_with_hybrid_intelligence()` to accept `adjacent_context` parameter
- Enhanced hybrid intelligence to use surrounding context for better suggestions

### 2. **Prompt Enhancements**

All AI prompts now include a **"SENTENCE CONTEXT"** section:

```
📖 SENTENCE CONTEXT (Adjacent Sentences):
PREVIOUS SENTENCE: "The following requirement must be met:"
CURRENT SENTENCE (to improve): "Access to the IED on which the IE app is installed."
NEXT SENTENCE: "This allows remote monitoring."

💡 Use this context to understand the sentence's purpose and maintain consistency.
```

### 3. **Context-Aware Instructions**

Enhanced prompts include specific instructions to:
- Check if the previous sentence is a heading (e.g., "Requirements:", "Prerequisites:")
- Maintain requirement style when appropriate
- Convert to imperative form under "Steps" sections
- Use appropriate subjects based on context (system vs. user actions)
- Preserve the sentence type (requirement, instruction, description)

## 🚀 How It Works

### Flow Diagram

```
1. User uploads document
   └─> Extract all sentences → Store in current_sentences_list

2. User requests AI suggestion for sentence N
   └─> Extract sentence_index from request
   └─> Get adjacent_context:
       ├─> previous_sentence = current_sentences_list[N-1]
       └─> next_sentence = current_sentences_list[N+1]

3. Pass to AI suggestion system
   └─> Build enhanced prompt with:
       ├─> Original issue and sentence
       ├─> Adjacent sentences context
       └─> RAG knowledge base examples

4. LLM generates context-aware suggestion
   └─> Returns improved sentence that fits the context
```

## 📝 Usage Example

### API Request

```javascript
POST /ai_suggestion
{
  "feedback": "Avoid passive voice - consider using active voice",
  "sentence": "Access to the IED on which the IE app is installed.",
  "sentence_index": 5,  // NEW: Include sentence position
  "document_type": "technical",
  "writing_goals": ["clarity", "directness"]
}
```

### Backend Processing

```python
# Extract adjacent context
adjacent_context = {}
if sentence_index > 0:
    adjacent_context['previous_sentence'] = current_sentences_list[sentence_index - 1].text

if sentence_index < len(current_sentences_list) - 1:
    adjacent_context['next_sentence'] = current_sentences_list[sentence_index + 1].text

# Pass to AI system
result = get_enhanced_ai_suggestion(
    feedback_text=feedback_text,
    sentence_context=sentence_context,
    adjacent_context=adjacent_context  # Include adjacent context
)
```

### Enhanced Prompt

The LLM receives:
```
📋 ISSUE: Passive voice detected
📝 ORIGINAL: "Access to the IED on which the IE app is installed."

📖 SENTENCE CONTEXT (Adjacent Sentences):
PREVIOUS SENTENCE: "The following requirement must be met:"
CURRENT SENTENCE (to improve): "Access to the IED on which the IE app is installed."
NEXT SENTENCE: ""

🎯 YOUR TASK: Convert this passive sentence to clear, direct active voice.

✅ CONVERSION RULES:
1. **Consider the context**: Look at the adjacent sentences to understand if this is:
   - A requirement/prerequisite (e.g., "The following requirement must be met:")
   - A descriptive statement
   - An instruction/action item
2. Identify who/what performs the action
3. **Preserve the sentence type**: If it's a heading or requirement, keep it as such
...
```

## 🎯 Benefits

### 1. **Context-Aware Suggestions**
- AI understands if a sentence is a requirement, instruction, or description
- Maintains appropriate tone and style based on surrounding text

### 2. **Better Requirement Handling**
- Recognizes requirement patterns from previous sentences
- Keeps requirement statements as requirements (not descriptions)

### 3. **Improved Flow**
- Suggestions maintain consistency with adjacent sentences
- Transitions and connections are preserved

### 4. **Type-Specific Conversion**
- Requirements → "You must..."
- Instructions → Imperative form
- Descriptions → Appropriate subject (system/user)

## 🔧 Technical Details

### Data Flow

```python
# app/app.py - Store sentences globally
current_sentences_list = []  # All sentences from document

# app/app.py - Extract adjacent context in /ai_suggestion endpoint
adjacent_context = {}
if sentence_index > 0:
    adjacent_context['previous_sentence'] = current_sentences_list[sentence_index - 1].text
if sentence_index < len(current_sentences_list) - 1:
    adjacent_context['next_sentence'] = current_sentences_list[sentence_index + 1].text

# app/intelligent_ai_improvement.py - Pass through to prompt builder
def _build_ollama_rag_prompt(..., adjacent_context=None):
    if adjacent_context:
        adjacent_section = "\n📖 SENTENCE CONTEXT (Adjacent Sentences):\n"
        if adjacent_context.get('previous_sentence'):
            adjacent_section += f"PREVIOUS SENTENCE: \"{adjacent_context['previous_sentence']}\"\n"
        adjacent_section += f"CURRENT SENTENCE (to improve): \"{sentence_context}\"\n"
        if adjacent_context.get('next_sentence'):
            adjacent_section += f"NEXT SENTENCE: \"{adjacent_context['next_sentence']}\"\n"
```

## 🧪 Testing

### Test Case 1: Requirement Context
**Input:**
- Previous: "The following requirement must be met:"
- Current: "Access to the IED on which the IE app is installed."
- Issue: Passive voice

**Expected:** Maintain requirement style
**Result:** ✅ "You must have access to the IED on which the IE app is installed."

### Test Case 2: Instruction Context
**Input:**
- Previous: "Follow these steps:"
- Current: "The configuration is saved."
- Issue: Passive voice

**Expected:** Convert to imperative
**Result:** ✅ "Save the configuration."

### Test Case 3: Description Context
**Input:**
- Previous: "The system operates as follows:"
- Current: "Data is displayed in the dashboard."
- Issue: Passive voice

**Expected:** Use system as subject
**Result:** ✅ "The system displays data in the dashboard."

## 🔮 Future Enhancements

1. **Extended Context Window**
   - Include 2-3 sentences before and after
   - Analyze paragraph structure

2. **Section Awareness**
   - Detect section headers (Requirements, Steps, Overview)
   - Apply section-specific rules automatically

3. **Document Type Learning**
   - Learn patterns from document type
   - Apply style consistently across document

4. **Smart Context Selection**
   - Only include relevant adjacent sentences
   - Skip irrelevant filler sentences

## 📊 Performance Impact

- **Minimal overhead**: Only extracting sentences already parsed
- **No additional API calls**: Context passed in single prompt
- **Better quality**: Fewer regeneration requests due to context-aware suggestions

## ✅ Conclusion

The adjacent context enhancement significantly improves AI suggestion quality by providing the LLM with surrounding sentence context. This enables more appropriate, context-aware suggestions that maintain the original intent and style of the document.

## 📚 Related Files

- `app/app.py` - Endpoint modifications and context extraction
- `app/intelligent_ai_improvement.py` - AI suggestion system with context support
- `app/hybrid_intelligence_integration.py` - Hybrid intelligence with context
- `docs/ADJACENT_CONTEXT_ENHANCEMENT.md` - This document
