#!/usr/bin/env python3
"""Test the full upload workflow with detailed error tracking."""

import sys
sys.path.append('.')

from app import create_app
import os

# Create the app
app = create_app()

# Create a test file
test_content = """
<p>This is a simple test document. It contains <strong>bold text</strong> and other formatting.</p>
<p>This is another paragraph with a <a href="http://example.com">link</a> in the middle of the sentence.</p>
<p>Finally, this paragraph has an image: <img src="test.jpg" alt="test image"> in the sentence.</p>
"""

with open('test_simple_doc.html', 'w', encoding='utf-8') as f:
    f.write(test_content)

# Test with Flask test client
with app.test_client() as client:
    with open('test_simple_doc.html', 'rb') as test_file:
        response = client.post('/upload', data={'file': test_file})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Response length: {len(response.get_data())}")
            json_data = response.get_json()
            if json_data:
                print(f"Sentences found: {len(json_data.get('sentences', []))}")
                if 'sentences' in json_data:
                    for i, sent in enumerate(json_data['sentences'][:3]):  # Show first 3
                        print(f"Sentence {i}: {sent.get('sentence', '')[:50]}...")
        else:
            print(f"Error Response: {response.get_json()}")

# Clean up
if os.path.exists('test_simple_doc.html'):
    os.remove('test_simple_doc.html')
