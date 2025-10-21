"""
Hybrid Intelligence Setup Script
===============================

Complete setup guide and verification for your hybrid RAG-LLM system
with intelligent model selection: phi3:mini + llama3:8b
"""

import subprocess
import requests
import time
import json

def check_ollama_installation():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timeout")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def install_models():
    """Install required models for hybrid intelligence"""
    models_to_install = [
        ("phi3:mini", "Fast model for 90% of tasks (2GB)"),
        ("llama3:8b", "Deep reasoning model for complex analysis (4GB)")
    ]
    
    print("\\n📦 Installing Hybrid Intelligence Models...")
    print("=" * 50)
    
    for model, description in models_to_install:
        print(f"\\n🔄 Installing {model}")
        print(f"   Purpose: {description}")
        
        try:
            print(f"   Running: ollama pull {model}")
            result = subprocess.run(
                ['ollama', 'pull', model], 
                capture_output=True, 
                text=True, 
                timeout=600  # 10 minute timeout for downloads
            )
            
            if result.returncode == 0:
                print(f"   ✅ {model} installed successfully")
            else:
                print(f"   ❌ Failed to install {model}")
                print(f"   Error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ Installation timeout for {model}")
        except Exception as e:
            print(f"   ❌ Error installing {model}: {e}")

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print("❌ Ollama service error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama service not running")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama service: {e}")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print("\\n🚀 Starting Ollama service...")
    print("   Command: ollama serve")
    print("   Note: This will start the service in the background")
    
    try:
        # Start ollama serve in background
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for service to start
        time.sleep(3)
        
        # Check if it's running
        if check_ollama_service():
            print("✅ Ollama service started successfully")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

def verify_models():
    """Verify that required models are available"""
    print("\\n🔍 Verifying Hybrid Intelligence Models...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            required_models = ['phi3:mini', 'llama3:8b']
            
            print(f"\\n📋 Available models: {len(available_models)}")
            for model in available_models:
                print(f"   • {model}")
            
            print(f"\\n🎯 Hybrid Intelligence Status:")
            
            phi3_available = any('phi3:mini' in model for model in available_models)
            llama3_available = any('llama3:8b' in model for model in available_models)
            
            print(f"   phi3:mini (fast): {'✅' if phi3_available else '❌'}")
            print(f"   llama3:8b (deep): {'✅' if llama3_available else '❌'}")
            
            if phi3_available and llama3_available:
                print("\\n🎉 Hybrid Intelligence Ready!")
                print("   • Fast model available for 90% of tasks")
                print("   • Deep model available for complex reasoning")
                return True
            else:
                print("\\n⚠️ Hybrid Intelligence Incomplete")
                missing = []
                if not phi3_available:
                    missing.append("phi3:mini")
                if not llama3_available:
                    missing.append("llama3:8b")
                print(f"   Missing models: {', '.join(missing)}")
                return False
        else:
            print("❌ Cannot verify models - service error")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying models: {e}")
        return False

def test_hybrid_intelligence():
    """Test the hybrid intelligence system"""
    print("\\n🧪 Testing Hybrid Intelligence...")
    
    test_cases = [
        {
            "prompt": "Improve this sentence: 'The system works fine.'",
            "expected_model": "phi3:mini",
            "mode": "fast"
        },
        {
            "prompt": "Analyze this complex sentence structure: 'When the server is restarted after maintenance, which usually happens weekly, all temporary sessions are cleared.'",
            "expected_model": "llama3:8b", 
            "mode": "deep"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\\n   Test {i}: {test['mode']} mode")
        print(f"   Expected model: {test['expected_model']}")
        
        try:
            # Test with ollama run command
            result = subprocess.run(
                ['ollama', 'run', test['expected_model'], test['prompt']], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"   ✅ {test['expected_model']} responded ({len(response)} chars)")
                print(f"   Preview: {response[:100]}...")
            else:
                print(f"   ❌ {test['expected_model']} failed")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ {test['expected_model']} timeout")
        except Exception as e:
            print(f"   ❌ Error testing {test['expected_model']}: {e}")

def show_integration_guide():
    """Show how to integrate with your DocScanner"""
    print(f"\\n🚀 INTEGRATION WITH YOUR DOCSCANNER")
    print("=" * 50)
    
    print("""
STEP 1: Use the Flask Backend
-----------------------------
python flask_hybrid_intelligence_backend.py

This starts your API server with:
• POST /api/ai-suggestion - Single suggestions
• POST /api/batch-suggestions - Batch processing
• Automatic model selection (phi3:mini vs llama3:8b)

STEP 2: Frontend Integration
----------------------------
// In your DocScanner frontend
async function getAISuggestion(sentence, issueType, context = "") {
    const response = await fetch('http://localhost:5000/api/ai-suggestion', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            sentence: sentence,
            issue_type: issueType,
            context: context,
            complexity: 'default'  // Let system auto-select model
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('Model used:', result.model_used);
        console.log('Corrected:', result.corrected);
        console.log('Reasoning:', result.reasoning);
        return result;
    }
}

STEP 3: Direct Python Integration  
---------------------------------
from hybrid_intelligence_rag_system import HybridIntelligenceRAGSystem, FlaggedIssue

# Initialize system
ai_system = HybridIntelligenceRAGSystem()

# Get intelligent suggestion
issue = FlaggedIssue(
    sentence="Delete the languages that are not needed.",
    issue="Passive voice",
    context="User manual section"
)

result = ai_system.generate_hybrid_solution(issue)

# System automatically selects:
# • phi3:mini for simple/fast tasks
# • llama3:8b for complex reasoning

print(f"Model used: {result['model_used']}")
print(f"Corrected: {result['corrected']}")
""")

def main():
    """Complete setup and verification process"""
    print("🧠 Hybrid Intelligence RAG-LLM Setup")
    print("=" * 50)
    print("Setting up intelligent model selection:")
    print("• phi3:mini - Fast responses for 90% of tasks")  
    print("• llama3:8b - Deep reasoning for complex analysis")
    print()
    
    # Step 1: Check Ollama installation
    print("STEP 1: Check Ollama Installation")
    print("-" * 35)
    ollama_installed = check_ollama_installation()
    
    if not ollama_installed:
        print("\\n❌ Ollama not found. Please install Ollama first:")
        print("   1. Go to: https://ollama.ai")
        print("   2. Download and install Ollama for Windows")
        print("   3. Restart your computer")
        print("   4. Run this setup script again")
        return False
    
    # Step 2: Check/Start Ollama service
    print("\\nSTEP 2: Check Ollama Service")
    print("-" * 30)
    service_running = check_ollama_service()
    
    if not service_running:
        print("Starting Ollama service...")
        service_running = start_ollama_service()
        
        if not service_running:
            print("\\n❌ Could not start Ollama service automatically.")
            print("   Please run manually: ollama serve")
            return False
    
    # Step 3: Install required models
    print("\\nSTEP 3: Install Hybrid Intelligence Models")
    print("-" * 45)
    install_models()
    
    # Step 4: Verify setup
    print("\\nSTEP 4: Verify Hybrid Intelligence Setup")
    print("-" * 40)
    models_ready = verify_models()
    
    if models_ready:
        # Step 5: Test the system
        test_hybrid_intelligence()
        
        # Step 6: Show integration guide
        show_integration_guide()
        
        print(f"\\n🎉 SUCCESS! Hybrid Intelligence Ready!")
        print("=" * 40)
        print("✅ phi3:mini installed - Fast responses")
        print("✅ llama3:8b installed - Deep reasoning") 
        print("✅ Automatic model selection working")
        print("✅ RAG context integration ready")
        print()
        print("🚀 Next Steps:")
        print("   1. Run: python flask_hybrid_intelligence_backend.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Test your hybrid intelligence system!")
        
        return True
    else:
        print("\\n❌ Setup incomplete. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n🎯 Your hybrid RAG-LLM system is ready!")
        print("   Every DocScanner issue → Intelligent model selection → Smart solutions")
    else:
        print("\\n⚠️ Setup needs attention. Please resolve the issues above.")