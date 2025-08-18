"""
Create Windows Desktop Shortcut for Doc-Scanner
Run this script once to create a desktop shortcut
"""

import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Get paths
        desktop = winshell.desktop()
        app_dir = Path(__file__).parent.absolute()
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(os.path.join(desktop, "Doc-Scanner.lnk"))
        shortcut.Targetpath = str(app_dir / "launcher.py")
        shortcut.WorkingDirectory = str(app_dir)
        shortcut.IconLocation = str(app_dir / "launcher.py")
        shortcut.Description = "Doc-Scanner - AI Writing Assistant"
        shortcut.save()
        
        print("✅ Desktop shortcut created successfully!")
        print(f"📍 Shortcut location: {desktop}")
        
    except ImportError:
        print("⚠️ Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell", "pywin32"])
        print("✅ Packages installed. Please run this script again.")
        
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        print("\n💡 Alternative: You can manually create a shortcut to launcher.py")

if __name__ == "__main__":
    create_desktop_shortcut()
    input("Press Enter to exit...")
