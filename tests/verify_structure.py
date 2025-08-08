#!/usr/bin/env python3
"""
PROJECT STRUCTURE VERIFICATION
Verify that the new organized structure is working correctly.
"""

import os
from app.llamaindex_ai import llamaindex_ai_engine

def verify_project_structure():
    """Verify the new project structure is in place and working."""
    
    print("🔍 VERIFYING DOC SCANNER PROJECT STRUCTURE")
    print("=" * 50)
    
    # Check core directories
    core_directories = [
        "app",
        "style_guides", 
        "chroma_db",
        "static",
        "docs"
    ]
    
    print("\n📁 Core Directories:")
    for directory in core_directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - MISSING")
    
    # Check core files
    core_files = [
        "app/llamaindex_ai.py",
        "app/ai_improvement.py",
        "improve_knowledge_db.py",
        "requirements.txt",
        ".env"
    ]
    
    print("\n📄 Core Files:")
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
    
    # Check style guides
    print("\n📚 Style Guides:")
    style_guides_path = "style_guides"
    if os.path.exists(style_guides_path):
        style_files = [f for f in os.listdir(style_guides_path) 
                      if f.endswith(('.md', '.txt')) and not f.lower().startswith('readme')]
        
        if style_files:
            for file in style_files:
                print(f"✅ style_guides/{file}")
        else:
            print("⚠️  No style guides found (add .md or .txt files to style_guides/)")
    else:
        print("❌ style_guides/ directory missing")
    
    # Test AI system
    print("\n🤖 AI System Status:")
    try:
        status = llamaindex_ai_engine.get_system_status()
        print(f"✅ System Type: {status.get('system_type', 'Unknown')}")
        print(f"✅ Model: {status.get('model', 'Unknown')}")
        print(f"✅ Database: {status.get('database_type', 'Unknown')}")
        print(f"✅ Cost: {status.get('cost', 'Unknown')}")
        
        # Test suggestion generation
        test_text = "The report was written by the team yesterday."
        result = llamaindex_ai_engine.generate_suggestion(
            feedback_text="passive voice detected",
            sentence_context=test_text
        )
        
        if result and result.get('suggestion'):
            print(f"✅ AI Suggestions: Working")
            print(f"   📝 Test: '{test_text}'")
            print(f"   💡 Suggestion: '{result['suggestion']}'")
        else:
            print("⚠️  AI Suggestions: No response")
            
    except Exception as e:
        print(f"❌ AI System Error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 STRUCTURE VERIFICATION COMPLETE")
    
    # Calculate completeness
    total_checks = len(core_directories) + len(core_files) + 1  # +1 for AI system
    passed_checks = 0
    
    for directory in core_directories:
        if os.path.exists(directory):
            passed_checks += 1
    
    for file_path in core_files:
        if os.path.exists(file_path):
            passed_checks += 1
    
    try:
        status = llamaindex_ai_engine.get_system_status()
        if status:
            passed_checks += 1
    except:
        pass
    
    completeness = (passed_checks / total_checks) * 100
    print(f"🎯 Structure Completeness: {completeness:.0f}%")
    
    if completeness >= 90:
        print("🎉 Project structure is EXCELLENT!")
    elif completeness >= 70:
        print("✅ Project structure is GOOD!")
    else:
        print("⚠️  Project structure needs attention")
    
    print("\n🚀 Ready for enhanced AI-powered writing assistance!")

if __name__ == "__main__":
    verify_project_structure()
