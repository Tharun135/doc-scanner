"""
Demo: How to See RAG-Based Solutions in Your App
This script shows you exactly where and how RAG solutions appear.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_rag_in_action():
    """Show how RAG provides solutions in the web interface."""
    
    print("🎯 RAG-Based Solutions in Your Doc Scanner App")
    print("=" * 60)
    
    print("\n🔍 WHERE TO SEE RAG SOLUTIONS:")
    print("1. Web Interface: http://127.0.0.1:5000")
    print("2. Upload any document (.docx, .pdf, .md, .txt)")
    print("3. Click on any red-highlighted issue")
    print("4. Click 'AI Suggestion' button")
    print("5. See RAG-powered solution with examples!")
    
    print("\n📋 WHAT YOU'LL SEE IN THE RAG SOLUTION:")
    
    # Test the RAG system directly
    try:
        from app.rules.rag_main import get_rag_suggestion
        
        test_cases = [
            {
                "issue": "passive voice detected",
                "sentence": "The bug was fixed by the developer.",
                "category": "grammar"
            },
            {
                "issue": "wordy phrase detected",
                "sentence": "In order to complete this task, we need to...",
                "category": "clarity"
            },
            {
                "issue": "non-inclusive language",
                "sentence": "Hey guys, let's start the meeting.",
                "category": "accessibility"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n🔧 Example {i}: {case['issue']}")
            print(f"   Sentence: \"{case['sentence']}\"")
            
            rag_response = get_rag_suggestion(
                issue_text=case['issue'],
                sentence_context=case['sentence'],
                category=case['category']
            )
            
            print(f"   📖 RAG Solution Preview:")
            solution = rag_response.get('suggestion', 'No solution')
            lines = solution.split('\n')[:3]  # First 3 lines
            for line in lines:
                if line.strip():
                    print(f"       {line.strip()}")
            print(f"       ... (full solution in web interface)")
            print(f"   🎯 Source: {rag_response.get('source', 'Unknown')}")
            print(f"   ⭐ Confidence: {rag_response.get('confidence', 0.0)}")
    
    except Exception as e:
        print(f"❌ Error testing RAG: {e}")
    
    print(f"\n" + "=" * 60)
    print("🚀 STEP-BY-STEP: See RAG Solutions in Action")
    print("=" * 60)
    
    steps = [
        "1. Open http://127.0.0.1:5000 in your browser",
        "2. Upload a document with writing issues",
        "3. Look for RED highlighted text (detected issues)",
        "4. Click on any red-highlighted sentence",
        "5. Click the 'AI Suggestion' button",
        "6. See your RAG-powered solution with:",
        "   • ✅ Specific explanation of the issue",
        "   • 🔧 Step-by-step solution",
        "   • 📝 Before/After examples",
        "   • 💡 Writing best practices",
        "   • 📚 Source from knowledge base"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n🎯 SAMPLE DOCUMENT TO TEST:")
    print("=" * 60)
    
    sample_text = """
# Test Document

The report was completed by the team. In order to improve performance, 
we need to optimize the database. Hey guys, this is pretty awesome! 
The code was written, the tests were executed, and the deployment was done.
This solution is really, really, really good for performance.
"""
    
    print("Copy this text into a .txt file and upload it:")
    print("-" * 40)
    print(sample_text)
    print("-" * 40)
    print("Expected RAG suggestions:")
    print("• Passive voice → Active voice conversion")
    print("• Wordy phrases → Concise alternatives") 
    print("• Inclusive language → Professional alternatives")
    print("• Repetitive words → Varied vocabulary")
    
    print(f"\n🏆 RESULT: Expert writing guidance powered by your RAG system!")

if __name__ == "__main__":
    demo_rag_in_action()
