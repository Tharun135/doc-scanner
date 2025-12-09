"""
Test the specific passive voice issue mentioned by the user
"""

from complete_integration import DocScannerAI

def test_specific_issue():
    """Test the specific passive voice issue: 'Delete the languages that are not needed.'"""
    
    print("🔍 Testing Specific Passive Voice Issue")
    print("=" * 50)
    
    # Initialize AI system
    ai = DocScannerAI()
    
    # Test the problematic sentence
    test_sentence = "Delete the languages that are not needed."
    issue_type = "Passive voice"
    
    print(f"Testing sentence: '{test_sentence}'")
    print(f"Issue type: {issue_type}")
    print()
    
    # Get AI suggestion
    result = ai.get_smart_suggestion(test_sentence, issue_type)
    
    print("📋 Results:")
    print("-" * 20)
    print(f"Success: {result['success']}")
    print(f"Original: '{result['original']}'")
    print(f"Corrected: '{result['corrected']}'")
    print(f"Explanation: {result['explanation']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Source: {result['source']}")
    print(f"Processing time: {result['processing_time']:.3f}s")
    
    # Test other similar constructions
    similar_sentences = [
        "Remove the files that are not used.",
        "Delete items that are unnecessary.", 
        "Click the button that is highlighted.",
        "Select options that are available.",
        "The issue was resolved by the developer."  # Classic passive
    ]
    
    print(f"\n🧪 Testing Similar Constructions:")
    print("-" * 40)
    
    for sentence in similar_sentences:
        result = ai.get_smart_suggestion(sentence, "Passive voice")
        print(f"\nOriginal:  '{sentence}'")
        print(f"Fixed:     '{result['corrected']}'")
        print(f"Confidence: {result['confidence']:.1%} | Source: {result['source']}")

if __name__ == "__main__":
    test_specific_issue()