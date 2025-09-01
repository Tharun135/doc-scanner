# Doc-Scanner AI Rewriter Integration

This document explains how to use the newly integrated AI-powered document rewriting feature in doc-scanner. The rewriting functionality has been seamlessly integrated into the existing application **without changing the UI**, providing intelligent document improvement capabilities.

## 🚀 Quick Start

The rewriter is automatically available once the application is running. No additional setup is required beyond ensuring Ollama is running locally.

### Prerequisites
- Ollama running locally (default: http://localhost:11434)
- Recommended models: `phi3:mini`, `llama3:8b`, or `tinyllama:latest`

## 📝 Available Endpoints

### 1. Rewrite Suggestion (Enhanced AI Suggestions)
**Endpoint:** `POST /rewrite-suggestion`

Enhanced version of the existing suggestion system that provides AI-powered rewriting.

```json
{
  "text": "The utilization of this methodology enables the facilitation of improved outcomes.",
  "mode": "simplicity",
  "feedback": "This sentence is too complex"
}
```

**Response:**
```json
{
  "suggestion": "This method helps achieve better results.",
  "ai_answer": "AI-enhanced rewrite using simplicity mode (Readability improved by 25.3 points)",
  "confidence": "high",
  "method": "ollama_rewriter",
  "rewriting": {
    "available": true,
    "mode_used": "simplicity",
    "readability_scores": {
      "original": {"flesch_reading_ease": 45.2},
      "rewritten": {"flesch_reading_ease": 70.5}
    }
  }
}
```

### 2. Full Document Rewrite
**Endpoint:** `POST /document-rewrite`

Rewrites entire documents for improved readability and clarity.

```json
{
  "content": "Your full document content here...",
  "mode": "balanced"
}
```

### 3. Readability Analysis
**Endpoint:** `POST /readability-analysis`

Provides detailed readability metrics and recommendations.

```json
{
  "text": "Your text to analyze..."
}
```

### 4. Rewriter Service Status
**Endpoint:** `GET /api/rewriter/status`

Check if the rewriter service is available and working.

## 🎯 Rewriting Modes

### `balanced` (Default)
- **Best for:** Business documents, reports, general content
- **Approach:** Two-pass rewriting (clarity + balance)
- **Goal:** Improve readability while maintaining professionalism

### `clarity`
- **Best for:** Technical documentation, instructions, complex content
- **Approach:** Single-pass focused on clarity
- **Goal:** Maximum clarity and removal of ambiguity

### `simplicity`
- **Best for:** Public communications, educational content, user guides
- **Approach:** Plain language conversion
- **Goal:** Grade 9-11 reading level, broader accessibility

## 🔧 Integration Points

The rewriter has been integrated into existing doc-scanner functionality:

### 1. Enhanced AI Suggestions
The existing `/ai_suggestion` endpoint can now leverage rewriting by including:
```json
{
  "feedback": "Sentence is too complex",
  "sentence": "Original sentence text",
  "enable_rewriting": true
}
```

### 2. Document Processing Pipeline
During document analysis, rewriting suggestions are automatically available for any detected issues.

### 3. Backward Compatibility
- All existing endpoints continue to work unchanged
- New functionality is opt-in via additional parameters
- UI remains completely unchanged

## 🚀 Usage Examples

### Example 1: Simple Text Rewriting
```bash
curl -X POST http://localhost:5000/rewrite-suggestion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The implementation of this solution facilitates the optimization of performance metrics.",
    "mode": "simplicity"
  }'
```

### Example 2: Context-Aware Rewriting
```bash
curl -X POST http://localhost:5000/rewrite-suggestion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The aforementioned methodology exhibits substantial efficacy.",
    "feedback": "Sentence uses complex vocabulary",
    "mode": "balanced"
  }'
```

### Example 3: Full Document Enhancement
```bash
curl -X POST http://localhost:5000/document-rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your entire document content...",
    "mode": "clarity"
  }'
```

## 📊 Readability Metrics

The system provides comprehensive readability analysis:

- **Flesch Reading Ease:** 0-100 (higher = easier)
- **Flesch-Kincaid Grade Level:** US grade level
- **SMOG Index:** Years of education needed
- **Gunning Fog Index:** Complexity measure
- **Automated Readability Index:** Another grade-level measure

### Interpretation Guide:
- **90-100:** Very Easy (5th grade)
- **80-89:** Easy (6th grade)
- **70-79:** Fairly Easy (7th grade)
- **60-69:** Standard (8th-9th grade)
- **50-59:** Fairly Difficult (10th-12th grade)
- **30-49:** Difficult (College level)
- **0-29:** Very Difficult (Graduate level)

## 🛠️ Configuration

The rewriter uses configuration from `ollama_config.json`:

```json
{
  "ollama_config": {
    "api_url": "http://localhost:11434/api/generate",
    "models": {
      "fast": "tinyllama:latest",
      "balanced": "phi3:mini", 
      "quality": "llama3:8b"
    },
    "timeouts": {
      "quick": 5,
      "standard": 10,
      "high": 15
    }
  }
}
```

## 🧪 Testing

Run the integration test to verify everything is working:

```bash
python test_rewriter_integration.py
```

This will test:
- ✅ Rewriter service status
- ✅ Rewrite suggestions
- ✅ Readability analysis
- ✅ Full document rewriting

## 🔍 Troubleshooting

### Common Issues

1. **"Rewriter service unavailable"**
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is available: `ollama list`
   - Verify the API URL in config

2. **"No improvement in readability"**
   - Try a different rewriting mode
   - Some texts may already be well-optimized
   - Check if the original text is too short

3. **Slow response times**
   - Use faster models for development (`tinyllama:latest`)
   - Adjust timeouts in configuration
   - Check Ollama server performance

### Error Handling
The rewriter gracefully handles failures:
- Returns original text if rewriting fails
- Provides fallback suggestions
- Logs detailed error information

## 🎯 Best Practices

1. **Mode Selection:**
   - Use `simplicity` for user-facing content
   - Use `clarity` for technical documentation
   - Use `balanced` for business communications

2. **Context Matters:**
   - Include relevant feedback when available
   - Provide document type context
   - Consider your target audience

3. **Performance:**
   - Use appropriate models for your quality/speed needs
   - Monitor response times and adjust timeouts
   - Cache results for frequently rewritten content

## 🚀 Future Enhancements

Planned features for future releases:
- Batch document processing
- Custom rewriting prompts
- Integration with style guides
- Real-time suggestion preview
- Performance analytics
- Multi-language support

---

**Note:** This integration maintains full backward compatibility with the existing doc-scanner functionality. All existing features continue to work unchanged while providing powerful new AI-driven rewriting capabilities.
