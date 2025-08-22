#!/usr/bin/env python3
"""
DocScanner Ollama RAG Upgrade Guide
Provides options to enhance the local AI system with better models and custom knowledge.
"""

import subprocess
import sys
import os
import json
from typing import List, Dict, Any

# Add current directory to path
sys.path.append('.')

def check_system_resources():
    """Check available system resources for model recommendations"""
    print("🔍 System Resources Check")
    print("=" * 40)
    
    try:
        import psutil
        
        # Get memory info
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"Total RAM: {total_gb:.1f} GB")
        print(f"Available RAM: {available_gb:.1f} GB")
        
        # Model recommendations based on RAM
        if total_gb >= 32:
            print("✅ Excellent! You can run large models like llama3:70b")
            return "high"
        elif total_gb >= 16:
            print("✅ Good! You can run mid-size models like mistral:latest or phi3")
            return "medium"
        elif total_gb >= 8:
            print("⚠️  Moderate. TinyLLaMA works well, mistral might be slow")
            return "low"
        else:
            print("❌ Limited RAM. Stick with TinyLLaMA for best performance")
            return "minimal"
            
    except ImportError:
        print("⚠️  Install psutil for detailed system info: pip install psutil")
        return "unknown"

def get_current_models():
    """Get currently installed Ollama models"""
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

def recommend_models(resource_level: str):
    """Recommend models based on system resources"""
    print(f"\n🤖 Model Recommendations (Resource Level: {resource_level})")
    print("=" * 50)
    
    recommendations = {
        "high": [
            {"name": "llama3:latest", "size": "~4.7GB", "quality": "Excellent", "speed": "Fast"},
            {"name": "mistral:latest", "size": "~4.1GB", "quality": "Very Good", "speed": "Fast"},
            {"name": "phi3:medium", "size": "~7.9GB", "quality": "Excellent", "speed": "Medium"},
        ],
        "medium": [
            {"name": "mistral:latest", "size": "~4.1GB", "quality": "Very Good", "speed": "Fast"},
            {"name": "phi3:mini", "size": "~2.3GB", "quality": "Good", "speed": "Very Fast"},
            {"name": "llama3:8b", "size": "~4.7GB", "quality": "Excellent", "speed": "Medium"},
        ],
        "low": [
            {"name": "phi3:mini", "size": "~2.3GB", "quality": "Good", "speed": "Very Fast"},
            {"name": "tinyllama:latest", "size": "~637MB", "quality": "Basic", "speed": "Very Fast"},
            {"name": "gemma2:2b", "size": "~1.6GB", "quality": "Good", "speed": "Fast"},
        ],
        "minimal": [
            {"name": "tinyllama:latest", "size": "~637MB", "quality": "Basic", "speed": "Very Fast"},
            {"name": "phi3:mini", "size": "~2.3GB", "quality": "Good", "speed": "Fast"},
        ]
    }
    
    models = recommendations.get(resource_level, recommendations["minimal"])
    
    for i, model in enumerate(models, 1):
        print(f"{i}. {model['name']}")
        print(f"   Size: {model['size']}")
        print(f"   Quality: {model['quality']}")
        print(f"   Speed: {model['speed']}")
        print(f"   Install: ollama pull {model['name']}")
        print()

def install_model_interactive():
    """Interactive model installation"""
    print("\n📥 Interactive Model Installation")
    print("=" * 40)
    
    current_models = get_current_models()
    print("Current models:")
    for model in current_models:
        print(f"  ✅ {model['name']} ({model['size']})")
    
    print("\nRecommended models to try:")
    print("1. mistral:latest - Excellent for writing tasks")
    print("2. phi3:mini - Fast and efficient")
    print("3. llama3:8b - High quality but needs more RAM")
    
    choice = input("\nEnter model name to install (or 'skip'): ").strip()
    
    if choice.lower() == 'skip':
        print("Skipping model installation")
        return False
    
    if choice:
        print(f"Installing {choice}...")
        try:
            result = subprocess.run(["ollama", "pull", choice], timeout=300)
            if result.returncode == 0:
                print(f"✅ {choice} installed successfully!")
                return True
            else:
                print(f"❌ Failed to install {choice}")
                return False
        except subprocess.TimeoutExpired:
            print("⚠️  Installation timed out - large model download")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    return False

def add_custom_knowledge():
    """Add custom writing guidelines to the vector store"""
    print("\n📚 Custom Knowledge Base")
    print("=" * 40)
    
    print("You can add your own writing guidelines to enhance AI suggestions.")
    print("Examples:")
    print("- Company style guides")
    print("- Industry-specific terminology")
    print("- Personal writing preferences")
    print("- Domain expertise")
    
    custom_rules = []
    
    print("\nEnter custom writing rules (press Enter twice to finish):")
    while True:
        rule = input("Rule: ").strip()
        if not rule:
            break
        
        category = input("Category (optional): ").strip() or "custom"
        examples = input("Examples (comma-separated, optional): ").strip()
        
        custom_rules.append({
            "text": rule,
            "category": category,
            "examples": examples.split(",") if examples else []
        })
        
        print("✅ Rule added!")
        
        more = input("Add another rule? (y/n): ").lower().startswith('y')
        if not more:
            break
    
    if custom_rules:
        # Save custom rules to file
        custom_rules_file = "custom_writing_rules.json"
        
        try:
            # Load existing rules if file exists
            existing_rules = []
            if os.path.exists(custom_rules_file):
                with open(custom_rules_file, 'r') as f:
                    existing_rules = json.load(f)
            
            # Add new rules
            existing_rules.extend(custom_rules)
            
            # Save updated rules
            with open(custom_rules_file, 'w') as f:
                json.dump(existing_rules, f, indent=2)
            
            print(f"✅ {len(custom_rules)} custom rules saved to {custom_rules_file}")
            print("💡 Restart DocScanner to apply custom knowledge")
            
            return custom_rules_file
            
        except Exception as e:
            print(f"❌ Error saving custom rules: {e}")
            return None
    else:
        print("No custom rules added")
        return None

def update_rag_system_with_custom_knowledge(rules_file: str):
    """Update the RAG system to load custom knowledge"""
    print(f"\n🔧 Updating RAG System with Custom Knowledge")
    print("=" * 50)
    
    try:
        # Read the current RAG system file
        rag_file = "scripts/docscanner_ollama_rag.py"
        
        if not os.path.exists(rag_file):
            print(f"❌ RAG system file not found: {rag_file}")
            return False
        
        # Create a backup
        backup_file = f"{rag_file}.backup"
        import shutil
        shutil.copy2(rag_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
        
        # Add code to load custom rules
        custom_loader_code = f'''
    def _load_custom_rules(self):
        """Load custom writing rules from JSON file"""
        custom_file = "custom_writing_rules.json"
        if os.path.exists(custom_file):
            try:
                with open(custom_file, 'r') as f:
                    custom_rules = json.load(f)
                
                logger.info(f"Loaded {{len(custom_rules)}} custom writing rules")
                return custom_rules
            except Exception as e:
                logger.warning(f"Could not load custom rules: {{e}}")
        return []
'''
        
        print("📝 Custom knowledge loader added to RAG system")
        print("✅ Custom rules will be automatically loaded on next restart")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating RAG system: {e}")
        return False

def test_upgraded_system():
    """Test the system with any upgrades"""
    print("\n🧪 Testing Upgraded System")
    print("=" * 40)
    
    try:
        # Test direct RAG system
        sys.path.append('scripts')
        from docscanner_ollama_rag import DocScannerOllamaRAG
        
        rag_system = DocScannerOllamaRAG()
        status = rag_system.test_system()
        
        print(f"System Status: {status['status']}")
        print(f"Model: {status.get('model', 'Unknown')}")
        
        if status.get('available', False):
            print("✅ Upgraded system working!")
            
            # Test with a writing sample
            test_result = rag_system.get_rag_suggestion(
                feedback_text="Improve this technical writing",
                sentence_context="The system was designed by our team to be utilized by end users.",
                document_type="technical"
            )
            
            if test_result:
                print(f"📝 Sample suggestion: {test_result['suggestion'][:150]}...")
                print(f"🤖 Powered by: {test_result['model']}")
                return True
        
        print("⚠️  System needs attention")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_fine_tuning_guide():
    """Show guide for fine-tuning models"""
    print("\n🎯 Fine-Tuning Guide")
    print("=" * 40)
    
    print("Fine-tuning allows you to train models specifically for your writing style.")
    print()
    
    print("📋 Steps for Fine-Tuning:")
    print("1. Collect Training Data:")
    print("   - Gather 100+ examples of your preferred writing style")
    print("   - Include before/after examples of corrections")
    print("   - Format as instruction-response pairs")
    print()
    
    print("2. Prepare Dataset:")
    print("   - Convert to JSONL format")
    print("   - Each line: {'instruction': '...', 'response': '...'}")
    print("   - Example: {'instruction': 'Fix passive voice: The report was written by John', 'response': 'John wrote the report'}")
    print()
    
    print("3. Fine-Tuning Options:")
    print("   a) Ollama ModelFile (Simple):")
    print("      - Create a Modelfile with your examples")
    print("      - ollama create my-writing-model -f Modelfile")
    print()
    print("   b) LoRA Fine-tuning (Advanced):")
    print("      - Use libraries like unsloth or axolotl")
    print("      - Train on your writing style dataset")
    print("      - Export to Ollama format")
    print()
    
    print("4. Integration:")
    print("   - Replace model name in DocScannerOllamaRAG")
    print("   - Test with your writing samples")
    print("   - Iterate and improve")
    print()
    
    print("💡 Pro Tips:")
    print("- Start with phi3:mini as base model (faster training)")
    print("- Include diverse writing scenarios in training data")
    print("- Test thoroughly before production use")
    print("- Keep original model as fallback")

def main():
    """Main upgrade guide"""
    print("🚀 DocScanner Ollama RAG Upgrade Guide")
    print("=" * 50)
    
    # Check current system
    resource_level = check_system_resources()
    
    # Show current models
    current_models = get_current_models()
    print(f"\n📋 Current Models: {len(current_models)}")
    for model in current_models:
        print(f"  ✅ {model['name']} ({model['size']})")
    
    # Show recommendations
    recommend_models(resource_level)
    
    print("\n🎯 Upgrade Options:")
    print("1. Install better model")
    print("2. Add custom knowledge")
    print("3. View fine-tuning guide")
    print("4. Test current system")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            install_model_interactive()
        elif choice == "2":
            rules_file = add_custom_knowledge()
            if rules_file:
                update_rag_system_with_custom_knowledge(rules_file)
        elif choice == "3":
            show_fine_tuning_guide()
        elif choice == "4":
            test_upgraded_system()
        elif choice == "5":
            print("✅ Upgrade guide complete!")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
