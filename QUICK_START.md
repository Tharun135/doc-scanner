# Quick Setup Guide for Document Review Agent

## 🚀 Transform Your Flask App into an AI Agent with VS Code Extension

This guide will help you convert your existing Flask document review app into a powerful AI agent system with VS Code integration.

### What You'll Get

✅ **AI-Powered Document Analysis** - Advanced writing quality assessment  
✅ **Smart Suggestions** - Context-aware improvement recommendations  
✅ **VS Code Extension** - Seamless editor integration  
✅ **Batch Processing** - Handle multiple documents at once  
✅ **Real-time Diagnostics** - See issues highlighted in your editor  
✅ **Web Dashboard** - Monitor and control the agent  

## Prerequisites

- Python 3.8+
- Node.js 16+
- VS Code
- Ollama (optional, for enhanced AI features)

## Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install additional agent dependencies
pip install websockets asyncio-mqtt dataclasses-json
```

## Step 2: Start the Agent

```bash
# Simple start
python start_agent.py

# Or use the full setup (installs VS Code extension too)
python setup_agent.py
```

## Step 3: Test the Agent

Open your browser and visit:
- **Web Interface**: http://localhost:5000
- **Agent Status**: http://localhost:5000/api/agent/status
- **Health Check**: http://localhost:5000/api/agent/health

## Step 4: Install VS Code Extension

### Option A: Auto-install (if you ran setup_agent.py)
The extension is automatically built and ready to install from `vscode-extension/` folder.

### Option B: Manual install
1. Navigate to `vscode-extension/` folder
2. Run `npm install && npm run compile`
3. In VS Code: Extensions → "..." → Install from VSIX
4. Select the generated .vsix file

## Step 5: Configure VS Code

Add to your VS Code settings:

```json
{
  "documentReviewAgent.agentUrl": "http://localhost:5000",
  "documentReviewAgent.autoStart": true,
  "documentReviewAgent.enableDiagnostics": true
}
```

## Step 6: Start Using the Agent

1. **Open a document** (.md, .txt, .html, .adoc)
2. **Right-click** → "Analyze Document"
3. **View results** in the Document Review panel
4. **Get suggestions** by right-clicking on highlighted issues

## API Usage Examples

### Analyze a Document
```bash
curl -X POST http://localhost:5000/api/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"document_path": "./my-document.md"}'
```

### Get AI Suggestion
```bash
curl -X POST http://localhost:5000/api/agent/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_text": "passive voice detected",
    "sentence_context": "The report was completed by the team."
  }'
```

## Key Features

### 1. Agent Capabilities
- Document analysis
- AI suggestions
- Batch processing
- Quality assessment

### 2. VS Code Integration
- Real-time diagnostics
- Context menus
- Command palette
- Status monitoring

### 3. Web Dashboard
- Agent status
- Analysis results
- Performance metrics
- Configuration

## Architecture Overview

```
Your Existing Flask App
         +
Document Review Agent (Python)
         +
VS Code Extension (TypeScript)
         =
Complete AI Writing Assistant
```

## Troubleshooting

### Agent Won't Start
- Check Python version: `python --version`
- Verify dependencies: `pip list`
- Check port 5000 availability

### VS Code Extension Issues
- Ensure agent is running on http://localhost:5000
- Check VS Code settings
- Restart VS Code after installation

### No AI Suggestions
- Install Ollama: https://ollama.ai/
- Pull a model: `ollama pull mistral`
- Restart the agent

## File Structure

```
doc-scanner/
├── agent/              # New agent system
│   ├── agent.py       # Main agent logic
│   ├── tools.py       # Agent tools
│   ├── mcp_server.py  # MCP protocol
│   └── flask_routes.py # API routes
├── app/               # Your existing Flask app
├── vscode-extension/  # VS Code extension
├── start_agent.py     # Quick launcher
└── setup_agent.py     # Full setup script
```

## What's New vs Your Original App

| Original Flask App | Enhanced Agent System |
|-------------------|----------------------|
| Web interface only | Web + VS Code + API |
| Manual file upload | Auto-detect + batch |
| Basic suggestions | AI-powered recommendations |
| Single document | Multiple documents |
| Static analysis | Real-time diagnostics |

## Next Steps

1. **Customize the agent** - Modify `agent/agent.py` for your specific needs
2. **Add more document types** - Extend parsing in `agent/tools.py`
3. **Enhance AI prompts** - Improve suggestions in `app/ai_improvement.py`
4. **Create custom VS Code commands** - Add features to the extension
5. **Deploy to cloud** - Scale the agent for team use

## Support

If you encounter issues:
1. Check the logs in the console
2. Verify all dependencies are installed
3. Test the agent health endpoint
4. Review the configuration files

Your Flask app is now a powerful AI agent system! 🎉
