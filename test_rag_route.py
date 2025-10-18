#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

try:
    from app import create_app
    app, socketio = create_app()
    
    print("Testing RAG dashboard route...")
    with app.test_client() as client:
        response = client.get('/rag/dashboard')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ RAG dashboard route working!")
            print(f"Response length: {len(response.data)} bytes")
        else:
            print(f"❌ Error: {response.status_code}")
            print("Response data:", response.data.decode('utf-8')[:500])
            
except Exception as e:
    print(f"❌ Error testing route: {e}")
    import traceback
    traceback.print_exc()