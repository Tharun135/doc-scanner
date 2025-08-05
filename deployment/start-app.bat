@echo off
echo Starting Doc-Scanner Application...
echo.
echo ========================================
echo   Doc-Scanner - AI Writing Assistant
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

REM Navigate to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install requirements if they don't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Start the application
echo.
echo Starting Doc-Scanner on http://localhost:5000
echo.
echo ==========================================
echo  🚀 App is running! 
echo  📱 Open browser: http://localhost:5000
echo  🛑 Press Ctrl+C to stop the server
echo ==========================================
echo.

python run.py

echo.
echo Application stopped.
pause
