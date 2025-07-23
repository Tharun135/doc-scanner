# Document Review Agent

🤖 **AI-Powered Document Review and Writing Assistant**

Transform your Flask-based document review application into an intelligent agent system with VS Code integration.

## Features

- 🔍 **Advanced Document Analysis**: Analyze writing quality, grammar, style, and readability
- 🧠 **AI-Powered Suggestions**: Get intelligent recommendations using Ollama models
- ⚡ **Batch Processing**: Process multiple documents simultaneously
- 🔌 **VS Code Extension**: Seamless integration with your favorite editor
- 📊 **Real-time Diagnostics**: See issues highlighted directly in your code
- 🌐 **Web Interface**: Access the agent through a web dashboard
- 🔄 **Model Context Protocol (MCP)**: Standard interface for AI model communication

## Quick Start

### 1. Setup the Agent System

```bash
# Clone or navigate to your doc-scanner directory
cd doc-scanner

# Run the setup script
python setup_agent.py
```

The setup script will:
- ✅ Check Python and Node.js versions
- ✅ Install Python dependencies
- ✅ Install VS Code extension dependencies
- ✅ Create configuration files
- ✅ Build the VS Code extension
- ✅ Create launcher scripts

### 2. Start the Agent

**Windows:**
```bash
start_agent.bat
```

**Mac/Linux:**
```bash
./start_agent.sh
```

**Or manually:**
```bash
python start_agent.py
```

### 3. Install VS Code Extension

**Option A: Install Pre-built Extension (Recommended for Quick Start)**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Click the "..." menu → "Install from VSIX"
4. Navigate to `D:\doc-scanner\vscode-extension\` and select `document-review-agent-1.0.0.vsix`
5. Click "Install" and reload VS Code when prompted

✅ **VSIX file is ready at:** `vscode-extension\document-review-agent-1.0.0.vsix`

**Option B: Build Extension from Source (For Full Features)**
```bash
# First install Node.js from https://nodejs.org/
cd vscode-extension
npm install
npm run compile
npm run package  # Creates the full-featured VSIX
```

**Option C: Use the Build Script**
```bash
# Creates a minimal VSIX without Node.js
python build_extension.py
```

### 4. Start Analyzing Documents

- Open a `.md`, `.txt`, `.html`, or `.adoc` file
- Right-click → "Analyze Document"
- Or use Command Palette: "Document Review: Analyze"

## Architecture

### Agent System

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VS Code       │    │   Flask App     │    │   Document      │
│   Extension     │◄──►│   + Agent API   │◄──►│   Review Agent  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Diagnostics   │    │   Web Dashboard │    │   AI Engine     │
│   Manager       │    │                 │    │   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **Document Review Agent** (`agent/agent.py`)
   - Core orchestration logic
   - Task queue management
   - Result caching

2. **Agent Tools** (`agent/tools.py`)
   - Document processing utilities
   - AI interaction helpers
   - Validation tools

3. **MCP Server** (`agent/mcp_server.py`)
   - WebSocket-based communication
   - Standardized agent protocol
   - Real-time updates

4. **VS Code Extension** (`vscode-extension/`)
   - Editor integration
   - Real-time diagnostics
   - Interactive suggestions

5. **Flask API** (`agent/flask_routes.py`)
   - RESTful agent endpoints
   - Async task handling
   - Health monitoring

## API Endpoints

### Agent Management
- `GET /api/agent/status` - Get agent status
- `GET /api/agent/capabilities` - List agent capabilities
- `GET /api/agent/health` - Health check

### Document Analysis
- `POST /api/agent/analyze` - Analyze a document
- `POST /api/agent/batch` - Batch process multiple documents
- `POST /api/agent/quality` - Assess document quality

### AI Suggestions
- `POST /api/agent/suggest` - Generate AI suggestions

### Tools
- `POST /api/agent/tools/document/read` - Read document
- `POST /api/agent/tools/document/structure` - Analyze structure
- `POST /api/agent/tools/validation/quality` - Validate quality

## VS Code Extension Commands

| Command | Description |
|---------|-------------|
| `Document Review: Analyze` | Analyze current document |
| `Document Review: Analyze Selection` | Analyze selected text |
| `Document Review: Get AI Suggestion` | Get suggestion for issue |
| `Document Review: Batch Analyze` | Analyze all workspace documents |
| `Document Review: Show Dashboard` | Open web dashboard |
| `Document Review: Start Agent` | Start the agent |
| `Document Review: Stop Agent` | Stop the agent |

## Configuration

### VS Code Settings

```json
{
  "documentReviewAgent.agentUrl": "http://localhost:5000",
  "documentReviewAgent.mcpUrl": "ws://localhost:8765",
  "documentReviewAgent.autoStart": true,
  "documentReviewAgent.enableDiagnostics": true,
  "documentReviewAgent.diagnosticSeverity": "Information",
  "documentReviewAgent.writingGoals": ["clarity", "conciseness", "professionalism"]
}
```

### Agent Configuration (`agent/config.json`)

```json
{
  "agent": {
    "name": "Document Review Agent",
    "version": "1.0.0",
    "host": "localhost",
    "port": 5000,
    "mcp_port": 8765
  },
  "ai": {
    "model": "mistral",
    "temperature": 0.01,
    "max_tokens": 150
  }
}
```

## Usage Examples

### Programmatic Usage

```python
from agent import DocumentReviewAgent
import asyncio

async def main():
    # Create agent
    agent = DocumentReviewAgent()
    await agent.start()
    
    # Analyze a document
    result = await agent.execute_task('document_analysis', {
        'document_path': './my-document.md',
        'document_type': 'technical',
        'writing_goals': ['clarity', 'conciseness']
    })
    
    print(f"Found {result.data['total_issues']} issues")
    
    # Get AI suggestion
    suggestion = await agent.execute_task('ai_suggestions', {
        'feedback_text': 'passive voice detected',
        'sentence_context': 'The report was completed by the team.',
        'document_type': 'technical'
    })
    
    print(f"Suggestion: {suggestion.data['suggestion']}")
    
    await agent.stop()

asyncio.run(main())
```

### REST API Usage

```bash
# Analyze document
curl -X POST http://localhost:5000/api/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document_path": "./my-document.md",
    "document_type": "technical"
  }'

# Get AI suggestion
curl -X POST http://localhost:5000/api/agent/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_text": "passive voice detected",
    "sentence_context": "The report was completed by the team."
  }'
```

## Advanced Features

### Custom Document Types

The agent supports different document types with tailored analysis:
- `technical` - Technical documentation
- `marketing` - Marketing content
- `academic` - Academic papers
- `general` - General writing

### Writing Goals

Customize analysis focus with writing goals:
- `clarity` - Focus on clear communication
- `conciseness` - Emphasize brevity
- `professionalism` - Professional tone
- `engagement` - Reader engagement
- `accessibility` - Accessibility compliance

### Batch Processing

Process multiple documents efficiently:

```python
# Batch analyze all markdown files
file_paths = ['doc1.md', 'doc2.md', 'doc3.md']
result = await agent.execute_task('batch_processing', {
    'file_paths': file_paths,
    'parallel': True
})
```

## Troubleshooting

### Common Issues

1. **Agent won't start**
   - Check Python version (3.8+ required)
   - Verify all dependencies installed
   - Check port 5000 availability

2. **VS Code extension not working**
   - Ensure agent is running
   - Check extension configuration
   - Verify network connectivity

3. **AI suggestions not available**
   - Install Ollama: https://ollama.ai/download
   - Pull a model: `ollama pull mistral`
   - Check Ollama service status

4. **Poor analysis quality**
   - Update to latest Ollama models
   - Adjust temperature settings
   - Provide more context

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Check agent health
curl http://localhost:5000/api/agent/health

# Check agent status
curl http://localhost:5000/api/agent/status
```

## Development

### Project Structure

```
doc-scanner/
├── agent/                 # Agent system
│   ├── __init__.py
│   ├── agent.py          # Main agent class
│   ├── tools.py          # Agent tools
│   ├── protocol.py       # Communication protocol
│   ├── mcp_server.py     # MCP server
│   └── flask_routes.py   # Flask API routes
├── app/                  # Original Flask app
│   ├── __init__.py
│   ├── app.py           # Main Flask routes
│   └── ai_improvement.py # AI suggestion engine
├── vscode-extension/     # VS Code extension
│   ├── package.json
│   ├── src/
│   │   ├── extension.ts
│   │   ├── agent.ts
│   │   └── providers/
│   └── out/             # Compiled output
├── requirements.txt      # Python dependencies
├── setup_agent.py       # Setup script
└── start_agent.py       # Launcher script
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing

```bash
# Test agent functionality
python -m pytest tests/

# Test VS Code extension
cd vscode-extension
npm test

# Integration tests
python test_integration.py
```

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our community]
- 📖 Documentation: [Full docs]
- 🐛 Issues: [GitHub Issues]

---

**Made with ❤️ for better writing everywhere.**
