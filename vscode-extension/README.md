# Document Review Agent VS Code Extension

This extension brings AI-powered document review and writing assistance directly into Visual Studio Code.

## Features
- Analyze your documents for grammar, style, and terminology issues
- Get context-aware, actionable suggestions powered by AI (Gemini/OpenAI)
- Works with Markdown and plaintext files
- Integrates with the Doc-Scanner backend for advanced analysis

## Usage
1. **Start the Doc-Scanner backend**
   ```
   python start_agent.py
   ```
2. **Open a document in VS Code**
3. **Run the extension commands:**
   - Open the Command Palette (Ctrl+Shift+P)
   - Type `Analyze Document` or `Analyze Selection`
   - Review suggestions in the editor or panel

## Requirements
- Python backend (Doc-Scanner) running locally
- API keys for Gemini/OpenAI configured in the backend

## Installation
- Install this extension from a `.vsix` file via Extensions → "..." → Install from VSIX

## Contributing
Pull requests and suggestions are welcome!

## License
MIT License
