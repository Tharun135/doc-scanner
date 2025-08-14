#!/usr/bin/env python3
"""Test the sentence extraction with complex formatting."""

import sys
sys.path.append('.')

from app import create_app
import os
import json

# Create the app
app = create_app()

# Test with Flask test client
with app.test_client() as client:
    with open('test_formatting_document.html', 'rb') as test_file:
        response = client.post('/upload', data={'file': test_file})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.get_json()
            print(f"\n=== SENTENCE EXTRACTION RESULTS ===")
            print(f"Total sentences found: {len(json_data.get('sentences', []))}")
            
            for i, sent in enumerate(json_data.get('sentences', [])):
                print(f"\nSentence {i+1}:")
                print(f"  Plain text: {sent.get('sentence', '')}")
                print(f"  HTML context: {sent.get('html_context', '')}")
                print(f"  Feedback items: {len(sent.get('feedback', []))}")
                
            print(f"\n=== DOCUMENT CONTENT ===")
            # Show a snippet of the HTML content
            content = json_data.get('content', '')
            print(f"Content length: {len(content)} characters")
            
        else:
            print(f"Error Response: {response.get_json()}")

print("\nTest completed!")
