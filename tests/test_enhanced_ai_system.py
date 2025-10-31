#!/usr/bin/env python3

"""
Test the enhanced AI suggestion system with advanced RAG enabled.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from ai_improvement import get_enhanced_ai_suggestion

def test_enhanced_ai_suggestions():
    """Test enhanced AI suggestions with RAG system."""
    
    print("🧪 Testing Enhanced AI Suggestions with RAG System")
    print("=" * 60)
    
    test_cases = [
        {
            "feedback": "Avoid passive voice in sentence: 'The configuration options are displayed.'",
            "sentence": "The configuration options are displayed.",
            "expected_quality": "Should provide specific active voice conversion"
        },
        {
            "feedback": "Consider breaking this long sentence into shorter ones.",
            "sentence": "The system provides comprehensive documentation, detailed configuration options, and extensive troubleshooting guides to help users navigate the complex setup process and resolve any issues that may arise during implementation.",
            "expected_quality": "Should provide specific sentence splitting suggestions"
        },
        {
            "feedback": "Check use of adverb: 'accordingly'",
            "sentence": "Configure the credentials accordingly.",
            "expected_quality": "Should suggest specific replacement for 'accordingly'"
        },
        {
            "feedback": "Use active voice instead of passive voice.",
            "sentence": "The file was created by the system.",
            "expected_quality": "Should convert to 'The system created the file'"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['sentence']}")
        print(f"   Expected: {test_case['expected_quality']}")
        
        result = get_enhanced_ai_suggestion(
            feedback_text=test_case['feedback'],
            sentence_context=test_case['sentence'],
            document_type="technical",
            writing_goals=["clarity", "active_voice", "conciseness"]
        )
        
        if result:
            suggestion = result.get('suggestion', '')
            method = result.get('method', 'unknown')
            confidence = result.get('confidence', 'unknown')
            
            print(f"   Method: {method}")
            print(f"   Confidence: {confidence}")
            print(f"   Original: '{test_case['sentence']}'")
            print(f"   Suggestion: '{suggestion}'")
            
            # Analyze quality
            if suggestion and suggestion != test_case['sentence']:
                if method.startswith('advanced_rag'):
                    print("   ✅ EXCELLENT: Using advanced RAG system")
                elif method.startswith('rag_'):
                    print("   ✅ GOOD: Using legacy RAG system")  
                elif method == 'smart_passive_conversion' or method == 'smart_rule_based':
                    print("   ⚠️  OK: Using smart rules (RAG unavailable)")
                else:
                    print("   ⚠️  BASIC: Using fallback system")
            else:
                print("   ❌ POOR: No meaningful improvement provided")
        else:
            print("   ❌ FAILED: No result returned")
    
    print(f"\n{'='*60}")
    print("Test completed! Check which AI system is being used.")

if __name__ == "__main__":
    test_enhanced_ai_suggestions()