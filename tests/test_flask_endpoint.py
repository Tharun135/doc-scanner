#!/usr/bin/env python3

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the actual Flask endpoint
import requests

def test_flask_endpoint():
    """Test the actual Flask /ai_suggestion endpoint"""
    
    # Your exact case
    payload = {
        "feedback": "Avoid passive voice in sentence: 'The following requirement must be met:'",
        "sentence": "The following requirement must be met:",
        "document_type": "technical",
        "writing_goals": [],
        "option_number": 1
    }
    
    print("🔍 Testing Flask AI Suggestion Endpoint")
    print("=" * 60)
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        # Make request to Flask endpoint
        response = requests.post('http://localhost:5000/ai_suggestion', 
                               json=payload, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(json.dumps(result, indent=2))
            
            suggestion = result.get("suggestion", "")
            print(f"\nFinal suggestion from Flask: '{suggestion}'")
            
            # Check for title case
            words = suggestion.split()
            title_case_words = []
            for i, word in enumerate(words):
                if i > 0 and word and len(word) > 1 and word[0].isupper() and word[1:].islower():
                    if word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from']:
                        title_case_words.append(word)
            
            if title_case_words:
                print(f"⚠️ TITLE CASE DETECTED IN FLASK RESPONSE: {title_case_words}")
            else:
                print("✅ No title case issues in Flask response")
                
            # Test the formatAISuggestion function simulation
            print(f"\nTesting formatAISuggestion logic on: '{suggestion}'")
            test_format_logic(suggestion)
                
        else:
            print(f"❌ Flask error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_format_logic(suggestion_text):
    """Simulate the JavaScript formatAISuggestion function"""
    if not suggestion_text:
        return ''
    
    # Split by newlines
    lines = suggestion_text.split('\n')
    html_parts = []
    
    for line in lines:
        # JavaScript regex: /^([A-Z][A-Z_ \-]+):\s*(.*)$/i
        import re
        match = re.match(r'^([A-Z][A-Z_ \-]+):\s*(.*)$', line, re.IGNORECASE)
        if match:
            key = match.group(1)
            value = match.group(2)
            # Apply the title case transformation
            key_formatted = key.replace('_', ' ')
            # Apply title case: replace(/\b([a-z])/g, c => c.toUpperCase())
            key_formatted = re.sub(r'\b([a-z])', lambda m: m.group(1).upper(), key_formatted)
            html_parts.append(f"<strong>{key_formatted}:</strong> {value}")
            print(f"  ⚠️ Matched as KEY:VALUE - Key: '{key}' -> '{key_formatted}', Value: '{value}'")
        elif line.strip():
            html_parts.append(line)
            print(f"  ✅ Normal line: '{line}'")
    
    return ' '.join(html_parts) if html_parts else suggestion_text

if __name__ == "__main__":
    test_flask_endpoint()
