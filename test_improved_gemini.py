#!/usr/bin/env python3
"""
Test the improved Gemini Answer functionality with specific sentence conversions
"""

import requests
import json

def test_passive_voice():
    """Test passive voice conversion"""
    print("=== TESTING PASSIVE VOICE CONVERSION ===")
    
    test_cases = [
        "These values are derived during the XSLT Transformation step in Model Maker.",
        "The document was written by the team.",
        "Mistakes were made by the management.",
        "The system will be updated by the IT department."
    ]
    
    for sentence in test_cases:
        try:
            response = requests.post('http://localhost:5000/ai_suggestion', 
                json={
                    'feedback': 'Passive voice detected',
                    'sentence': sentence,
                    'document_type': 'general'
                }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nOriginal: {sentence}")
                print(f"Gemini Answer: {result.get('gemini_answer', 'None')}")
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

def test_modal_verbs():
    """Test modal verb corrections"""
    print("\n=== TESTING MODAL VERB CORRECTIONS ===")
    
    test_cases = [
        ("You may use this feature", "Use 'can' instead of 'may'"),
        ("Users can access the system", "Use 'may' for formal permission")
    ]
    
    for sentence, feedback in test_cases:
        try:
            response = requests.post('http://localhost:5000/ai_suggestion', 
                json={
                    'feedback': feedback,
                    'sentence': sentence,
                    'document_type': 'general'
                }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nOriginal: {sentence}")
                print(f"Feedback: {feedback}")
                print(f"Gemini Answer: {result.get('gemini_answer', 'None')}")
        except Exception as e:
            print(f"Request failed: {e}")

def test_tense_conversion():
    """Test tense conversion"""
    print("\n=== TESTING TENSE CONVERSION ===")
    
    test_cases = [
        "The system will process the data automatically.",
        "Users went to the dashboard to check their status.",
        "The application was running smoothly."
    ]
    
    for sentence in test_cases:
        try:
            response = requests.post('http://localhost:5000/ai_suggestion', 
                json={
                    'feedback': 'Convert to simple present tense',
                    'sentence': sentence,
                    'document_type': 'general'
                }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nOriginal: {sentence}")
                print(f"Gemini Answer: {result.get('gemini_answer', 'None')}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Improved Gemini Answer Functionality\n")
    
    test_passive_voice()
    test_modal_verbs()
    test_tense_conversion()
    
    print("\n✅ Testing complete!")
