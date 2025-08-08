# Document Scanner

A sophisticated document analysis and improvement tool with AI-powered suggestions and grammar checking capabilities.

## Project Structure

```text
doc-scanner/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── app.py             # Flask application entry point
│   ├── ai_config.py       # AI configuration
│   ├── ai_improvement.py  # AI improvement logic
│   ├── llamaindex_ai.py   # LlamaIndex integration
│   ├── performance_monitor.py
│   ├── smart_rule_filter.py
│   ├── custom_terminology.py
│   ├── rules/             # Grammar and style rules
│   └── templates/         # HTML templates
├── scripts/               # Utility and maintenance scripts
│   ├── debug_*.py         # Debug utilities
│   ├── analyze_*.py       # Analysis tools
│   ├── fix_*.py          # Fix and improvement scripts
│   ├── setup_ollama.py   # Ollama setup
│   ├── enhance_knowledge_base.py
│   ├── improve_knowledge_db.py
│   └── utils/            # Utility modules
├── tests/                 # Test files
│   ├── test_*.py         # Unit and integration tests
│   └── verify_structure.py
├── docs/                  # Documentation
│   ├── README.md         # Project documentation
│   ├── QUICK_START.md    # Getting started guide
│   ├── AI_*.md           # AI-related documentation
│   ├── workflow.md       # Development workflow
│   └── *.md             # Other documentation files
├── data/                  # Data files and databases
│   ├── *.json           # Cache and configuration files
│   ├── *.db             # Database files
│   └── *.txt            # Text data files
├── static/               # Static web assets
├── style_guides/         # Style guide references
├── rule_knowledge_base/  # Knowledge base for rules
├── chroma_db/           # ChromaDB vector database
├── deployment/          # Deployment configurations
├── venv/               # Python virtual environment
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env               # Environment variables
└── .gitignore         # Git ignore rules
```

## Quick Start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python run.py
   ```

3. Open your browser to `http://localhost:5000`

## Features

- AI-powered document analysis
- Grammar and style checking
- Real-time suggestions
- Knowledge base integration
- Vector database for semantic search
- Performance monitoring
- Custom terminology support

## Development

- Main application code is in the `app/` directory
- Tests are in the `tests/` directory
- Utility scripts are in the `scripts/` directory
- Documentation is in the `docs/` directory

For more detailed information, see the documentation in the `docs/` folder.
