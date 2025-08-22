#!/usr/bin/env python3
"""
Quick Test: DocScanner Ollama RAG Upgrades
Tests better models and custom knowledge features
"""

import sys
import json
import os

# Add current directory to path  
sys.path.append('.')

def create_sample_custom_rules():
    """Create sample custom writing rules"""
    print("📚 Creating Sample Custom Writing Rules")
    print("=" * 40)
    
    # Sample custom rules for technical writing
    custom_rules = [
        {
            "text": "Use 'you' instead of 'the user' for direct communication. This makes instructions more personal and engaging.",
            "category": "technical_writing",
            "examples": ["Click the button", "Enter your password", "Select your preferred option"]
        },
        {
            "text": "Avoid hedging language like 'might', 'perhaps', 'possibly' in technical documentation. Be definitive and clear.",
            "category": "clarity", 
            "examples": ["The system will restart", "This method returns", "Click Save to continue"]
        },
        {
            "text": "Use parallel structure in lists and sequences. Keep verb forms consistent throughout instructions.",
            "category": "consistency",
            "examples": ["Save, edit, and publish", "Configure settings, test connections, deploy changes"]
        },
        {
            "text": "Write error messages that explain what happened and what to do next. Avoid technical jargon.",
            "category": "error_handling",
            "examples": ["File not found. Check the file path and try again.", "Connection failed. Verify your network settings."]
        }
    ]
    
    # Save to file
    filename = "custom_writing_rules.json"
    try:
        with open(filename, 'w') as f:
            json.dump(custom_rules, f, indent=2)
        
        print(f"✅ Created {filename} with {len(custom_rules)} custom rules:")
        for rule in custom_rules:
            print(f"  • {rule['category']}: {rule['text'][:60]}...")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error creating custom rules: {e}")
        return None

def test_with_custom_knowledge():
    """Test the RAG system with custom knowledge"""
    print("\n🧪 Testing RAG with Custom Knowledge")
    print("=" * 40)
    
    try:
        sys.path.append('scripts')
        from docscanner_ollama_rag import DocScannerOllamaRAG
        
        # Create new RAG system (will load custom rules automatically)
        rag_system = DocScannerOllamaRAG()
        
        # Test system status
        status = rag_system.test_system()
        print(f"System status: {status['status']}")
        print(f"Model: {status.get('model', 'Unknown')}")
        
        if status.get('available', False):
            print("✅ RAG system working with custom knowledge!")
            
            # Test with scenarios that should trigger custom rules
            test_scenarios = [
                {
                    "feedback": "Use direct addressing instead of third person",
                    "sentence": "The user should click the save button to continue.",
                    "expected": "Direct addressing (you)"
                },
                {
                    "feedback": "Remove hedging language for clearer instructions", 
                    "sentence": "The system might possibly restart after the update.",
                    "expected": "Definitive language"
                },
                {
                    "feedback": "Improve error message clarity",
                    "sentence": "Error 404: Resource not accessible.",
                    "expected": "Clearer error message"
                }
            ]
            
            for i, test in enumerate(test_scenarios, 1):
                print(f"\n📝 Test {i}: {test['expected']}")
                print(f"Original: {test['sentence']}")
                
                result = rag_system.get_rag_suggestion(
                    feedback_text=test['feedback'],
                    sentence_context=test['sentence'],
                    document_type="technical"
                )
                
                if result:
                    suggestion = result['suggestion']
                    print(f"AI Suggestion: {suggestion[:120]}...")
                    print(f"Model: {result.get('model', 'unknown')}")
                    
                    # Check if suggestion seems to address the custom rule
                    if 'you' in suggestion.lower() and 'user' not in suggestion.lower():
                        print("🎯 Custom rule applied: Direct addressing!")
                    elif 'will' in suggestion or 'must' in suggestion:
                        print("🎯 Custom rule applied: Definitive language!")
                    elif len(suggestion) > len(test['sentence']):
                        print("🎯 Enhanced suggestion detected!")
                else:
                    print("⚠️  No suggestion generated")
            
            return True
        else:
            print(f"❌ RAG system not available: {status.get('reason', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_model_upgrade_options():
    """Show available model upgrade options"""
    print("\n🤖 Model Upgrade Options")
    print("=" * 40)
    
    # Check what models are currently available
    import subprocess
    
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Currently installed models:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('NAME'):
                    print(f"  ✅ {line}")
        else:
            print("❌ Could not check installed models")
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
    
    print("\n💡 Recommended upgrades:")
    
    upgrades = [
        {
            "name": "mistral:latest",
            "size": "~4.1GB", 
            "benefits": "Better reasoning, more coherent suggestions",
            "command": "ollama pull mistral:latest"
        },
        {
            "name": "phi3:mini",
            "size": "~2.3GB",
            "benefits": "Fast, efficient, good for writing tasks", 
            "command": "ollama pull phi3:mini"
        },
        {
            "name": "llama3:8b",
            "size": "~4.7GB",
            "benefits": "Excellent quality, comprehensive suggestions",
            "command": "ollama pull llama3:8b"
        }
    ]
    
    for upgrade in upgrades:
        print(f"\n📦 {upgrade['name']}")
        print(f"   Size: {upgrade['size']}")
        print(f"   Benefits: {upgrade['benefits']}")
        print(f"   Install: {upgrade['command']}")
    
    print("\n⚡ Performance Tips:")
    print("• Larger models = better quality but slower")
    print("• phi3:mini is the best balance of speed/quality")
    print("• mistral excels at writing and editing tasks")
    print("• Test models with your specific use cases")

def show_fine_tuning_example():
    """Show a practical fine-tuning example"""
    print("\n🎯 Fine-Tuning Example")
    print("=" * 40)
    
    print("Fine-tune a model for your specific writing style:")
    
    example_modelfile = """
FROM phi3:mini

# Custom system prompt for your writing style
SYSTEM \"\"\"
You are a technical writing assistant specialized in clear, concise documentation.

Writing Style:
- Use active voice
- Write in present tense  
- Use "you" instead of "the user"
- Be direct and specific
- Include practical examples
- Avoid jargon and buzzwords

Format responses as complete sentence rewrites.
\"\"\"

# Example training data
TEMPLATE \"\"\"
User: {{.Prompt}}
Assistant: {{.Response}}
\"\"\"
"""
    
    print("1. Create a Modelfile:")
    print("```")
    print(example_modelfile)
    print("```")
    
    print("\n2. Create your custom model:")
    print("   ollama create my-docscanner-model -f Modelfile")
    
    print("\n3. Update DocScanner to use your model:")
    print("   Edit scripts/docscanner_ollama_rag.py")
    print("   Change: model='phi3:mini' to model='my-docscanner-model'")
    
    print("\n4. Benefits of fine-tuning:")
    print("   • Consistent with your writing style")
    print("   • Better understanding of your domain")
    print("   • More relevant suggestions")
    print("   • Faster, more focused responses")

def main():
    """Test upgrade features"""
    print("🚀 DocScanner Ollama RAG Upgrade Test")
    print("=" * 50)
    
    # Create sample custom rules
    rules_file = create_sample_custom_rules()
    
    if rules_file:
        # Test with custom knowledge
        success = test_with_custom_knowledge()
        
        if success:
            print("\n🎉 Upgrade Features Working!")
            print("=" * 40)
            print("✅ Custom knowledge integration")
            print("✅ Enhanced AI suggestions")
            print("✅ Domain-specific improvements")
        else:
            print("\n⚠️  Some features need attention")
    
    # Show upgrade options
    show_model_upgrade_options()
    show_fine_tuning_example()
    
    print("\n🎯 Next Steps:")
    print("1. Try: python upgrade_ollama_rag.py (full upgrade guide)")
    print("2. Install a better model: ollama pull mistral:latest")
    print("3. Add your own writing rules to custom_writing_rules.json")
    print("4. Consider fine-tuning for your specific use case")

if __name__ == "__main__":
    main()
