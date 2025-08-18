"""
Alternative EXE creation using auto-py-to-exe (GUI method)
"""

import subprocess
import sys

def install_auto2exe():
    """Install auto-py-to-exe for GUI-based EXE creation."""
    try:
        print("📦 Installing auto-py-to-exe...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "auto-py-to-exe"])
        print("✅ auto-py-to-exe installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install auto-py-to-exe")

def launch_auto2exe():
    """Launch the auto-py-to-exe GUI."""
    try:
        print("🎨 Launching auto-py-to-exe GUI...")
        subprocess.run([sys.executable, "-m", "auto_py_to_exe"])
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

def show_instructions():
    """Show instructions for using auto-py-to-exe."""
    instructions = """
    
🎯 AUTO-PY-TO-EXE INSTRUCTIONS:

1. In the GUI that opens:
   - Script Location: Browse to 'run.py'
   - One File: Select 'One File'
   - Console Window: Select 'Console Based'
   
2. Advanced Options:
   - Additional Files: Add these folders:
     * app (folder)
     * agent (folder)
     * .env (file)
   
3. Hidden Imports: Add these modules:
   - flask
   - spacy
   - beautifulsoup4
   - PyPDF2
   - docx
   - markdown
   - textstat
   - google.generativeai
   - langchain
   - chromadb
   
4. Click 'CONVERT .PY TO .EXE'

5. Find your EXE in the 'dist' folder!

📦 The resulting EXE will be ~200-300 MB but will run without Python installed.
    """
    print(instructions)

if __name__ == "__main__":
    print("🎨 Auto-py-to-exe EXE Creator")
    print("=" * 40)
    
    install_auto2exe()
    show_instructions()
    
    input("\nPress Enter to launch the GUI...")
    launch_auto2exe()
