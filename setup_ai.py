#!/usr/bin/env python3
"""
Setup script for the enhanced AI suggestion system.
This script helps configure and optimize the doc-scanner AI capabilities.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install Python requirements."""
    print("\n📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    print("\n🤖 Checking Ollama installation...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} models")
            return True, models
    except:
        pass
    
    print("❌ Ollama not found or not running")
    print("To install Ollama:")
    print("1. Visit https://ollama.ai")
    print("2. Download and install Ollama")
    print("3. Run: ollama pull mistral-7b-instruct")
    return False, []

def download_recommended_models():
    """Download recommended AI models for better suggestions."""
    print("\n⬇️ Downloading recommended AI models...")
    
    recommended_models = [
        "mistral-7b-instruct",  # Main model for general suggestions
        "llama3.1",            # Alternative model
        "codellama"            # For technical documentation
    ]
    
    for model in recommended_models:
        print(f"Downloading {model}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", model], 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            if result.returncode == 0:
                print(f"✅ {model} downloaded successfully")
            else:
                print(f"❌ Failed to download {model}: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ Download timeout for {model} - you can continue manually")
        except FileNotFoundError:
            print("❌ Ollama command not found. Please install Ollama first.")
            break

def setup_database():
    """Initialize the performance monitoring database."""
    print("\n🗄️ Setting up performance monitoring database...")
    try:
        from app.performance_monitor import monitor
        monitor.init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_config_file():
    """Create initial configuration file."""
    print("\n⚙️ Creating configuration file...")
    
    config = {
        "ai_settings": {
            "default_model": "mistral-7b-instruct",
            "temperature": 0.2,
            "max_tokens": 400,
            "enable_learning": True
        },
        "performance": {
            "track_metrics": True,
            "auto_improve": True,
            "feedback_collection": True
        },
        "features": {
            "advanced_prompts": True,
            "context_awareness": True,
            "multi_model_fallback": True
        }
    }
    
    config_path = Path("ai_config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def test_ai_suggestions():
    """Test the AI suggestion system."""
    print("\n🧪 Testing AI suggestion system...")
    
    test_cases = [
        {
            "feedback": "Passive voice detected",
            "sentence": "The report was completed by the team yesterday.",
            "expected_improvement": "active voice"
        },
        {
            "feedback": "Sentence too long and complex",
            "sentence": "The system, which was developed by our engineering team over several months, provides users with comprehensive data management capabilities.",
            "expected_improvement": "shorter sentences"
        }
    ]
    
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        all_passed = True
        for i, test in enumerate(test_cases, 1):
            print(f"Test {i}: {test['feedback']}")
            
            result = get_enhanced_ai_suggestion(
                feedback_text=test["feedback"],
                sentence_context=test["sentence"],
                document_type="general",
                writing_goals=["clarity", "conciseness"]
            )
            
            if result and result.get("suggestion"):
                print(f"✅ Test {i} passed - Got suggestion")
                print(f"   Method: {result.get('method', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 'unknown')}")
            else:
                print(f"❌ Test {i} failed - No suggestion generated")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions for the enhanced system."""
    print("""
🎉 Setup completed! Here's how to use the enhanced AI suggestion system:

📖 BASIC USAGE:
1. Start the application: python run.py
2. Navigate to http://localhost:5000
3. Upload documents or paste text for analysis

🔧 ENHANCED FEATURES:
- Advanced AI prompts for better suggestions
- Context-aware feedback based on document type
- Performance monitoring and learning from user feedback
- Multiple fallback systems for reliability

📊 MONITORING:
- Visit /performance_dashboard for AI performance metrics
- Provide feedback on suggestions to improve the system
- Check /ai_config for configuration options

🎯 DOCUMENT TYPES:
Specify document types for better suggestions:
- technical: For technical documentation
- academic: For scholarly writing
- business: For corporate communications
- marketing: For promotional content
- creative: For creative writing

💡 TIPS FOR BETTER SUGGESTIONS:
1. Provide context with your text
2. Specify document type when possible
3. Give feedback on suggestions to train the system
4. Use specific feedback descriptions for better AI responses

🆘 TROUBLESHOOTING:
- If Ollama fails, the system uses smart fallback suggestions
- Check logs in the console for error details
- Performance metrics help identify improvement areas
""")

def main():
    """Main setup function."""
    print("🚀 Doc-Scanner AI Enhancement Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check Ollama
    ollama_available, models = check_ollama_installation()
    
    if ollama_available:
        if len(models) == 0:
            download_recommended_models()
    else:
        print("⚠️ Continuing without Ollama - fallback suggestions will be used")
    
    # Setup database
    setup_database()
    
    # Create config
    create_config_file()
    
    # Test system
    if test_ai_suggestions():
        print("✅ All tests passed!")
    else:
        print("⚠️ Some tests failed, but system should still work")
    
    # Print instructions
    print_usage_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
