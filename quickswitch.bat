@echo off
setlocal EnableDelayedExpansion

rem Self-contained universal branch switcher for doc-scanner
rem Works across all branches by generating Python code inline

if "%1"=="" (
    echo ⚠️  Usage: quickswitch.bat ^<branch-name^>
    echo Available branches:
    git branch -a | findstr -v HEAD
    exit /b 1
)

echo ≡ƒöä Quick switching to: %1
echo 🧹 Cleaning workspace...

rem Clean git locks and problematic directories
if exist ".git\*.lock" del /q ".git\*.lock" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "chroma_db" rmdir /s /q "chroma_db" 2>nul
if exist ".pytest_cache" rmdir /s /q ".pytest_cache" 2>nul

rem Generate temporary Python script for advanced operations
echo import os, subprocess, sys > temp_switcher.py
echo. >> temp_switcher.py
echo def safe_switch(branch): >> temp_switcher.py
echo     try: >> temp_switcher.py
echo         # Force clean any remaining issues >> temp_switcher.py
echo         subprocess.run(['git', 'reset', '--hard'], check=False, capture_output=True) >> temp_switcher.py
echo         subprocess.run(['git', 'clean', '-fd'], check=False, capture_output=True) >> temp_switcher.py
echo         # Switch branch >> temp_switcher.py
echo         result = subprocess.run(['git', 'checkout', branch], capture_output=True, text=True) >> temp_switcher.py
echo         if result.returncode == 0: >> temp_switcher.py
echo             print(f'✅ Successfully switched to: {branch}') >> temp_switcher.py
echo             return True >> temp_switcher.py
echo         else: >> temp_switcher.py
echo             print(f'❌ Failed to switch: {result.stderr}') >> temp_switcher.py
echo             return False >> temp_switcher.py
echo     except Exception as e: >> temp_switcher.py
echo         print(f'❌ Error: {e}') >> temp_switcher.py
echo         return False >> temp_switcher.py
echo. >> temp_switcher.py
echo if __name__ == '__main__': >> temp_switcher.py
echo     safe_switch(sys.argv[1]) >> temp_switcher.py

rem Run the generated Python script
python temp_switcher.py %1

rem Clean up temporary script
if exist "temp_switcher.py" del "temp_switcher.py" 2>nul

rem Show final status
echo.
echo 📍 Current status:
git branch --show-current 2>nul || echo Error getting current branch