#!/usr/bin/env python3
"""
Simple Integration Example: Click On → Click Rule
Ready-to-use integration for your existing DocScanner system
"""
import re

def fix_click_on_usage(text: str) -> str:
    """
    Simple function to fix 'click on' → 'click' in text.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with 'click on' changed to 'click'
        
    Examples:
        >>> fix_click_on_usage("Click on the button")
        'Click the button'
        >>> fix_click_on_usage("Please click on Save")  
        'Please click Save'
    """
    # Pattern matches 'click on' with word boundaries, case insensitive
    pattern = re.compile(r'\bclick\s+on\b', re.IGNORECASE)
    
    def replace_func(match):
        # Preserve original capitalization
        matched = match.group(0)
        if matched[0].isupper():
            return "Click"
        else:
            return "click"
    
    return pattern.sub(replace_func, text)


def process_document_sentences(sentences: list) -> dict:
    """
    Process a list of sentences from document scanning.
    
    Args:
        sentences: List of sentences to process
        
    Returns:
        Dict with processing results
    """
    results = {
        "processed": [],
        "changed": 0,
        "unchanged": 0,
        "total": len(sentences)
    }
    
    for sentence in sentences:
        original = sentence
        fixed = fix_click_on_usage(sentence)
        
        results["processed"].append({
            "original": original,
            "fixed": fixed,
            "changed": fixed != original
        })
        
        if fixed != original:
            results["changed"] += 1
        else:
            results["unchanged"] += 1
    
    return results


# Example usage in your existing system
def demo_simple_integration():
    """Demo how to integrate into your existing DocScanner."""
    
    # Sample sentences that might come from your document scanner
    sample_sentences = [
        "Click on the Submit button to continue.",
        "To save your work, click on the Save icon.",
        "Click on Settings in the menu.",
        "Users can click on Help for assistance.", 
        "Please click on Next to proceed.",
        "Click the button to start.",  # Already correct
        "The process will start automatically."  # No click instruction
    ]
    
    print("🔧 Simple Click On → Click Rule Demo")
    print("=" * 50)
    
    results = process_document_sentences(sample_sentences)
    
    print(f"📊 Processing Results:")
    print(f"   Total sentences: {results['total']}")
    print(f"   Changed: {results['changed']}")
    print(f"   Unchanged: {results['unchanged']}")
    print(f"   Success rate: {results['changed']/results['total']*100:.1f}%")
    
    print(f"\n📝 Detailed Results:")
    for i, result in enumerate(results["processed"], 1):
        if result["changed"]:
            print(f"   {i}. ✅ '{result['original']}'")
            print(f"      → '{result['fixed']}'")
        else:
            print(f"   {i}. ➡️  '{result['original']}' (no change)")
    
    # Example of how you'd integrate this into your existing pipeline
    print(f"\n🔄 Integration Example:")
    print("```python")
    print("# In your existing DocScanner pipeline:")
    print("def improve_sentence(sentence):")
    print("    # Step 1: Apply click on → click fix")
    print("    improved = fix_click_on_usage(sentence)")
    print("    ")
    print("    # Step 2: Apply your other existing rules") 
    print("    # improved = apply_other_rules(improved)")
    print("    ")
    print("    # Step 3: Return improved sentence")
    print("    return improved")
    print("```")


if __name__ == "__main__":
    demo_simple_integration()
