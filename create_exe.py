"""
Create EXE file for Doc-Scanner using PyInstaller
This script will bundle the entire app into a single executable
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_spec_file():
    """Create a custom spec file for better control."""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add all Python files
a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('agent', 'agent'),
        ('.env', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'spacy',
        'en_core_web_sm',
        'flask',
        'werkzeug',
        'jinja2',
        'google.generativeai',
        'langchain',
        'chromadb',
        'beautifulsoup4',
        'PyPDF2',
        'docx',
        'markdown',
        'textstat',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/favicon.ico'  # Add an icon if you have one
)
'''
    
    with open('doc_scanner.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Spec file created: doc_scanner.spec")

def build_exe():
    """Build the EXE file."""
    print("🔨 Building EXE file... This may take a few minutes...")
    
    try:
        # Use the spec file for building
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "doc_scanner.spec"
        ])
        
        print("✅ EXE file created successfully!")
        print("📁 Location: dist/DocScanner.exe")
        print("📦 File size: ~200-300 MB (includes Python runtime)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building EXE: {e}")
        print("💡 Try the alternative method below")

def create_simple_launcher_exe():
    """Create a simpler launcher EXE."""
    launcher_script = '''
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 Starting Doc-Scanner...")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Start the app
    try:
        print("📡 Starting server...")
        process = subprocess.Popen([sys.executable, "run.py"])
        
        # Wait a moment and open browser
        time.sleep(3)
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:5000")
        
        print("✅ Doc-Scanner is running!")
        print("🛑 Close this window to stop the server")
        
        # Wait for process
        process.wait()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
    
    with open('launcher_simple.py', 'w') as f:
        f.write(launcher_script)
    
    # Build simple launcher
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name=DocScannerLauncher",
        "launcher_simple.py"
    ])
    
    print("✅ Simple launcher EXE created: dist/DocScannerLauncher.exe")

def main():
    """Main function to create EXE."""
    print("🎯 Creating EXE file for Doc-Scanner")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Try to build full EXE
    try:
        build_exe()
    except:
        print("🔄 Trying alternative simple launcher...")
        create_simple_launcher_exe()
    
    print("\n🎉 EXE creation completed!")
    print("\n📋 Distribution package should include:")
    print("  • DocScanner.exe (or DocScannerLauncher.exe)")
    print("  • app/ folder")
    print("  • agent/ folder") 
    print("  • .env file")
    print("  • requirements.txt")
    
    print("\n💡 Recipients can run the EXE without installing Python!")

if __name__ == "__main__":
    main()
