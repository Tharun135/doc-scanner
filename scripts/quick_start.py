"""
Auto-start Doc-Scanner with browser opening
This version automatically opens your default browser
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path

def start_app_with_browser():
    """Start the app and open browser when ready."""
    
    print("🚀 Starting Doc-Scanner...")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Start the Flask app
    try:
        app_process = subprocess.Popen(
            [sys.executable, 'run.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Server starting...")
        print("🌐 Opening browser in 3 seconds...")
        
        # Wait a bit for server to start, then open browser
        def open_browser_delayed():
            time.sleep(3)
            webbrowser.open('http://localhost:5000')
            print("📱 Browser opened! You can close this window.")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        # Wait for the process to complete
        app_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        app_process.terminate()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    start_app_with_browser()
