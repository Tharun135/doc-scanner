#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.ai_improvement import ai_engine

# Test with our specific feedback that contains a rewrite
feedback_text = 'Consider rewriting to describe the action instead of using \'can\'. Original: "You can install Connector for IEC 61850 on all Industrial Edge devices you want to connect to your devices." → Suggested: "Install Connector for IEC 61850 on all Industrial Edge devices you want to connect to your devices."'

sentence = 'You can install Connector for IEC 61850 on all Industrial Edge devices you want to connect to your devices.'

print("Testing AI improvement system...")
print("Feedback:", feedback_text[:100] + "...")
print()

result = ai_engine.generate_smart_fallback_suggestion(feedback_text, sentence)
print("Result:", result)
print()
print("Method:", result.get('method'))
print("Confidence:", result.get('confidence'))
print("Suggestion:", result.get('suggestion'))
