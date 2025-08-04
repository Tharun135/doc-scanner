"""
Fixed EXE creation script - simplified version without icon
"""

import subprocess
import sys
import os
from pathlib import Path

def create_simple_exe():
    """Create EXE using simple PyInstaller command."""
    try:
        print("🔨 Creating simple EXE...")
        
        # Simple PyInstaller command without icon
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                    # Single EXE file
            "--console",                    # Keep console window
            "--name=DocScanner",           # EXE name
            "--add-data=app;app",          # Include app folder
            "--add-data=agent;agent",      # Include agent folder
            "--hidden-import=flask",
            "--hidden-import=spacy", 
            "--hidden-import=beautifulsoup4",
            "run.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        print("✅ EXE created successfully!")
        print("📂 Check the 'dist' folder for DocScanner.exe")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating EXE: {e}")
        return False

def create_launcher_exe():
    """Create a simple launcher EXE."""
    launcher_script = """
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the directory where the EXE is located
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
    
    # Change to app directory
    os.chdir(app_dir)
    
    print("🚀 Starting Doc-Scanner...")
    print("📂 Working directory:", app_dir)
    
    # Run the app
    try:
        subprocess.run([sys.executable, "run.py"], check=True)
    except FileNotFoundError:
        print("❌ run.py not found. Make sure to copy all files with the EXE.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
"""
    
    # Write launcher script
    with open("launcher_exe.py", "w") as f:
        f.write(launcher_script)
    
    try:
        print("🔨 Creating launcher EXE...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console", 
            "--name=DocScannerLauncher",
            "launcher_exe.py"
        ]
        
        subprocess.check_call(cmd)
        print("✅ Launcher EXE created!")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Launcher EXE creation failed")
        return False
    finally:
        # Clean up
        if os.path.exists("launcher_exe.py"):
            os.remove("launcher_exe.py")

if __name__ == "__main__":
    print("🎯 Simple EXE Creator")
    print("=" * 30)
    
    # Try simple method first
    if create_simple_exe():
        print("\n🎉 Success! Your EXE is ready.")
    else:
        print("\n💡 Trying alternative launcher method...")
        if create_launcher_exe():
            print("\n🎉 Launcher EXE created successfully!")
        else:
            print("\n❌ Both methods failed. Try the GUI method instead.")
    
    input("\nPress Enter to exit...")
