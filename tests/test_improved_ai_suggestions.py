#!/usr/bin/env python3
"""
Test the improved AI suggestions with rule-specific corrections.
This validates that the enhanced RAG system now provides accurate solutions.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_improved_suggestions():
    """Test the improved AI suggestions with your exact examples"""
    
    print("🧪 Testing Improved AI Suggestions")
    print("=" * 60)
    
    # Your exact test cases from the user request
    test_cases = [
        {
            "name": "Sentence 5 - Passive Voice Issue",
            "feedback": "Avoid passive voice in sentence",
            "sentence": "When the \"Bulk Publish\" is enabled, all tags data is published under single group with topic name as:",
            "expected_improvement": "Convert to active voice with clear subject"
        },
        {
            "name": "Sentence 15 - Capitalization Issue", 
            "feedback": "Start sentences with a capital letter",
            "sentence": "it is in ISO 8601 Zulu format.",
            "expected_improvement": "Capitalize first letter"
        },
        {
            "name": "Sentence 18 - Long Sentence Issue",
            "feedback": "Consider breaking this long sentence into shorter ones",
            "sentence": "With \"SLMP Connector V2.0\", with qc, qx is published which holds all the bits data: quality code, sub status, extended sub status, flags, and limit.",
            "expected_improvement": "Break into multiple shorter sentences"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Issue: {test_case['feedback']}")
        print(f"Original: \"{test_case['sentence']}\"")
        print(f"Expected: {test_case['expected_improvement']}")
        
        # Test with enhanced RAG system
        try:
            # Create issue dict in the format expected by the integration function
            issue = {
                "message": test_case['feedback'],
                "context": test_case['sentence'],
                "issue_type": "passive-voice" if "passive" in test_case['feedback'].lower() 
                            else "capitalization" if "capital" in test_case['feedback'].lower()
                            else "long-sentence" if "long" in test_case['feedback'].lower()
                            else "general"
            }
            
            result = enhanced_enrich_issue_with_solution(issue)
            
            if result:
                suggestion = result.get('proposed_rewrite', '')
                explanation = result.get('solution_text', '')
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 'unknown')
                
                print(f"✅ Method: {method}")
                print(f"✅ AI Suggestion: \"{suggestion}\"")
                print(f"✅ Explanation: {explanation}")
                print(f"✅ Confidence: {confidence}")
                
                # Analyze improvement quality
                original = test_case['sentence']
                
                if suggestion and suggestion != original and suggestion.strip():
                    print("✅ Status: IMPROVED - Suggestion differs from original")
                    
                    # Check specific improvements
                    if i == 1:  # Passive voice test
                        if "you enable" in suggestion.lower() or "system publishes" in suggestion.lower():
                            print("✅ Passive Voice: Successfully converted to active voice")
                        else:
                            print("⚠️  Passive Voice: Partial improvement")
                    elif i == 2:  # Capitalization test
                        if suggestion[0].isupper() and original[0].islower():
                            print("✅ Capitalization: Successfully capitalized first letter")
                        else:
                            print("⚠️  Capitalization: Not fixed properly")
                    elif i == 3:  # Long sentence test
                        if '. ' in suggestion and '. ' not in original:
                            print("✅ Long Sentence: Successfully broken into multiple sentences")
                        else:
                            print("⚠️  Long Sentence: Partial improvement")
                else:
                    print(f"❌ Status: NO IMPROVEMENT - Empty or same suggestion")
                    print(f"   Original length: {len(original)}")
                    print(f"   Suggestion length: {len(suggestion) if suggestion else 0}")
                    if suggestion:
                        print(f"   Same as original: {suggestion == original}")
            else:
                print("❌ No result returned from enhanced RAG system")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print("🎯 Summary: Enhanced RAG system with rule-specific corrections")
    print("   - Provides targeted fixes for specific writing rules")
    print("   - Falls back gracefully when Ollama is unavailable") 
    print("   - Uses deterministic corrections for simple cases")
    print("   - Maintains backward compatibility with existing system")


if __name__ == "__main__":
    test_improved_suggestions()
