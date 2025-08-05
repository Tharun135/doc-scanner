#!/usr/bin/env python3
"""
Test the full Doc-Scanner app with the new rewriting suggestions rule
"""

import requests
import json
import time

def test_app_with_rewriting_rule():
    """Test the Doc-Scanner app with rewriting suggestions."""
    
    # Test document with action verbs
    test_document = """
    Instructions for Setting Up the System
    
    The user clicks on the start button to begin the setup process.
    Next, they select the appropriate configuration from the dropdown menu.
    Then the system opens a new dialog window.
    The user types their credentials in the provided fields.
    Finally, they press the submit button to complete the setup.
    """
    
    print("🚀 Testing Doc-Scanner with Rewriting Suggestions Rule")
    print("=" * 60)
    print(f"📝 Test Document:\n{test_document}")
    print("=" * 60)
    
    try:
        # Send request to the app
        response = requests.post(
            'http://localhost:5000/analyze',
            json={'content': test_document},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            print(f"✅ App Response: {len(suggestions)} total suggestions found")
            
            # Filter for rewriting suggestions
            rewriting_suggestions = [
                s for s in suggestions 
                if any(keyword in str(s).lower() 
                      for keyword in ['manual_steps', 'imperative', 'click', 'select', 'rewrite'])
            ]
            
            if rewriting_suggestions:
                print(f"🎯 Found {len(rewriting_suggestions)} rewriting-related suggestions:")
                for i, suggestion in enumerate(rewriting_suggestions, 1):
                    print(f"{i}. {suggestion}")
            else:
                print("ℹ️ No specific rewriting suggestions found in response")
                print("📋 All suggestions:")
                for i, suggestion in enumerate(suggestions[:5], 1):  # Show first 5
                    print(f"{i}. {suggestion}")
                if len(suggestions) > 5:
                    print(f"   ... and {len(suggestions) - 5} more")
            
            return True
            
        else:
            print(f"❌ App returned error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Doc-Scanner app")
        print("💡 Make sure the app is running on http://localhost:5000")
        print("   Run: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        return False

def check_app_status():
    """Check if the Doc-Scanner app is running."""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Doc-Scanner Integration Test")
    print("=" * 40)
    
    # Check if app is running
    if check_app_status():
        print("✅ Doc-Scanner app is running")
        test_app_with_rewriting_rule()
    else:
        print("❌ Doc-Scanner app is not running")
        print("💡 To start the app, run: python run.py")
        print("   Then run this test again")
