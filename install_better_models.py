#!/usr/bin/env python3
"""
Install Better Models for DocScanner Ollama RAG
Installs Mistral, Phi3, and Llama3 models with system resource checks.
"""

import subprocess
import sys
import time
import requests
from typing import Dict, List, Tuple

def check_system_memory():
    """Check available system memory"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        return total_gb, available_gb
    except ImportError:
        print("⚠️  Install psutil for memory check: pip install psutil")
        return None, None

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        return free_gb
    except:
        return None

def check_ollama_status():
    """Check if Ollama is running and responsive"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            return True, version_info.get('version', 'unknown')
        return False, "Server error"
    except requests.exceptions.RequestException:
        return False, "Not running"

def get_installed_models():
    """Get currently installed models"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        name = parts[0]
                        size = parts[2] if len(parts) > 2 else "Unknown"
                        models.append({"name": name, "size": size})
            return models
    except Exception as e:
        print(f"Error getting models: {e}")
    return []

def install_model(model_name: str, expected_size: str) -> Tuple[bool, str]:
    """Install a specific model with progress tracking"""
    print(f"\n🔄 Installing {model_name} ({expected_size})")
    print("=" * 50)
    
    try:
        # Start installation
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Track progress
        start_time = time.time()
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Show progress indicators
                line = output.strip()
                if "pulling" in line.lower() or "%" in line:
                    print(f"  📥 {line}")
                elif "success" in line.lower():
                    print(f"  ✅ {line}")
                elif "error" in line.lower():
                    print(f"  ❌ {line}")
        
        # Check result
        return_code = process.poll()
        elapsed = time.time() - start_time
        
        if return_code == 0:
            print(f"✅ {model_name} installed successfully in {elapsed:.1f}s!")
            return True, "Success"
        else:
            print(f"❌ {model_name} installation failed (exit code: {return_code})")
            return False, f"Exit code: {return_code}"
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {model_name} installation timed out (large download)")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Error installing {model_name}: {e}")
        return False, str(e)

def recommend_models(total_ram: float, available_ram: float, free_disk: float):
    """Recommend models based on system resources"""
    
    models = [
        {
            "name": "phi3:mini",
            "size": "~2.3GB",
            "ram_needed": 4.0,
            "disk_needed": 3.0,
            "benefits": "Fast, efficient, great for everyday writing",
            "priority": 1
        },
        {
            "name": "mistral:latest", 
            "size": "~4.1GB",
            "ram_needed": 8.0,
            "disk_needed": 5.0,
            "benefits": "Excellent for writing tasks, best quality/speed balance",
            "priority": 2
        },
        {
            "name": "llama3:8b",
            "size": "~4.7GB", 
            "ram_needed": 12.0,
            "disk_needed": 6.0,
            "benefits": "Highest quality, comprehensive suggestions",
            "priority": 3
        }
    ]
    
    print(f"\n📊 System Resources:")
    print(f"  RAM: {available_ram:.1f}GB available / {total_ram:.1f}GB total")
    print(f"  Disk: {free_disk:.1f}GB free")
    
    print(f"\n🎯 Model Recommendations:")
    
    recommended = []
    for model in models:
        can_install = (
            available_ram >= model["ram_needed"] and 
            free_disk >= model["disk_needed"]
        )
        
        status = "✅ Recommended" if can_install else "⚠️  May struggle"
        print(f"\n{model['priority']}. {model['name']} ({model['size']})")
        print(f"   Status: {status}")
        print(f"   Benefits: {model['benefits']}")
        print(f"   Requirements: {model['ram_needed']}GB RAM, {model['disk_needed']}GB disk")
        
        if can_install:
            recommended.append(model)
    
    return recommended

def install_models_interactive(recommended_models: List[Dict]):
    """Interactive model installation"""
    
    print(f"\n🚀 Ready to Install Models")
    print("=" * 40)
    
    # Check what's already installed
    installed = get_installed_models()
    installed_names = [m["name"] for m in installed]
    
    print("Currently installed:")
    for model in installed:
        print(f"  ✅ {model['name']} ({model['size']})")
    
    # Filter out already installed models
    to_install = []
    for model in recommended_models:
        if not any(model["name"] in installed_name for installed_name in installed_names):
            to_install.append(model)
    
    if not to_install:
        print("\n🎉 All recommended models already installed!")
        return True
    
    print(f"\nAvailable to install:")
    for i, model in enumerate(to_install, 1):
        print(f"  {i}. {model['name']} - {model['benefits']}")
    
    # Installation options
    print(f"\nInstallation options:")
    print("1. Install all recommended models")
    print("2. Install specific models")
    print("3. Skip installation")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    models_to_install = []
    
    if choice == "1":
        models_to_install = to_install
    elif choice == "2":
        print("\nSelect models to install (comma-separated numbers):")
        selections = input("Models: ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selections.split(",")]
            models_to_install = [to_install[i] for i in indices if 0 <= i < len(to_install)]
        except:
            print("Invalid selection")
            return False
    elif choice == "3":
        print("Skipping installation")
        return True
    else:
        print("Invalid choice")
        return False
    
    # Install selected models
    if models_to_install:
        print(f"\n🔄 Installing {len(models_to_install)} models...")
        
        success_count = 0
        for model in models_to_install:
            success, message = install_model(model["name"], model["size"])
            if success:
                success_count += 1
            time.sleep(2)  # Brief pause between installations
        
        print(f"\n📊 Installation Summary:")
        print(f"  ✅ Successful: {success_count}/{len(models_to_install)}")
        print(f"  ❌ Failed: {len(models_to_install) - success_count}/{len(models_to_install)}")
        
        return success_count > 0
    
    return False

def test_installed_models():
    """Test newly installed models"""
    print(f"\n🧪 Testing Installed Models")
    print("=" * 40)
    
    models = get_installed_models()
    target_models = ["phi3:mini", "mistral:latest", "llama3:8b"]
    
    available_targets = []
    for model in models:
        for target in target_models:
            if target.split(":")[0] in model["name"]:
                available_targets.append(model["name"])
                break
    
    if not available_targets:
        print("⚠️  No target models found for testing")
        return False
    
    print(f"Testing models: {available_targets}")
    
    try:
        sys.path.append('scripts')
        from docscanner_ollama_rag import DocScannerOllamaRAG
        
        for model_name in available_targets:
            print(f"\n🔧 Testing {model_name}...")
            
            try:
                # Create RAG system with specific model
                rag_system = DocScannerOllamaRAG()
                rag_system.model = model_name
                
                # Quick initialization test
                success = rag_system._initialize_with_model(model_name)
                
                if success:
                    print(f"  ✅ {model_name} working!")
                    
                    # Test suggestion
                    result = rag_system.get_rag_suggestion(
                        feedback_text="Convert to active voice",
                        sentence_context="The document was written by John.",
                        document_type="technical"
                    )
                    
                    if result:
                        print(f"  📝 Sample: {result['suggestion'][:100]}...")
                    else:
                        print(f"  ⚠️  No suggestion generated")
                else:
                    print(f"  ❌ {model_name} failed to initialize")
                    
            except Exception as e:
                print(f"  ❌ Error testing {model_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🚀 DocScanner Better Models Installer")
    print("=" * 50)
    
    # Check prerequisites
    print("🔍 System Check...")
    
    # Check Ollama
    ollama_running, ollama_info = check_ollama_status()
    if not ollama_running:
        print(f"❌ Ollama not running: {ollama_info}")
        print("💡 Start Ollama with: ollama serve")
        return False
    
    print(f"✅ Ollama running (version: {ollama_info})")
    
    # Check resources
    total_ram, available_ram = check_system_memory()
    free_disk = check_disk_space()
    
    if total_ram is None or free_disk is None:
        print("⚠️  Could not check system resources - proceeding anyway")
        total_ram, available_ram, free_disk = 16.0, 8.0, 50.0  # Reasonable defaults
    
    # Get recommendations
    recommended = recommend_models(total_ram, available_ram, free_disk)
    
    if not recommended:
        print("\n❌ No models recommended for your system")
        print("💡 Try freeing up RAM/disk space or use TinyLLaMA")
        return False
    
    # Install models
    success = install_models_interactive(recommended)
    
    if success:
        # Test installations
        print("\n" + "="*50)
        test_success = test_installed_models()
        
        if test_success:
            print(f"\n🎉 SUCCESS: Better models ready for DocScanner!")
            print("Benefits:")
            print("  🎯 Higher quality suggestions")
            print("  🧠 Better context understanding") 
            print("  📝 More coherent writing assistance")
            print("  🚀 Enhanced DocScanner experience")
            
            print(f"\n💡 Next steps:")
            print("1. Restart DocScanner to use new models")
            print("2. Test with real documents")
            print("3. Compare suggestions with TinyLLaMA")
            print("4. Add custom knowledge: edit custom_writing_rules.json")
        else:
            print(f"\n⚠️  Models installed but testing had issues")
    else:
        print(f"\n❌ Model installation incomplete")
        print("💡 Try installing individual models: ollama pull phi3:mini")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n✅ Installation complete!")
        else:
            print(f"\n❌ Installation failed - check errors above")
    except KeyboardInterrupt:
        print(f"\n⏸️  Installation cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
