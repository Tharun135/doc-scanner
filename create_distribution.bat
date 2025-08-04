@echo off
echo Creating Doc-Scanner distribution package...
echo.

REM Create distribution folder
if not exist "dist" mkdir dist

REM Copy essential files
xcopy /E /I /Y "app" "dist\app"
xcopy /E /I /Y "agent" "dist\agent"
xcopy /E /I /Y "vscode-extension" "dist\vscode-extension"

copy "run.py" "dist\"
copy "requirements.txt" "dist\"
copy "start-app.bat" "dist\"
copy "launcher.py" "dist\"
copy "quick_start.py" "dist\"
copy "create_shortcut.py" "dist\"
copy ".env" "dist\"
copy "readme.md" "dist\"

REM Create setup instructions
echo Creating setup instructions...
(
echo # Doc-Scanner Setup Instructions
echo.
echo ## Quick Start:
echo 1. Double-click `start-app.bat` to start the application
echo 2. Open your browser to http://localhost:5000
echo 3. Upload documents to analyze writing quality
echo.
echo ## Alternative Methods:
echo - Double-click `launcher.py` for GUI launcher
echo - Run `python create_shortcut.py` to create desktop shortcut
echo.
echo ## Requirements:
echo - Python 3.8 or higher
echo - Internet connection for AI features
echo.
echo ## Support:
echo If you encounter issues, contact [your-email@company.com]
) > "dist\SETUP_INSTRUCTIONS.txt"

REM Create a simple installer
(
echo @echo off
echo echo Setting up Doc-Scanner...
echo.
echo REM Check Python
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Python not found. Please install Python 3.8+
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Install requirements
echo echo Installing dependencies...
echo pip install -r requirements.txt
echo.
echo REM Create desktop shortcut
echo echo Creating desktop shortcut...
echo python create_shortcut.py
echo.
echo echo Setup complete! You can now use Doc-Scanner.
echo pause
) > "dist\setup.bat"

echo.
echo ✅ Distribution package created in 'dist' folder!
echo 📦 You can now share the 'dist' folder with others.
echo.
pause
