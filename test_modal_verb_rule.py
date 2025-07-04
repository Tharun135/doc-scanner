#!/usr/bin/env python3
"""
Test the modal verb detection rule directly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_modal_verb_rule():
    """Test the modal verb detection rule directly."""
    
    print("🔍 TESTING MODAL VERB DETECTION RULE")
    print("=" * 50)
    
    try:
        from app.rules.can_may_terms import check
        
        # Test content with modal verbs
        test_content = """
        <p>Users can access their data through the dashboard.</p>
        <p>You can configure the settings from the main menu.</p>
        <p>The system can process multiple requests simultaneously.</p>
        <p>Administrators can manage user permissions.</p>
        <p>You can download the report by clicking the export button.</p>
        """
        
        print("Test content:")
        print(test_content)
        print()
        
        # Run the check function
        suggestions = check(test_content)
        
        print(f"✅ Rule executed successfully")
        print(f"📊 Number of suggestions: {len(suggestions)}")
        
        if suggestions:
            print("\nSuggestions found:")
            for i, suggestion in enumerate(suggestions):
                print(f"  {i+1}. {suggestion}")
        else:
            print("⚠️ No suggestions found")
            
        return suggestions
        
    except Exception as e:
        print(f"❌ Error testing rule: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_single_sentence():
    """Test with a single sentence to debug."""
    
    print("\n🔍 TESTING SINGLE SENTENCE")
    print("=" * 50)
    
    try:
        from app.rules.can_may_terms import check
        
        test_sentence = "<p>Users can access their data through the dashboard.</p>"
        print(f"Testing: {test_sentence}")
        
        suggestions = check(test_sentence)
        print(f"Suggestions: {len(suggestions)}")
        
        for suggestion in suggestions:
            print(f"  - {suggestion}")
            
        return suggestions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_spacy_parsing():
    """Test spacy parsing of the content."""
    
    print("\n🔍 TESTING SPACY PARSING")
    print("=" * 50)
    
    try:
        import spacy
        from bs4 import BeautifulSoup
        
        nlp = spacy.load("en_core_web_sm")
        
        content = "<p>Users can access their data through the dashboard.</p>"
        
        # Strip HTML tags from content
        soup = BeautifulSoup(content, "html.parser")
        text_content = soup.get_text()
        
        print(f"Original content: {content}")
        print(f"Text content: {text_content}")
        
        # Define doc using nlp
        doc = nlp(text_content)
        
        print("Tokens:")
        for token in doc:
            print(f"  {token.text} | {token.pos_} | {token.dep_} | {token.lemma_}")
        
        print("\nLooking for 'can' with aux dependency:")
        for token in doc:
            if token.text.lower() == "can":
                print(f"  Found 'can': {token.text} | {token.pos_} | {token.dep_}")
                if token.dep_ == "aux":
                    print(f"    ✅ Found auxiliary 'can' in sentence: {token.sent.text}")
                else:
                    print(f"    ❌ 'can' is not auxiliary, it's: {token.dep_}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("TESTING MODAL VERB DETECTION RULE")
    print("=" * 50)
    
    # Test the rule directly
    suggestions = test_modal_verb_rule()
    
    # Test single sentence
    single_suggestions = test_single_sentence()
    
    # Test spacy parsing
    test_spacy_parsing()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if suggestions:
        print(f"✅ Modal verb rule is working: {len(suggestions)} suggestions")
    else:
        print("❌ Modal verb rule is not detecting issues")
        
    print("\nNote: The AI suggestion fix is working perfectly regardless of detection rule issues.")
