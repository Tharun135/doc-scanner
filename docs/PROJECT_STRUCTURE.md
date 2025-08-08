# Doc Scanner Project Structure

## Current Organization

```
doc-scanner/
├── app/
│   ├── __init__.py
│   ├── llamaindex_ai.py          # LlamaIndex + ChromaDB interface
│   ├── ai_improvement.py         # Suggestion generator
│   ├── app.py                    # Flask web application
│   ├── ai_config.py              # AI configuration
│   ├── custom_terminology.py     # Custom term handling
│   ├── performance_monitor.py    # Performance tracking
│   ├── rules/                    # Writing rules
│   └── templates/                # HTML templates
│
├── style_guides/                 # 📁 NEW: Style guide imports
│   ├── README.md                 # How to use this directory
│   ├── company_style_guide.md    # Company writing standards
│   ├── technical_writing_guide.md # Technical documentation
│   └── business_writing_guide.md # Business communication
│
├── improve_knowledge_db.py       # 🚀 Enhanced: Auto-imports style guides
├── enhance_knowledge_base.py     # Analysis and recommendations
├── setup_ollama.py               # Ollama setup script
├── run.py                        # Application launcher
├── requirements.txt              # Python dependencies
├── .env                          # Environment configuration
│
├── chroma_db/                    # ChromaDB vector database
├── rule_knowledge_base/          # Legacy knowledge storage
├── static/                       # CSS, JS, images
├── tests/                        # 🧪 ALL test files (63 files organized)
│   ├── test_*.py                 # Python test scripts
│   ├── debug_*.py                # Debug utilities
│   ├── demo_*.py                 # Demo scripts
│   └── test_*.md                 # Test documents
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
└── deployment/                   # Build and deployment tools
```

## Key Components

### 🔥 Core AI Engine
- **`app/llamaindex_ai.py`**: Main AI interface using LlamaIndex + ChromaDB + Ollama
- **`app/ai_improvement.py`**: Suggestion generation and text processing
- **`chroma_db/`**: Local vector database for knowledge storage

### 📚 Knowledge Management
- **`style_guides/`**: Organized directory for writing standards and style guides
- **`improve_knowledge_db.py`**: Enhanced script that auto-imports style guides
- **`enhance_knowledge_base.py`**: Analysis tool for knowledge optimization

### 🧪 Testing & Development
- **`tests/`**: All test files, debug scripts, and demo code (63 files total)
- **`verify_structure.py`**: Project structure verification script
- **`enhance_knowledge_base.py`**: Analysis tool for knowledge optimization

### 🌐 Web Application
- **`app/app.py`**: Flask web server
- **`app/templates/`**: HTML templates
- **`static/`**: Web assets (CSS, JavaScript, images)
- **`run.py`**: Application entry point

### ⚙️ Configuration & Setup
- **`requirements.txt`**: All Python dependencies for LlamaIndex stack
- **`.env`**: Environment variables and API configurations
- **`setup_ollama.py`**: Automated Ollama and model setup

## Usage Workflow

### 1. Adding New Style Guides
```bash
# 1. Add your .md or .txt files to style_guides/
cp your_company_guide.md style_guides/

# 2. Import them into the knowledge base
python improve_knowledge_db.py
```

### 2. Running the Application
```bash
# Start the web application
python run.py

# Application runs on: http://127.0.0.1:5000
```

### 3. Analyzing Knowledge Base
```bash
# Get current knowledge analysis
python enhance_knowledge_base.py
```

## Technical Stack

### AI Components
- **LlamaIndex 0.11.20**: RAG (Retrieval Augmented Generation) system
- **ChromaDB 0.5.23**: Vector database for semantic search
- **Ollama**: Local LLM inference server
- **TinyLlama**: Lightweight language model (637MB)

### Web Framework
- **Flask**: Python web framework
- **HTML/CSS/JavaScript**: Frontend interface
- **Responsive design**: Mobile-friendly interface

### Development Tools
- **Python 3.8+**: Programming language
- **Virtual Environment**: Isolated dependency management
- **Git**: Version control
- **VS Code**: Recommended development environment

## File Types Supported

### Style Guide Imports
- **`.md`**: Markdown files (recommended)
- **`.txt`**: Plain text files
- **`.docx`**: Microsoft Word documents (with python-docx)

### Document Processing
- **Input**: Plain text, HTML content, markdown
- **Output**: Improved text with AI suggestions
- **Formats**: Real-time web interface, API responses

## Migration Status

✅ **Complete Migration from Google Gemini to Local AI**
- No external API dependencies
- Unlimited processing quota
- Complete privacy (local processing)
- No monthly costs
- Faster response times

✅ **Enhanced Knowledge Management**
- Organized style guide directory
- Automatic import capabilities
- Comprehensive writing standards
- Domain-specific knowledge patterns

## Next Steps

### Immediate Actions
1. **Add your organization's style guides** to `style_guides/`
2. **Run knowledge enhancement** with `python improve_knowledge_db.py`
3. **Test the application** with your specific writing needs

### Future Enhancements
1. **Larger Models**: Upgrade to Mistral or Phi-3 for more advanced suggestions
2. **Custom Rules**: Add domain-specific writing rules to `app/rules/`
3. **Integration**: Connect with existing document workflows
4. **Analytics**: Track suggestion acceptance and effectiveness

## Support Resources

- **Quick Start**: See `docs/QUICK_START.md`
- **Migration Guide**: See `LLAMAINDEX_MIGRATION_GUIDE.md`
- **Enhancement Guide**: See `KNOWLEDGE_ENHANCEMENT_GUIDE.md`
- **AI Setup**: See `LOCAL_AI_SETUP_COMPLETE.md`

Your Doc Scanner is now a **powerful, self-contained AI writing assistant** with unlimited processing capabilities! 🚀
