"""
Quick Status Check for Hybrid Intelligence System
===============================================
"""

import subprocess
import requests
import json
import os

def check_system_status():
    """Quick check of hybrid intelligence system status"""
    
    print("🔍 HYBRID INTELLIGENCE SYSTEM STATUS")
    print("=" * 45)
    
    # Check Ollama installation
    print("\\n1. Ollama Installation:")
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Installed: {result.stdout.strip()}")
        else:
            print("   ❌ Not working properly")
    except FileNotFoundError:
        print("   ❌ Not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check Ollama service
    print("\\n2. Ollama Service:")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("   ✅ Running on localhost:11434")
            
            # Check available models
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            print("\\n3. Hybrid Intelligence Models:")
            phi3_available = any('phi3:mini' in model for model in model_names)
            llama3_available = any('llama3:8b' in model for model in model_names)
            
            print(f"   phi3:mini (fast): {'✅' if phi3_available else '❌'}")
            print(f"   llama3:8b (deep): {'✅' if llama3_available else '❌'}")
            
            if phi3_available and llama3_available:
                print("\\n🎉 HYBRID INTELLIGENCE READY!")
                print("   • Both models available")
                print("   • Automatic selection working")
            else:
                print("\\n⚠️ Models incomplete - run setup script")
            
        else:
            print("   ❌ Service error")
    except requests.exceptions.ConnectionError:
        print("   ❌ Not running (run: ollama serve)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check system files
    print("\\n4. System Files:")
    required_files = [
        'hybrid_intelligence_rag_system.py',
        'flask_hybrid_intelligence_backend.py',
        'rules_rag_context.json',
        'ollama_config.json'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} missing")
    
    print("\\n" + "=" * 45)
    print("Run setup_hybrid_intelligence.py for complete setup")

if __name__ == "__main__":
    check_system_status()