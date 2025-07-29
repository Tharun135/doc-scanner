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

def check_openai_setup():
    """Check if OpenAI API key is configured."""
    print("\n🤖 Checking OpenAI API setup...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found in environment variables")
        print("\nTo set up OpenAI API:")
        print("1. Get your API key from https://platform.openai.com/api-keys")
        print("2. Set environment variable: OPENAI_API_KEY=your_api_key_here")
        print("3. On Windows: setx OPENAI_API_KEY \"your_api_key_here\"")
        print("4. On Linux/Mac: export OPENAI_API_KEY=\"your_api_key_here\"")
        return False, []
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test the API key by listing models
        models = client.models.list()
        available_models = [model.id for model in models.data if 'gpt' in model.id.lower()]
        
        print(f"✅ OpenAI API connected successfully")
        print(f"📋 Available GPT models: {len(available_models)}")
        
        # Show recommended models
        recommended = [m for m in available_models if m in ['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4o']]
        if recommended:
            print(f"🎯 Recommended models available: {recommended}")
        
        return True, available_models
        
    except ImportError:
        print("❌ OpenAI Python library not installed")
        print("Run: pip install openai")
        return False, []
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("Please check your API key and internet connection")
        return False, []

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
            "default_model": "gpt-4o-mini",
            "temperature": 0.1,
            "max_tokens": 150,
            "enable_learning": True,
            "api_provider": "openai"
        },
        "performance": {
            "track_metrics": True,
            "auto_improve": True,
            "feedback_collection": True
        },
        "features": {
            "advanced_prompts": True,
            "context_awareness": True,
            "smart_fallback": True
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
- OpenAI ChatGPT integration for superior AI suggestions
- Context-aware feedback based on document type
- Performance monitoring and learning from user feedback
- Smart fallback systems for reliability

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
1. Set up your OpenAI API key for best results
2. Provide context with your text
3. Specify document type when possible
4. Give feedback on suggestions to train the system
5. Use specific feedback descriptions for better AI responses

🆘 TROUBLESHOOTING:
- If OpenAI API fails, the system uses smart fallback suggestions
- Check logs in the console for error details
- Ensure your OPENAI_API_KEY environment variable is set
- Performance metrics help identify improvement areas

🔑 API COSTS:
- GPT-4o-mini: ~$0.15 per 1M tokens (very affordable)
- GPT-3.5-turbo: ~$0.50 per 1M tokens
- Usage is typically very low for document suggestions
""")

def main():
    """Main setup function."""
    print("🚀 Doc-Scanner AI Enhancement Setup (OpenAI ChatGPT)")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check OpenAI API setup
    openai_available, models = check_openai_setup()
    
    if not openai_available:
        print("⚠️ Continuing without OpenAI - fallback suggestions will be used")
        print("⚠️ For best AI suggestions, please set up your OpenAI API key")
    
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
