# Quick Start Script for FastAPI
# Run this to install and start FastAPI in one command

Write-Host "=" -ForegroundColor Cyan
Write-Host "🚀 Doc Scanner FastAPI Quick Start" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create one first: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Check if FastAPI is installed
try {
    python -c "import fastapi" 2>$null
    $fastApiInstalled = $?
} catch {
    $fastApiInstalled = $false
}

if (-not $fastApiInstalled) {
    Write-Host "📥 Installing FastAPI dependencies..." -ForegroundColor Yellow
    pip install -r fastapi_requirements.txt
    
    Write-Host "📥 Downloading NLTK data..." -ForegroundColor Yellow
    python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.fastapi.example .env
    Write-Host "✅ Created .env file (you can customize it later)" -ForegroundColor Green
}

# Run validation tests
Write-Host ""
Write-Host "🧪 Running validation tests..." -ForegroundColor Yellow
python test_fastapi_setup.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" -ForegroundColor Green
    Write-Host "✅ All tests passed! Starting FastAPI server..." -ForegroundColor Green
    Write-Host "=" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 API Documentation will be available at:" -ForegroundColor Cyan
    Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Start the server
    python run_fastapi.py
} else {
    Write-Host ""
    Write-Host "=" -ForegroundColor Red
    Write-Host "❌ Validation tests failed!" -ForegroundColor Red
    Write-Host "=" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors above before starting the server." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Cyan
    Write-Host "  - pip install -r fastapi_requirements.txt --upgrade" -ForegroundColor White
    Write-Host "  - python -c 'import nltk; nltk.download(""punkt"")'" -ForegroundColor White
    exit 1
}
