#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import extract_formatted_sentence_html

# Test the fix directly
test_html = """<p>You can choose to set any project to Autostart mode by activating the <strong>Enable Autostart</strong> option.</p>"""

print("🧪 TESTING EXTRACT_FORMATTED_SENTENCE_HTML FIX")
print("=" * 50)
print(f"📄 Input HTML: {test_html}")
print()

sentences = extract_formatted_sentence_html(test_html)

print(f"🔍 RESULTS:")
print(f"📊 Total sentences: {len(sentences)}")
print()

for i, sentence in enumerate(sentences):
    print(f"Sentence {i+1}:")
    print(f"  📝 HTML: {sentence.get('html_segment', 'N/A')}")
    print(f"  📄 Plain: {sentence.get('sentence', 'N/A')}")
    print()

if len(sentences) == 1:
    plain_text = sentences[0].get('sentence', '')
    if "Enable Autostart" in plain_text and "activating the" in plain_text and "option." in plain_text:
        print("🎉 SUCCESS! The sentence was NOT split at formatting elements!")
        print("✅ extract_formatted_sentence_html is working correctly!")
    else:
        print("⚠️ Unexpected sentence content:")
        print(f"Content: {plain_text}")
else:
    print(f"❌ FAILED! Expected 1 sentence, got {len(sentences)}")
    print("The HTML processing is still splitting incorrectly.")
