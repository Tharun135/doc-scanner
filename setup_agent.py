#!/usr/bin/env python3
"""
Setup script for Document Review Agent
Installs all necessary dependencies and initializes the agent system.
"""

import subprocess
import sys
import os
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        logger.info(f"✅ Command succeeded: {command}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8 or higher is required")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_node_version():
    """Check if Node.js is installed."""
    result = run_command("node --version")
    if result:
        logger.info(f"✅ Node.js detected: {result.stdout.strip()}")
        return True
    logger.error("❌ Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/")
    return False


def install_python_dependencies():
    """Install Python dependencies."""
    logger.info("🔧 Installing Python dependencies...")
    
    # Check if we're in a virtual environment
    if not sys.prefix != sys.base_prefix:
        logger.warning("⚠️  Not in a virtual environment. Consider using venv or conda.")
    
    # Install base requirements
    result = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    if not result:
        return False
    
    # Install additional agent dependencies
    additional_deps = [
        "websockets>=11.0",
        "asyncio-mqtt>=0.11.0",
        "pydantic>=2.0.0"
    ]
    
    for dep in additional_deps:
        result = run_command(f"{sys.executable} -m pip install {dep}")
        if not result:
            logger.warning(f"⚠️  Failed to install {dep}, continuing...")
    
    return True


def install_vscode_extension_dependencies():
    """Install VS Code extension dependencies."""
    logger.info("🔧 Installing VS Code extension dependencies...")
    
    vscode_dir = Path("vscode-extension")
    if not vscode_dir.exists():
        logger.error("❌ VS Code extension directory not found")
        return False
    
    # Install npm dependencies
    result = run_command("npm install", cwd=vscode_dir)
    if not result:
        logger.error("❌ Failed to install npm dependencies")
        return False
    
    return True


def setup_agent_config():
    """Setup agent configuration."""
    logger.info("🔧 Setting up agent configuration...")
    
    config = {
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
        },
        "documents": {
            "supported_formats": [".txt", ".md", ".docx", ".pdf", ".html", ".adoc"],
            "max_file_size": "10MB",
            "batch_size": 10
        },
        "vscode": {
            "auto_start": True,
            "enable_diagnostics": True,
            "diagnostic_severity": "Information"
        }
    }
    
    config_path = Path("agent/config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Configuration saved to {config_path}")
    return True


def check_ollama():
    """Check if Ollama is installed and running."""
    logger.info("🔍 Checking Ollama installation...")
    
    result = run_command("ollama --version")
    if not result:
        logger.warning("⚠️  Ollama not found. AI suggestions will use fallback mode.")
        logger.info("💡 To install Ollama: https://ollama.ai/download")
        return False
    
    logger.info(f"✅ Ollama detected: {result.stdout.strip()}")
    
    # Check if any models are available
    result = run_command("ollama list")
    if result and "NAME" in result.stdout:
        logger.info("✅ Ollama models found")
        return True
    else:
        logger.warning("⚠️  No Ollama models found. Please install a model:")
        logger.info("💡 Run: ollama pull mistral")
        return False


def create_launcher_scripts():
    """Create launcher scripts for easy startup."""
    logger.info("🔧 Creating launcher scripts...")
    
    # Python launcher script
    python_launcher = """#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Document Review Agent starting...")
    print("📡 Flask server: http://localhost:5000")
    print("🔌 Agent API: http://localhost:5000/api/agent")
    print("⏹️  Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
    
    with open("start_agent.py", "w") as f:
        f.write(python_launcher)
    
    # Batch file for Windows
    batch_launcher = """@echo off
echo Starting Document Review Agent...
python start_agent.py
pause
"""
    
    with open("start_agent.bat", "w") as f:
        f.write(batch_launcher)
    
    # Shell script for Unix
    shell_launcher = """#!/bin/bash
echo "Starting Document Review Agent..."
python3 start_agent.py
"""
    
    with open("start_agent.sh", "w") as f:
        f.write(shell_launcher)
    
    # Make shell script executable
    if os.name != 'nt':
        os.chmod("start_agent.sh", 0o755)
    
    logger.info("✅ Launcher scripts created")
    return True


def test_agent_startup():
    """Test if the agent can start properly."""
    logger.info("🧪 Testing agent startup...")
    
    try:
        # Import test
        from agent.agent import DocumentReviewAgent
        from app import create_app
        
        # Create agent instance
        agent = DocumentReviewAgent()
        logger.info("✅ Agent import successful")
        
        # Create Flask app
        app = create_app()
        logger.info("✅ Flask app creation successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Agent startup test failed: {str(e)}")
        return False


def build_vscode_extension():
    """Build the VS Code extension."""
    logger.info("🔨 Building VS Code extension...")
    
    vscode_dir = Path("vscode-extension")
    
    # Compile TypeScript
    result = run_command("npm run compile", cwd=vscode_dir)
    if not result:
        logger.error("❌ Failed to compile TypeScript")
        return False
    
    logger.info("✅ VS Code extension built successfully")
    logger.info("💡 To install: Open VS Code, go to Extensions, click '...' > 'Install from VSIX', then select the .vsix file")
    
    return True


def print_success_message():
    """Print success message with usage instructions."""
    print("\n" + "="*60)
    print("🎉 DOCUMENT REVIEW AGENT SETUP COMPLETE!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1️⃣  Start the agent:")
    print("   • Windows: double-click start_agent.bat")
    print("   • Mac/Linux: ./start_agent.sh")
    print("   • Or run: python start_agent.py")
    print()
    print("2️⃣  Install VS Code extension:")
    print("   • Open VS Code")
    print("   • Go to Extensions (Ctrl+Shift+X)")
    print("   • Click '...' menu > 'Install from VSIX'")
    print("   • Select vscode-extension/document-review-agent-1.0.0.vsix")
    print()
    print("3️⃣  Configure VS Code:")
    print("   • Open Settings (Ctrl+,)")
    print("   • Search for 'Document Review Agent'")
    print("   • Set agent URL to: http://localhost:5000")
    print()
    print("4️⃣  Start reviewing documents:")
    print("   • Open a .md, .txt, or .html file")
    print("   • Right-click > 'Analyze Document'")
    print("   • Or use Command Palette: 'Document Review: Analyze'")
    print()
    print("🔗 ENDPOINTS:")
    print("   • Web Interface: http://localhost:5000")
    print("   • Agent API: http://localhost:5000/api/agent")
    print("   • Health Check: http://localhost:5000/api/agent/health")
    print()
    print("📚 FEATURES:")
    print("   • ✅ Document analysis")
    print("   • ✅ AI-powered suggestions")
    print("   • ✅ Batch processing")
    print("   • ✅ VS Code integration")
    print("   • ✅ Real-time diagnostics")
    print()
    print("="*60)


def main():
    """Main setup function."""
    logger.info("🚀 Starting Document Review Agent setup...")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_python_dependencies():
        logger.error("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    if not install_vscode_extension_dependencies():
        logger.error("❌ Failed to install VS Code extension dependencies")
        sys.exit(1)
    
    # Setup configuration
    if not setup_agent_config():
        logger.error("❌ Failed to setup configuration")
        sys.exit(1)
    
    # Check optional dependencies
    check_ollama()
    
    # Create launcher scripts
    if not create_launcher_scripts():
        logger.error("❌ Failed to create launcher scripts")
        sys.exit(1)
    
    # Test agent
    if not test_agent_startup():
        logger.error("❌ Agent startup test failed")
        sys.exit(1)
    
    # Build VS Code extension
    if not build_vscode_extension():
        logger.warning("⚠️  VS Code extension build failed, but setup can continue")
    
    print_success_message()


if __name__ == "__main__":
    main()
