#!/usr/bin/env python3

"""
DIAGNOSTIC TOOL: Find exact cause of unclear issue display
This will help identify why you're seeing unclear issues like "Issue: appropriate"
"""

import requests
import time
import json
import subprocess
import os
import sys

def start_server_and_test():
    """Start server and run comprehensive diagnostic"""
    
    print("🔍 COMPREHENSIVE DIAGNOSTIC FOR ISSUE DISPLAY")
    print("=" * 65)
    
    # Start server
    print("🚀 Starting server for testing...")
    server_process = None
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, "run.py"], 
            cwd=os.getcwd(),
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("⏳ Waiting for server startup...")
        time.sleep(6)
        
        # Test the exact content that causes your issue
        test_content = """Security guidelines for usage of USB sticks within shop floor are applied.
The system uses appropriate security measures.
Customer is responsible for configuring the application security settings.
The system is installed in an environment that ensures physical access is limited to authorized maintenance personnel.
System includes hardware, firmware and operating system components.
Centralized IT security components (Active Directory, Centralized IT Logging Server) are provided and configured.
The operator personnel accessing the system is well trained.
The operator uses appropriate access controls.
Operator is responsible for configuring the PLCs with appropriate security settings."""
        
        print(f"📤 Testing with content that causes your reported issues...")
        
        # Upload and analyze
        files = {'file': ('diagnostic_test.txt', test_content)}
        response = requests.post('http://localhost:5000/upload', files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful! Analyzing response...")
            
            sentences = result.get('sentences', [])
            print(f"\n📊 DETAILED ANALYSIS OF {len(sentences)} SENTENCES:")
            print("=" * 65)
            
            problematic_issues = []
            good_issues = []
            
            for i, sentence in enumerate(sentences, 1):
                feedback_items = sentence.get('feedback', [])
                sentence_text = sentence.get('sentence', '')
                
                if feedback_items:
                    print(f"\n📝 Sentence {i} ({len(feedback_items)} issues):")
                    print(f"   Text: '{sentence_text[:80]}...'")
                    
                    for j, issue in enumerate(feedback_items, 1):
                        issue_text = issue.get('text', '')
                        issue_message = issue.get('message', '')
                        
                        print(f"\n   Issue {j}:")
                        print(f"     🔤 TEXT field: '{issue_text}'")
                        print(f"     💬 MESSAGE field: '{issue_message}'")
                        print(f"     📍 Position: {issue.get('start', 0)}-{issue.get('end', 0)}")
                        
                        # Categorize the issue
                        if not issue_message or len(issue_message.strip()) < 10:
                            problematic_issues.append({
                                'sentence': i,
                                'issue': j,
                                'text': issue_text,
                                'message': issue_message,
                                'problem': 'Missing or very short message'
                            })
                            print(f"     ❌ PROBLEM: {problematic_issues[-1]['problem']}")
                        elif issue_text == issue_message:
                            problematic_issues.append({
                                'sentence': i,
                                'issue': j,
                                'text': issue_text,
                                'message': issue_message,
                                'problem': 'Text and message are identical'
                            })
                            print(f"     ⚠️  WARNING: {problematic_issues[-1]['problem']}")
                        elif len(issue_text) < 20 and len(issue_message) > 20:
                            good_issues.append({
                                'sentence': i,
                                'text': issue_text,
                                'message': issue_message
                            })
                            print(f"     ✅ GOOD: Short text with explanatory message")
                        else:
                            good_issues.append({
                                'sentence': i,
                                'text': issue_text,
                                'message': issue_message
                            })
                            print(f"     ✅ GOOD: Has proper text and message")
            
            # Summary
            print(f"\n📈 DIAGNOSTIC SUMMARY:")
            print("=" * 65)
            print(f"✅ Good issues: {len(good_issues)}")
            print(f"❌ Problematic issues: {len(problematic_issues)}")
            
            if problematic_issues:
                print(f"\n🔍 PROBLEMATIC ISSUES DETAILS:")
                for issue in problematic_issues:
                    print(f"  Sentence {issue['sentence']}: '{issue['text']}' - {issue['problem']}")
            
            if good_issues:
                print(f"\n✅ EXAMPLE OF GOOD ISSUE:")
                good_example = good_issues[0]
                print(f"  Text: '{good_example['text']}'")
                print(f"  Message: '{good_example['message']}'")
                print(f"  Display should be: 'Issue: {good_example['message']}'")
            
            # Check if the issues match what you reported
            print(f"\n🎯 COMPARISON WITH YOUR REPORTED ISSUES:")
            print("=" * 65)
            
            your_reported_issues = [
                "Security guidelines for usage of USB sticks within shop floor are applied",
                "appropriate",
                "Customer is responsible for configuring the applic...",
                "The system is installed in an environment that ensures physical access is limited to authorized main...",
                "hardware, firmware and operating",
                "Centralized IT security components (Active Directory, Centralized IT Logging Server) are provided an...",
                "The operator personnel accessing the system is wel...",
                "appropriate",
                "Operator is responsible for configuring the PLCs w..."
            ]
            
            detected_texts = []
            for sentence in sentences:
                for issue in sentence.get('feedback', []):
                    detected_texts.append(issue.get('text', ''))
            
            print(f"Your reported issues: {len(your_reported_issues)}")
            print(f"Detected issue texts: {len(detected_texts)}")
            
            matches = 0
            for reported in your_reported_issues:
                for detected in detected_texts:
                    if detected.startswith(reported[:20]) or reported.startswith(detected[:20]):
                        matches += 1
                        break
            
            print(f"Matches: {matches}/{len(your_reported_issues)}")
            
            if matches > len(your_reported_issues) * 0.7:
                print("✅ CONFIRMED: This reproduces your issue!")
                print("\n🔧 THE SOLUTION:")
                print("The frontend should display issue.message, not issue.text")
                print("Your browser/client is showing the TEXT field instead of MESSAGE field")
            else:
                print("❓ Different issues detected than you reported")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up server
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
                print("\n🔄 Server stopped")
            except:
                server_process.kill()
                print("\n🔄 Server force-stopped")

if __name__ == "__main__":
    start_server_and_test()
