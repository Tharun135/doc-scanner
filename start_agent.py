#!/usr/bin/env python3
"""
Simple launcher for the Document Review Agent
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    print("🚀 Document Review Agent starting...")
    print("📡 Flask server: http://localhost:5000")
    print("🔌 Agent API: http://localhost:5000/api/agent")
    print("⏹️  Press Ctrl+C to stop")
    
    app = create_app()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Document Review Agent stopped")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        sys.exit(1)
