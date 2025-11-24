# DocScanner Docker Quick Start (Windows PowerShell)
# Run this script to quickly start DocScanner with Docker

Write-Host "DocScanner Docker Quick Start" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Docker is running" -ForegroundColor Green
Write-Host ""

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[ERROR] docker-compose.yml not found. Run this script from the project root." -ForegroundColor Red
    exit 1
}

# Ask user what to do
Write-Host "What would you like to do?" -ForegroundColor Yellow
Write-Host "1. Start DocScanner (build if needed)"
Write-Host "2. Stop DocScanner"
Write-Host "3. View logs"
Write-Host "4. Clean up (stop and remove containers)"
Write-Host "5. Full reset (remove everything including data)"
Write-Host "6. Check service health"
Write-Host ""

$choice = Read-Host "Enter choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting DocScanner..." -ForegroundColor Cyan
        docker-compose up -d --build
        
        Write-Host ""
        Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        Write-Host ""
        Write-Host "[OK] DocScanner is starting up!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access points:" -ForegroundColor Cyan
        Write-Host "   - DocScanner UI:  http://localhost:5000" -ForegroundColor White
        Write-Host "   - ChromaDB:       http://localhost:8000" -ForegroundColor White
        Write-Host "   - Ollama API:     http://localhost:11434" -ForegroundColor White
        Write-Host ""
        Write-Host "View logs:  docker-compose logs -f" -ForegroundColor Gray
        Write-Host "Stop:       docker-compose stop" -ForegroundColor Gray
        Write-Host ""
        
        # Ask if user wants to view logs
        $viewLogs = Read-Host "View logs now? (y/n)"
        if ($viewLogs -eq "y") {
            docker-compose logs -f
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Stopping DocScanner..." -ForegroundColor Yellow
        docker-compose stop
        Write-Host "[OK] Services stopped" -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "Viewing logs (Ctrl+C to exit)..." -ForegroundColor Cyan
        docker-compose logs -f
    }
    
    "4" {
        Write-Host ""
        Write-Host "Cleaning up containers..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "[OK] Containers removed. Data volumes preserved." -ForegroundColor Green
    }
    
    "5" {
        Write-Host ""
        Write-Host "WARNING: This will delete ALL data including:" -ForegroundColor Red
        Write-Host "   - Uploaded documents" -ForegroundColor Yellow
        Write-Host "   - ChromaDB embeddings" -ForegroundColor Yellow
        Write-Host "   - Ollama models" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "Are you SURE? Type 'yes' to confirm"
        
        if ($confirm -eq "yes") {
            Write-Host ""
            Write-Host "Removing everything..." -ForegroundColor Red
            docker-compose down -v
            Write-Host "All containers and volumes removed" -ForegroundColor Green
        } else {
            Write-Host "Cancelled" -ForegroundColor Yellow
        }
    }
    
    "6" {
        Write-Host ""
        Write-Host "Checking service health..." -ForegroundColor Cyan
        Write-Host ""
        
        # Check web service
        try {
            $webResponse = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 5 -UseBasicParsing
            Write-Host "[OK] Web Service: Healthy" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Web Service: Unhealthy or not running" -ForegroundColor Red
        }
        
        # Check ChromaDB
        try {
            $chromaResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/heartbeat" -TimeoutSec 5 -UseBasicParsing
            Write-Host "[OK] ChromaDB: Healthy" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] ChromaDB: Unhealthy or not running" -ForegroundColor Red
        }
        
        # Check Ollama
        try {
            $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -UseBasicParsing
            Write-Host "[OK] Ollama: Healthy" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Ollama: Unhealthy or not running" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "Container Status:" -ForegroundColor Cyan
        docker-compose ps
    }
    
    default {
        Write-Host "[ERROR] Invalid choice" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
