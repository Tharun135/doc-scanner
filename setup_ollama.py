"""
Ollama Setup and Management Script for Doc Scanner
Helps install, configure, and manage Ollama with optimal models for writing assistance.
"""

import os
import sys
import requests
import subprocess
import time
import platform
from typing import List, Dict, Any

def check_ollama_installed() -> bool:
    """Check if Ollama is installed on the system."""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_installed_models() -> List[str]:
    """Get list of installed Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"].split(":")[0] for model in models]
        return []
    except Exception:
        return []

def install_ollama():
    """Download and install Ollama based on the operating system."""
    system = platform.system().lower()
    
    print("🚀 Installing Ollama...")
    
    if system == "windows":
        print("Please download and install Ollama from: https://ollama.ai/download/windows")
        print("Run the installer and restart your terminal.")
        return False
    elif system == "darwin":  # macOS
        print("Installing Ollama on macOS...")
        try:
            subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], 
                         shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("Failed to install Ollama. Please visit: https://ollama.ai/download/mac")
            return False
    elif system == "linux":
        print("Installing Ollama on Linux...")
        try:
            subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], 
                         shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("Failed to install Ollama. Please visit: https://ollama.ai/download/linux")
            return False
    else:
        print(f"Unsupported operating system: {system}")
        print("Please visit: https://ollama.ai/ for manual installation")
        return False

def start_ollama_service():
    """Start the Ollama service."""
    print("🔄 Starting Ollama service...")
    
    # Try to start Ollama in the background
    try:
        if platform.system().lower() == "windows":
            # On Windows, Ollama usually runs as a service
            subprocess.Popen(["ollama", "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Unix systems
            subprocess.Popen(["ollama", "serve"])
        
        # Wait a moment for service to start
        time.sleep(3)
        
        if check_ollama_running():
            print("✅ Ollama service started successfully")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def pull_model(model_name: str) -> bool:
    """Pull/download a specific model."""
    print(f"📥 Downloading model: {model_name}")
    print("This may take several minutes for the first download...")
    
    try:
        result = subprocess.run(["ollama", "pull", model_name], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ Model {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model {model_name}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout downloading model {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading model {model_name}: {e}")
        return False

def recommend_models_for_writing() -> List[Dict[str, Any]]:
    """Return recommended models for writing assistance."""
    return [
        {
            "name": "mistral",
            "size": "4.1GB",
            "description": "Excellent for writing assistance, fast and accurate",
            "recommended": True
        },
        {
            "name": "phi3",
            "size": "2.3GB", 
            "description": "Microsoft's efficient model, good for writing tasks",
            "recommended": True
        },
        {
            "name": "llama2",
            "size": "3.8GB",
            "description": "Meta's popular model, good general performance",
            "recommended": False
        },
        {
            "name": "tinyllama",
            "size": "637MB",
            "description": "Very fast but less capable, good for testing",
            "recommended": False
        }
    ]

def setup_recommended_models():
    """Set up the recommended models for writing assistance."""
    models = recommend_models_for_writing()
    
    print("\n📋 Recommended Models for Writing Assistance:")
    for model in models:
        status = "⭐ RECOMMENDED" if model["recommended"] else "Optional"
        print(f"  • {model['name']} ({model['size']}) - {status}")
        print(f"    {model['description']}")
    
    print("\n🎯 Installing recommended models...")
    
    installed_any = False
    for model in models:
        if model["recommended"]:
            if pull_model(model["name"]):
                installed_any = True
                break  # Install only one recommended model initially
    
    if not installed_any:
        print("⚠️  No recommended models were installed. Trying tinyllama as fallback...")
        pull_model("tinyllama")

def test_model(model_name: str) -> bool:
    """Test if a model works correctly."""
    print(f"🧪 Testing model: {model_name}")
    
    try:
        # Test with a simple writing improvement prompt
        test_prompt = "Rewrite this sentence to be more active: 'The report was written by the team.'"
        
        # Make API call to test
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": test_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result and result["response"].strip():
                print(f"✅ Model {model_name} is working correctly")
                print(f"   Sample response: {result['response'][:100]}...")
                return True
        
        print(f"❌ Model {model_name} test failed")
        return False
        
    except Exception as e:
        print(f"❌ Error testing model {model_name}: {e}")
        return False

def get_system_info():
    """Display system information and recommendations."""
    print("🖥️  System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Memory recommendations
    if platform.system().lower() == "windows":
        print("\n💾 Memory Recommendations:")
        print("   • Minimum: 8GB RAM for Mistral/Phi-3")
        print("   • Recommended: 16GB+ RAM for best performance")
        print("   • For 4GB systems: Use tinyllama model")

def main():
    """Main setup function."""
    print("🚀 Doc Scanner - Ollama Setup Assistant")
    print("=" * 50)
    
    # Show system info
    get_system_info()
    
    # Check if Ollama is installed
    print("\n🔍 Checking Ollama installation...")
    if not check_ollama_installed():
        print("❌ Ollama not found")
        if input("Install Ollama now? (y/n): ").lower().startswith('y'):
            if not install_ollama():
                print("Please install Ollama manually and run this script again.")
                return
        else:
            print("Please install Ollama manually from: https://ollama.ai/")
            return
    else:
        print("✅ Ollama is installed")
    
    # Check if service is running
    print("\n🔍 Checking Ollama service...")
    if not check_ollama_running():
        print("❌ Ollama service not running")
        if input("Start Ollama service now? (y/n): ").lower().startswith('y'):
            if not start_ollama_service():
                print("Please start Ollama manually: 'ollama serve'")
                return
        else:
            print("Please start Ollama service manually: 'ollama serve'")
            return
    else:
        print("✅ Ollama service is running")
    
    # Check installed models
    print("\n🔍 Checking installed models...")
    installed_models = get_installed_models()
    
    if installed_models:
        print("✅ Found installed models:")
        for model in installed_models:
            print(f"   • {model}")
        
        # Test a model
        test_model_name = installed_models[0]
        if input(f"Test model '{test_model_name}'? (y/n): ").lower().startswith('y'):
            test_model(test_model_name)
    else:
        print("❌ No models installed")
        if input("Install recommended models for writing assistance? (y/n): ").lower().startswith('y'):
            setup_recommended_models()
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Ensure Ollama service is running: 'ollama serve'")
    print("2. Test your Doc Scanner app: 'python run.py'")
    print("3. Upload a document and see AI suggestions in action!")
    
    print("\n🔧 Useful Commands:")
    print("   • List models: ollama list")
    print("   • Pull new model: ollama pull <model_name>")
    print("   • Remove model: ollama rm <model_name>")
    print("   • Check service: curl http://localhost:11434/api/tags")

if __name__ == "__main__":
    main()
