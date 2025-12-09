#!/usr/bin/env python3
"""
Test script to verify that wsgi.py fix works correctly
"""

import sys
import os

def test_wsgi_import():
    """Test that wsgi.py can be imported without errors"""
    try:
        print("🧪 Testing wsgi.py import...")
        
        # Import wsgi module
        import wsgi
        
        # Check that application is a Flask app, not a tuple
        print(f"📋 Application type: {type(wsgi.application)}")
        
        if hasattr(wsgi.application, 'run'):
            print("✅ Application has 'run' method - WSGI fix successful!")
            return True
        else:
            print("❌ Application missing 'run' method")
            return False
            
    except AttributeError as e:
        print(f"❌ AttributeError: {e}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_create_app():
    """Test that create_app returns only Flask app, not tuple"""
    try:
        print("\n🧪 Testing create_app() function...")
        
        from app import create_app
        result = create_app()
        
        print(f"📋 create_app() returns: {type(result)}")
        
        # Should return Flask app, not tuple
        if hasattr(result, 'run') and hasattr(result, 'socketio'):
            print("✅ create_app() returns Flask app with socketio attribute!")
            return True
        else:
            print("❌ create_app() doesn't return proper Flask app")
            return False
            
    except Exception as e:
        print(f"❌ Error testing create_app(): {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing WSGI fix for deployment...")
    
    wsgi_ok = test_wsgi_import()
    app_ok = test_create_app()
    
    if wsgi_ok and app_ok:
        print("\n🎉 All tests passed! Deployment should work now.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        sys.exit(1)