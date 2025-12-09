"""
Simple Integration Example - DocScanner + RAG + Ollama
=====================================================

This script shows how to integrate the RAG solution generator
with your existing DocScanner flagging system.
"""

from ollama_rag_integration import OllamaRagSolutionGenerator, FlaggedIssue, AIResponse
import json

def process_docscanner_results(flagged_sentences):
    """
    Process results from your DocScanner and generate AI solutions
    
    Args:
        flagged_sentences: List of dicts with 'sentence' and 'issue' keys
        
    Returns:
        List of solutions with corrected sentences and explanations
    """
    
    # Initialize the RAG solution generator
    generator = OllamaRagSolutionGenerator()
    
    # Convert to FlaggedIssue objects
    flagged_issues = []
    for item in flagged_sentences:
        flagged_issues.append(FlaggedIssue(
            sentence=item['sentence'],
            issue=item['issue'],
            line_number=item.get('line_number'),
            severity=item.get('severity', 'medium')
        ))
    
    # Generate AI solutions
    print(f"🔄 Processing {len(flagged_issues)} flagged issues...")
    solutions = generator.generate_batch_solutions(flagged_issues)
    
    # Return formatted results
    results = []
    for solution in solutions:
        results.append({
            'original': solution.original_sentence,
            'corrected': solution.corrected_sentence,
            'explanation': solution.explanation,
            'issue_type': solution.issue_type,
            'confidence': solution.confidence
        })
    
    return results

def demo_integration():
    """Demo showing the complete workflow"""
    
    print("🚀 DocScanner AI Integration Demo")
    print("=" * 40)
    
    # Simulate DocScanner output (replace with your actual flagging results)
    docscanner_results = [
        {
            "sentence": "The application runs diagnostics and reports errors, and then logs them into the system automatically.",
            "issue": "Long sentence",
            "line_number": 15,
            "severity": "medium"
        },
        {
            "sentence": "The issue was resolved by the developer yesterday.",
            "issue": "Passive voice",
            "line_number": 23,
            "severity": "low"
        },
        {
            "sentence": "The system works fine and everything is good.",
            "issue": "Vague terms",
            "line_number": 31,
            "severity": "high"
        },
        {
            "sentence": "installing the application",
            "issue": "Title capitalization",
            "line_number": 1,
            "severity": "low"
        }
    ]
    
    # Process with AI
    solutions = process_docscanner_results(docscanner_results)
    
    # Display results in a user-friendly format
    print(f"\n✅ Generated {len(solutions)} AI-powered solutions:\n")
    
    for i, solution in enumerate(solutions, 1):
        print(f"🔍 Issue #{i}: {solution['issue_type']}")
        print(f"   Original: \"{solution['original']}\"")
        print(f"   ✨ Improved: \"{solution['corrected']}\"")
        print(f"   💡 Why: {solution['explanation']}")
        print(f"   📊 Confidence: {solution['confidence']:.1%}")
        print()
    
    # Save to file for DocScanner UI integration
    with open('docscanner_ai_suggestions.json', 'w', encoding='utf-8') as f:
        json.dump(solutions, f, indent=2, ensure_ascii=False)
    
    print("💾 Saved suggestions to 'docscanner_ai_suggestions.json'")
    
    return solutions

# Integration functions for your existing codebase

def get_ai_suggestion_for_issue(sentence: str, issue_type: str) -> dict:
    """
    Get a single AI suggestion for a flagged sentence
    
    Use this function in your existing DocScanner code:
    
    suggestion = get_ai_suggestion_for_issue(
        "The issue was resolved by the developer.",
        "Passive voice"
    )
    print(suggestion['corrected'])  # "The developer resolved the issue."
    """
    generator = OllamaRagSolutionGenerator()
    
    flagged_issue = FlaggedIssue(sentence=sentence, issue=issue_type)
    solution = generator.generate_solution(flagged_issue)
    
    return {
        'corrected': solution.corrected_sentence,
        'explanation': solution.explanation,
        'confidence': solution.confidence,
        'success': solution.corrected_sentence != "AI service unavailable"
    }

def batch_process_flagged_content(document_issues: dict) -> dict:
    """
    Process an entire document's flagged issues
    
    Args:
        document_issues: {
            "document_name": "user_manual.md",
            "issues": [
                {"sentence": "...", "issue": "...", "line": 10},
                ...
            ]
        }
    
    Returns:
        Enhanced document_issues with AI suggestions
    """
    
    # Extract flagged sentences
    flagged_sentences = document_issues.get('issues', [])
    
    # Get AI solutions
    solutions = process_docscanner_results(flagged_sentences)
    
    # Add solutions back to the issues
    for i, issue in enumerate(flagged_sentences):
        if i < len(solutions):
            issue['ai_suggestion'] = solutions[i]
    
    return document_issues

if __name__ == "__main__":
    # Run the demo
    demo_integration()
    
    print("\n" + "="*50)
    print("🎯 INTEGRATION READY!")
    print("="*50)
    print()
    print("To integrate with your DocScanner:")
    print()
    print("1. Import the functions:")
    print("   from simple_integration import get_ai_suggestion_for_issue")
    print()
    print("2. When you flag an issue, get AI suggestion:")
    print("   suggestion = get_ai_suggestion_for_issue(sentence, issue_type)")
    print()
    print("3. Show user both the rule and AI solution:")
    print("   print(f'Rule: {rule_text}')")
    print("   print(f'AI Fix: {suggestion[\"corrected\"]}')")
    print("   print(f'Why: {suggestion[\"explanation\"]}')")