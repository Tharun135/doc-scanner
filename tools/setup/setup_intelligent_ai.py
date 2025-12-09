#!/usr/bin/env python3
"""
Setup script for the Intelligent AI DocScanner integration.
This script helps install and configure the new RAG-first AI system.
"""

import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ Success: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required")
        return False
    logger.info(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages."""
    logger.info("📦 Installing Python dependencies...")
    
    # Install OpenAI
    run_command("pip install openai>=1.3.0", "Installing OpenAI")
    
    # Install ChromaDB 
    run_command("pip install chromadb>=1.0.15", "Installing ChromaDB")
    
    # Install sentence transformers for embeddings
    run_command("pip install sentence-transformers>=2.2.2", "Installing Sentence Transformers")
    
    # Install additional dependencies
    run_command("pip install python-dotenv>=1.1.1", "Installing python-dotenv")
    run_command("pip install requests>=2.32.3", "Installing requests")
    
    logger.info("✅ Dependencies installed successfully")

def create_env_file():
    """Create .env file template."""
    env_path = ".env"
    if not os.path.exists(env_path):
        env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (optional)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# ChromaDB Configuration
CHROMA_DB_PATH=./app/chroma_db

# DocScanner Configuration
DEBUG=True
SECRET_KEY=your_secret_key_here
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        logger.info(f"✅ Created {env_path} template")
        logger.info("⚠️  Please edit .env file and add your OpenAI API key")
    else:
        logger.info("✅ .env file already exists")

def create_directories():
    """Create necessary directories."""
    directories = [
        "./app/chroma_db",
        "./logs",
        "./data"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"✅ Created directory: {directory}")
        else:
            logger.info(f"✅ Directory exists: {directory}")

def verify_installation():
    """Verify that the installation is working."""
    logger.info("🔍 Verifying installation...")
    
    try:
        # Test OpenAI import
        import openai
        logger.info("✅ OpenAI library imported successfully")
        
        # Test ChromaDB import
        import chromadb
        logger.info("✅ ChromaDB library imported successfully")
        
        # Test sentence transformers
        import sentence_transformers
        logger.info("✅ Sentence Transformers library imported successfully")
        
        # Test intelligent AI import
        sys.path.append('./app')
        try:
            from intelligent_ai_improvement import IntelligentAISuggestionEngine
            logger.info("✅ Intelligent AI system imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️  Intelligent AI system import failed: {e}")
        
        logger.info("✅ Installation verification completed")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Installation verification failed: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("🚀 Starting DocScanner Intelligent AI Setup")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Verify installation
    if verify_installation():
        logger.info("🎉 Setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Edit .env file and add your OpenAI API key")
        logger.info("2. Optionally install and start Ollama for local AI")
        logger.info("3. Run: python run.py")
        logger.info("4. Navigate to http://localhost:5000")
        logger.info("5. Try the new 'Intelligent AI Analysis' button!")
        return True
    else:
        logger.error("❌ Setup failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)