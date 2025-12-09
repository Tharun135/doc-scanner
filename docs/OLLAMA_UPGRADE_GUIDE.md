# 🚀 DocScanner Ollama RAG Upgrade Guide

Your DocScanner now has a **fully functional local RAG system**! Here are the upgrade options to make it even better.

## 🎯 Current System Status

✅ **Working Components:**
- **Ollama Server**: Running locally
- **Model**: TinyLLaMA (637MB - fast and efficient) 
- **ChromaDB**: Vector storage for writing rules
- **LlamaIndex**: RAG framework connecting everything
- **Custom Knowledge**: Support for your own writing guidelines

## 🤖 Better Models

Upgrade to more powerful models for higher quality suggestions:

### Option 1: Mistral (Recommended for Writing)
```bash
ollama pull mistral:latest
```
- **Size**: ~4.1GB
- **Benefits**: Excellent reasoning, coherent suggestions, great for writing
- **Best for**: Professional writing, complex edits

### Option 2: Phi3 Mini (Best Balance)
```bash
ollama pull phi3:mini
```
- **Size**: ~2.3GB  
- **Benefits**: Fast, efficient, good quality
- **Best for**: Quick suggestions, everyday writing

### Option 3: Llama3 8B (Highest Quality)
```bash
ollama pull llama3:8b
```
- **Size**: ~4.7GB
- **Benefits**: Excellent quality, comprehensive suggestions
- **Best for**: Professional documents, detailed analysis

### System Requirements
- **8GB RAM**: TinyLLaMA, Phi3 Mini
- **16GB RAM**: Mistral, Llama3 8B
- **32GB+ RAM**: Large models like Llama3 70B

## 📚 Custom Knowledge

Add your own writing guidelines to enhance AI suggestions:

### 1. Quick Setup
Run the upgrade test to create sample custom rules:
```bash
python test_upgrades.py
```

This creates `custom_writing_rules.json` with sample rules for:
- Technical writing style
- Clear error messages  
- Direct addressing ("you" vs "the user")
- Definitive language

### 2. Add Your Own Rules
Edit `custom_writing_rules.json`:

```json
[
  {
    "text": "Use 'you' instead of 'the user' for direct communication",
    "category": "technical_writing",
    "examples": ["Click the button", "Enter your password"]
  },
  {
    "text": "Write error messages that explain what to do next", 
    "category": "error_handling",
    "examples": ["File not found. Check the path and try again."]
  }
]
```

### 3. Types of Custom Knowledge to Add
- **Company Style Guides**: Brand voice, terminology preferences
- **Industry Standards**: Medical, legal, technical conventions  
- **Domain Expertise**: Specialized knowledge for your field
- **Personal Preferences**: Your writing style and patterns

### 4. Auto-Loading
Custom rules are automatically loaded when DocScanner starts. No code changes needed!

## 🎯 Fine-Tuning (Advanced)

Train models specifically for your writing style:

### Method 1: Ollama Modelfile (Simple)

1. **Create a Modelfile**:
```dockerfile
FROM phi3:mini

SYSTEM """You are a technical writing assistant.

Writing Style:
- Use active voice
- Write in present tense  
- Use "you" instead of "the user"
- Be direct and specific
- Include practical examples
"""
```

2. **Create your custom model**:
```bash
ollama create my-writing-model -f Modelfile
```

3. **Update DocScanner**:
Edit `scripts/docscanner_ollama_rag.py`, change:
```python
def __init__(self, model="my-writing-model"):
```

### Method 2: LoRA Fine-Tuning (Advanced)

1. **Collect Training Data**: 100+ examples of your writing style
2. **Format as JSONL**:
```json
{"instruction": "Fix passive voice: The report was written by John", "response": "John wrote the report"}
{"instruction": "Make this more direct: Users might want to click save", "response": "Click Save to continue"}
```

3. **Use Training Libraries**: 
   - [Unsloth](https://github.com/unslothai/unsloth) - Fast LoRA training
   - [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) - Full training pipeline

4. **Export to Ollama**: Convert trained model to Ollama format

## 🧪 Testing Upgrades

### Test Current System
```bash
python test_final_integration.py
```

### Test Upgrade Features  
```bash
python test_upgrades.py
```

### Interactive Upgrade Guide
```bash
python upgrade_ollama_rag.py
```

## 🎯 Upgrade Recommendations by Use Case

### For Daily Writing (Emails, Docs)
- **Model**: phi3:mini
- **Custom Rules**: Company style guide, common corrections
- **Benefits**: Fast, consistent, personal

### For Professional Writing (Articles, Reports) 
- **Model**: mistral:latest
- **Custom Rules**: Industry standards, advanced grammar
- **Benefits**: High quality, professional tone

### For Technical Documentation
- **Model**: llama3:8b  
- **Custom Rules**: API docs, code examples, technical terms
- **Benefits**: Comprehensive, accurate, detailed

### For Specialized Domains (Medical, Legal)
- **Model**: Fine-tuned phi3 or mistral
- **Custom Rules**: Domain terminology, compliance requirements
- **Benefits**: Domain expertise, regulatory compliance

## 💡 Pro Tips

1. **Start Small**: Test with phi3:mini before upgrading to larger models
2. **Monitor Performance**: Larger models use more RAM and are slower
3. **Iterate Custom Rules**: Start with a few rules, add more based on results
4. **Backup Models**: Keep TinyLLaMA as fallback for resource constraints
5. **Test Thoroughly**: Validate improvements with real documents

## 🔧 Troubleshooting

### Model Installation Fails
- Check disk space (models can be 4GB+)
- Ensure stable internet connection
- Try smaller models first

### Performance Issues
- Close other applications to free RAM
- Use smaller models (phi3:mini vs llama3:8b)
- Increase Ollama timeout settings

### Custom Rules Not Working
- Check JSON syntax in `custom_writing_rules.json`
- Restart DocScanner after adding rules
- Verify rules are specific and actionable

## 🎉 Success Metrics

After upgrading, you should see:
- **Better Suggestions**: More relevant, context-aware improvements
- **Consistent Style**: Suggestions match your writing preferences  
- **Domain Accuracy**: AI understands your field/industry
- **Faster Workflow**: Less manual editing needed

## 📞 Support

- **Test Scripts**: Run the test files to verify upgrades
- **Logs**: Check console output for error messages
- **Community**: Share your custom rules and model experiences
- **Documentation**: This guide covers most upgrade scenarios

---

**Your DocScanner is now a powerful, customizable AI writing assistant that runs completely locally and privately!** 🏆
