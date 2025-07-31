# Doc-Scanner PowerShell Launcher
# Right-click and "Run with PowerShell" to start the application

Write-Host "
========================================
   Doc-Scanner - AI Writing Assistant  
========================================
" -ForegroundColor Cyan

Write-Host "🚀 Starting Doc-Scanner Application..." -ForegroundColor Green

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\activate.bat") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\activate.bat"
}

# Install requirements if needed
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "
==========================================
  🌐 Starting server on http://localhost:5000
  📱 Your browser should open automatically
  🛑 Press Ctrl+C to stop the server
==========================================
" -ForegroundColor Green

# Start the application and open browser
Start-Process "http://localhost:5000" -ErrorAction SilentlyContinue
python run.py

Write-Host "
Application stopped. Press Enter to exit..." -ForegroundColor Yellow
Read-Host
