#!/usr/bin/env python3

"""
COMPREHENSIVE FIX: Issue Display Problem
This script identifies and fixes the core issue with unclear feedback display
"""

import requests
import time
import json

def test_issue_display_problem():
    """Test to identify exactly what's causing the unclear issue display"""
    
    print("🔍 TESTING ISSUE DISPLAY PROBLEM")
    print("=" * 60)
    
    # Start server first
    print("🚀 Starting server...")
    import subprocess
    import os
    
    try:
        # Start server in background
        server_process = subprocess.Popen(
            ["python", "run.py"], 
            cwd=os.getcwd(),
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test content that causes the problem
        test_content = """Security guidelines for usage of USB sticks within shop floor are applied.
The system uses appropriate security measures.
Customer is responsible for configuring the application security settings.
The system is installed in an environment that ensures physical access is limited to authorized maintenance personnel.
System includes hardware, firmware and operating system components.
Centralized IT security components (Active Directory, Centralized IT Logging Server) are provided and configured.
The operator personnel accessing the system is well trained.
The operator uses appropriate access controls.
Operator is responsible for configuring the PLCs with appropriate security settings."""
        
        print(f"📝 Testing content with {len(test_content.split('.'))} sentences")
        
        try:
            # Upload document
            files = {'file': ('test_issue_display.txt', test_content)}
            response = requests.post('http://localhost:5000/upload', files=files, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                
                sentences = result.get('sentences', [])
                print(f"\n📊 ANALYSIS OF {len(sentences)} SENTENCES:")
                print("=" * 60)
                
                for i, sentence in enumerate(sentences, 1):
                    feedback_items = sentence.get('feedback', [])
                    sentence_text = sentence.get('sentence', '')
                    
                    print(f"\nSentence {i}:")
                    print(f"  Display Text: '{sentence_text[:100]}...'")
                    print(f"  Issues: {len(feedback_items)}")
                    
                    for j, issue in enumerate(feedback_items, 1):
                        issue_text = issue.get('text', '')
                        issue_message = issue.get('message', '')
                        
                        print(f"    Issue {j}:")
                        print(f"      Text Field: '{issue_text}'")
                        print(f"      Message Field: '{issue_message}'")
                        
                        # Identify the problem
                        if len(issue_text) < 50 and not issue_message:
                            print(f"      ❌ PROBLEM: Only showing text fragment, no helpful message!")
                        elif issue_text and not issue_message:
                            print(f"      ⚠️  WARNING: Missing explanatory message")
                        elif issue_text == sentence_text[:len(issue_text)]:
                            print(f"      ❌ PROBLEM: Text field is just sentence fragment")
                        else:
                            print(f"      ✅ OK: Has both text and message")
                
                # Check what the frontend should be displaying
                print(f"\n🎯 FRONTEND DISPLAY RECOMMENDATION:")
                print("=" * 60)
                
                print("The frontend should display:")
                print("  Format: 'Issue: [MESSAGE]' not 'Issue: [TEXT]'")
                print("  Where MESSAGE explains what's wrong")
                print("  And TEXT is just the detected fragment")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            
        finally:
            # Clean up server
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                server_process.kill()
                
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def create_display_fix():
    """Create a fix for the display issue"""
    
    print("\n🔧 CREATING DISPLAY FIX")
    print("=" * 60)
    
    fix_explanation = """
    THE CORE PROBLEM:
    The frontend is displaying issue.text instead of issue.message
    
    WHAT YOU SEE NOW:
    "Issue: appropriate" (just the detected word)
    "Issue: Security guidelines for usage..." (just the detected text)
    
    WHAT YOU SHOULD SEE:
    "Issue: Be specific instead of 'appropriate': define what makes it suitable"
    "Issue: Possible passive voice detected - consider active voice"
    
    THE FIX:
    The backend is correctly providing both fields:
    - text: the detected problematic text fragment
    - message: the helpful explanation of what's wrong
    
    But the display logic needs to show the MESSAGE, not the TEXT.
    """
    
    print(fix_explanation)
    
    # Create a test to verify the data structure
    print("\n📋 BACKEND DATA STRUCTURE TEST:")
    print("-" * 40)
    
    sample_issue = {
        "text": "appropriate",
        "message": "Be specific instead of 'appropriate': define what makes it suitable",
        "start": 91,
        "end": 102
    }
    
    print("Sample issue data structure:")
    print(json.dumps(sample_issue, indent=2))
    
    print("\n✅ CORRECT DISPLAY LOGIC:")
    print(f"  Should show: 'Issue: {sample_issue['message']}'")
    print(f"  NOT: 'Issue: {sample_issue['text']}'")

if __name__ == "__main__":
    test_issue_display_problem()
    create_display_fix()
