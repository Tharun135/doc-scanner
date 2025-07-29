# 🧠 RAG Integration Guide: Gemini + LangChain for Enhanced AI Suggestions

This guide covers the integration of Retrieval-Augmented Generation (RAG) using Google Gemini and LangChain to enhance the AI suggestions in your document scanner.

## 🎯 What's New

The AI Suggestions panel now includes:
- **Context-aware suggestions** using your document content
- **Knowledge base** with writing guidelines and best practices
- **Source attribution** showing where suggestions come from
- **Enhanced accuracy** by combining traditional AI with retrieval

## 🚀 Quick Setup

### 1. Install Dependencies

Run the setup script to install RAG dependencies:

```bash
python setup_rag.py
```

Or install manually:

```bash
pip install langchain==0.1.5 langchain-google-genai==0.0.8 langchain-community==0.0.20 chromadb==0.4.22 faiss-cpu==1.7.4 google-generativeai==0.3.2
```

### 2. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

#### OpenAI API Key (for fallback)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key

### 3. Configure Environment

Create or update your `.env` file:

```env
# Google Gemini for RAG
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI for fallback (optional but recommended)
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Test the Integration

1. Start your application: `python run.py`
2. Upload a document
3. Click the AI icon (🤖) next to any writing issue
4. Look for the "🧠 RAG Enhanced" badge on suggestions

## 🔧 How It Works

### Architecture Overview

```
Document Upload → Text Extraction → Knowledge Base
                                         ↓
Writing Issue → OpenAI Suggestion + RAG Context → Combined Output
                     ↓                    ↓
              Traditional AI        Document Context
                                   + Writing Guidelines
```

### RAG Components

1. **Document Context**: Your uploaded document is automatically added to the knowledge base
2. **Writing Guidelines**: Pre-loaded best practices for grammar, style, and clarity
3. **Vector Search**: Finds relevant context for each writing issue
4. **Combined Suggestions**: Merges traditional AI with retrieved context

### Enhanced UI Features

- **RAG Badge**: Shows when suggestions use RAG enhancement
- **Source Attribution**: Displays which guidelines or document parts influenced the suggestion
- **Contextual Examples**: Provides document-specific examples when available

## 📋 Usage Examples

### Basic Usage

1. Upload any document (PDF, DOCX, TXT, MD)
2. The system automatically processes and indexes the content
3. Click AI suggestions to get enhanced, context-aware advice

### What You'll See

**Traditional Suggestion:**
```
AI Suggestion: Convert passive voice to active voice.
Method: openai_chatgpt
```

**RAG-Enhanced Suggestion:**
```
AI Suggestion: Convert passive voice to active voice. 
Change "The report was completed by the team" to "The team completed the report".

🧠 RAG Enhanced
Method: openai_chatgpt_with_rag

📚 Knowledge Sources:
📋 Writing Guidelines: Use active voice to make writing more direct and engaging...
📄 Document Context: Your document uses formal business language...
```

## ⚙️ Configuration

### Customizing Writing Guidelines

Edit `app/rag_system.py` and modify the `_get_default_writing_guidelines()` method to add your organization's specific style rules.

### Adjusting RAG Behavior

Key parameters in `app/rag_system.py`:

```python
# Chunk size for document processing
chunk_size=800          # Larger chunks = more context
chunk_overlap=100       # Overlap between chunks

# Retrieval settings  
search_kwargs={"k": 4}  # Number of relevant chunks to retrieve
```

### Model Selection

The system uses:
- **Gemini Pro** for RAG generation
- **OpenAI GPT-3.5/4** for traditional suggestions
- **Embedding-001** for document vectorization

## 🎨 Frontend Integration

### New UI Elements

The AI suggestions now include:

1. **RAG Badge**: Indicates when suggestions use retrieval
2. **Sources Section**: Shows knowledge sources used
3. **Enhanced Formatting**: Better display of combined suggestions

### CSS Classes Added

```css
.rag-badge          /* RAG enhancement indicator */
.sources-container  /* Container for source attribution */
.source-item        /* Individual source display */
.source-content     /* Source content text */
```

## 📊 Performance Monitoring

### Tracking RAG Usage

The system tracks:
- When RAG suggestions are used
- User feedback on RAG vs. traditional suggestions
- Source attribution accuracy
- Response times

### Debugging

Check logs for:
```
"RAG suggestion obtained successfully"
"Using enhanced AI suggestion with RAG context..."
"Gemini RAG system initialized successfully"
```

## 🛠️ Troubleshooting

### Common Issues

**RAG system not available:**
```
Warning: RAG system not available - continuing with standard AI suggestions
```
- Check if dependencies are installed
- Verify Google API key is set correctly

**Empty suggestions:**
```
Error getting RAG suggestion: Invalid response
```
- Check API key quota and billing
- Verify internet connection

**Import errors:**
```
Import "langchain" could not be resolved
```
- Run `pip install -r requirements.txt`
- Check virtual environment activation

### Fallback Behavior

If RAG fails, the system automatically falls back to:
1. Traditional OpenAI suggestions
2. Rule-based suggestions
3. Basic fallback responses

## 🔐 Security Considerations

### API Key Management
- Store API keys in `.env` file only
- Never commit API keys to version control
- Use environment variables in production

### Data Privacy
- Document content is processed locally before sending to APIs
- Only relevant excerpts are sent to external services
- No document content is permanently stored externally

## 📈 Future Enhancements

### Planned Features
- Custom knowledge base uploads
- Team-specific writing guidelines
- Advanced source filtering
- Multilingual support
- Offline RAG mode

### Integration Opportunities
- Custom document templates
- Industry-specific guidelines
- Real-time collaboration features
- Advanced analytics dashboard

## 🤝 Contributing

To extend the RAG system:

1. **Add new knowledge sources** in `_get_default_writing_guidelines()`
2. **Customize retrieval logic** in `_format_rag_query()`
3. **Enhance UI components** in the frontend templates
4. **Add new document types** in the processing pipeline

## 📚 Additional Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [Google Gemini API Guide](https://ai.google.dev/docs)
- [Chroma Vector Database](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)

## 🎉 Benefits

With RAG integration, you get:

✅ **Better Context**: Suggestions consider your specific document  
✅ **Consistency**: Guidelines ensure consistent writing style  
✅ **Transparency**: See why suggestions were made  
✅ **Quality**: Higher accuracy through retrieval augmentation  
✅ **Flexibility**: Combines multiple AI approaches  

The RAG system transforms generic AI suggestions into personalized, context-aware writing assistance that understands your document and follows established guidelines.
