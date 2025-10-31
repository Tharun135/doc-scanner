"""
Test the document-first routing fix with the minimal server
"""

import requests
import json

def test_routing_fix():
    """Test if our routing fix works"""
    print("🚀 Testing Document-First AI Routing Fix")
    print("=" * 60)
    
    # Test the exact case from the user's report
    test_data = {
        'feedback': 'passive voice detected',
        'sentence': 'The installation steps are demonstrated in a video at the following link:',
        'document_type': 'user_manual'
    }
    
    try:
        print("📡 Sending test request...")
        response = requests.post(
            'http://localhost:5001/ai_suggestion',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            method = result.get('method', 'unknown')
            confidence = result.get('confidence', 'unknown')
            
            print(f"✅ Request successful!")
            print(f"📊 Method: {method}")
            print(f"📊 Confidence: {confidence}")
            
            # Check if it's using document-first methods
            if method in ['document_first', 'advanced_rag', 'ollama_enhanced', 'intelligent_suggestion']:
                print(f"🎉 SUCCESS! Using document-first method: '{method}'")
                print("✅ This means smart_rule_based and smart_fallback are now backup only!")
                return True
            elif method in ['smart_rule_based', 'smart_fallback']:
                print(f"❌ STILL USING OLD METHOD: '{method}'")
                print("🔧 Need to investigate why document-first isn't being used")
                return False
            else:
                print(f"⚠️  Unknown method: '{method}' - investigating...")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_server_status():
    """Check server status"""
    try:
        response = requests.get('http://localhost:5001/test_status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("📊 Server Status:")
            print(f"   Intelligent AI Available: {status.get('intelligent_ai_available')}")
            print(f"   Enhanced AI Available: {status.get('enhanced_ai_available')}")
            print(f"   Mock Documents: {status.get('mock_documents')}")
            print(f"   Routing Fix Applied: {status.get('routing_fix_applied')}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Document-First AI Routing")
    print("************************************************************")
    
    # Check server status first
    if test_server_status():
        print("\n" + "=" * 60)
        # Test the routing
        success = test_routing_fix()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ROUTING FIX SUCCESSFUL!")
            print("🎯 Your AI now uses document-first system instead of smart_rule_based/smart_fallback")
        else:
            print("❌ ROUTING FIX NEEDS MORE WORK")
            print("🔧 The system is still using old methods")
    else:
        print("❌ Server not ready - check if test_server_minimal.py is running")
    
    print("\n✅ Test completed!")