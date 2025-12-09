#!/usr/bin/env python3
"""
Quick test to verify spaCy max length fix works
"""
import spacy

def test_spacy_large_text():
    """Test that we can process large text with spaCy"""
    print("Loading spaCy model...")
    
    # Load and configure spaCy the same way as the application
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 2000000  # 2MB limit
    
    print(f"spaCy max_length set to: {nlp.max_length:,} characters")
    
    # Create a large text (1.3 MB)
    large_text = "This is a test sentence. " * 50000  # About 1.25 MB
    
    print(f"Test text length: {len(large_text):,} characters")
    
    try:
        # Try to process the large text
        doc = nlp(large_text)
        sentences = list(doc.sents)
        
        print(f"✅ SUCCESS: Processed {len(sentences):,} sentences from large text")
        print(f"✅ No spaCy E088 error occurred!")
        
        # Test a specific rule function like the app would use
        from app.rules.vague_terms import check
        
        print("\nTesting actual vague_terms rule with large text...")
        suggestions = check(large_text)
        print(f"✅ SUCCESS: vague_terms.check returned {len(suggestions)} suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_spacy_large_text()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")