#!/usr/bin/env python3
"""
Debug script to test RAG dashboard directly
"""

import sys
import os
sys.path.append('.')

from app import create_app

def test_rag_dashboard():
    """Test the RAG dashboard route directly"""
    try:
        # Create app
        app = create_app()
        socketio = app.socketio
        
        # Test client
        with app.test_client() as client:
            print("Testing RAG dashboard route...")
            response = client.get('/rag/dashboard')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS - Dashboard route is working!")
                print(f"Response length: {len(response.data)} bytes")
            else:
                print("❌ ERROR - Dashboard route failed!")
                print(f"Response data: {response.data.decode('utf-8')[:500]}...")
                
            return response.status_code == 200
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_dashboard()