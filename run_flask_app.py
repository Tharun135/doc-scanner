#!/usr/bin/env python
"""
Run Flask app with proper Python path setup
"""
import sys
import os

# Add necessary paths for imports
current_dir = os.getcwd()
sys.path.insert(0, current_dir)  # Add root directory
sys.path.insert(0, os.path.join(current_dir, 'app'))  # Add app directory

# Set Flask environment
os.environ['FLASK_APP'] = 'app.app'
os.environ['FLASK_ENV'] = 'development'

if __name__ == "__main__":
    # Import and run Flask app
    from app.app import main
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(main)
    
    print("🚀 Starting Flask app on http://localhost:5000")
    print("💡 Test the AI endpoint with: python test_flask_ai_endpoint.py")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
