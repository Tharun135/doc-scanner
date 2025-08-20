#!/usr/bin/env python3
print("Starting debug...")

import sys
print(f"Python path: {sys.path}")

try:
    sys.path.append('.')
    from app.rules.title_utils import is_title_or_heading
    print("Successfully imported is_title_or_heading")
    
    result = is_title_or_heading("1. Basic Configuration", "<p>1. Basic Configuration</p>")
    print(f"Test result: {result}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(f"Traceback: {traceback.format_exc()}")

print("Debug completed.")
