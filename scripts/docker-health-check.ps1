# DocScanner Docker Health Check Script
# Verifies all services are running correctly

Write-Host "🏥 DocScanner Health Check" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "1️⃣ Checking Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerRunning) {
    Write-Host "   ✅ Docker Desktop is running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker Desktop is NOT running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check container status
Write-Host "2️⃣ Checking container status..." -ForegroundColor Yellow
$containers = docker-compose ps --format json 2>$null | ConvertFrom-Json

if ($containers) {
    $webStatus = $containers | Where-Object { $_.Service -eq "web" }
    $chromaStatus = $containers | Where-Object { $_.Service -eq "chromadb" }
    $ollamaStatus = $containers | Where-Object { $_.Service -eq "ollama" }

    # Web service
    if ($webStatus -and $webStatus.State -eq "running") {
        Write-Host "   ✅ DocScanner Web App: Running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ DocScanner Web App: Not Running" -ForegroundColor Red
    }

    # ChromaDB
    if ($chromaStatus -and $chromaStatus.State -eq "running") {
        Write-Host "   ✅ ChromaDB: Running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ ChromaDB: Not Running" -ForegroundColor Red
    }

    # Ollama
    if ($ollamaStatus -and $ollamaStatus.State -eq "running") {
        Write-Host "   ✅ Ollama: Running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Ollama: Not Running" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ No containers are running" -ForegroundColor Red
    Write-Host "   Run 'docker-compose up -d' to start services" -ForegroundColor Yellow
}

Write-Host ""

# Check port availability
Write-Host "3️⃣ Checking ports..." -ForegroundColor Yellow

function Test-Port {
    param($Port, $ServiceName)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient("localhost", $Port)
        $connection.Close()
        Write-Host "   ✅ Port $Port ($ServiceName): Accessible" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ Port $Port ($ServiceName): Not Accessible" -ForegroundColor Red
        return $false
    }
}

$webPort = Test-Port -Port 5000 -ServiceName "Web App"
$chromaPort = Test-Port -Port 8000 -ServiceName "ChromaDB"
$ollamaPort = Test-Port -Port 11434 -ServiceName "Ollama"

Write-Host ""

# Test HTTP endpoints
Write-Host "4️⃣ Testing HTTP endpoints..." -ForegroundColor Yellow

if ($webPort) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Web App (http://localhost:5000): Responding" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ⚠️ Web App (http://localhost:5000): Not responding yet" -ForegroundColor Yellow
    }
}

if ($chromaPort) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v2/heartbeat" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ ChromaDB (http://localhost:8000): Responding" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ⚠️ ChromaDB (http://localhost:8000): Not responding yet" -ForegroundColor Yellow
    }
}

if ($ollamaPort) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Ollama (http://localhost:11434): Responding" -ForegroundColor Green
            
            # Check for available models
            $models = ($response.Content | ConvertFrom-Json).models
            if ($models) {
                Write-Host "      Available models: $($models.name -join ', ')" -ForegroundColor Gray
            } else {
                Write-Host "      No models installed yet (will download on first use)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "   ⚠️ Ollama (http://localhost:11434): Not responding yet" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check Docker volumes
Write-Host "5️⃣ Checking Docker volumes..." -ForegroundColor Yellow
$volumes = docker volume ls --filter "name=doc-scanner" --format "{{.Name}}" 2>$null
if ($volumes) {
    foreach ($volume in $volumes) {
        Write-Host "   ✅ Volume: $volume" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️ No volumes found (will be created on first run)" -ForegroundColor Yellow
}

Write-Host ""

# Check Docker networks
Write-Host "6️⃣ Checking Docker networks..." -ForegroundColor Yellow
$network = docker network ls --filter "name=docscanner-network" --format "{{.Name}}" 2>$null
if ($network) {
    Write-Host "   ✅ Network: $network" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ Network not found (will be created on first run)" -ForegroundColor Yellow
}

Write-Host ""

# Check logs for errors
Write-Host "7️⃣ Checking recent logs for errors..." -ForegroundColor Yellow
$recentErrors = docker-compose logs --tail=50 2>&1 | Select-String -Pattern "ERROR|Error|error|CRITICAL|FATAL" | Select-Object -First 5

if ($recentErrors) {
    Write-Host "   ⚠️ Found recent errors in logs:" -ForegroundColor Yellow
    foreach ($error in $recentErrors) {
        Write-Host "      $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "   Run 'docker-compose logs -f' to see full logs" -ForegroundColor Gray
} else {
    Write-Host "   ✅ No critical errors in recent logs" -ForegroundColor Green
}

Write-Host ""

# System resources
Write-Host "8️⃣ Checking system resources..." -ForegroundColor Yellow
$stats = docker stats --no-stream --format "{{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>$null
if ($stats) {
    Write-Host "   Container Stats:" -ForegroundColor Gray
    Write-Host "   Container                 CPU         Memory" -ForegroundColor Gray
    Write-Host "   ------------------------------------------------" -ForegroundColor Gray
    foreach ($stat in $stats) {
        Write-Host "   $stat" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️ No running containers to check" -ForegroundColor Yellow
}

Write-Host ""

# Overall summary
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "📊 Health Check Summary" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

$allHealthy = $webPort -and $chromaPort -and $ollamaPort

if ($allHealthy) {
    Write-Host ""
    Write-Host "✅ All systems operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access DocScanner at: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️ Some services are not running properly" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "   1. Check if Docker Desktop is running" -ForegroundColor White
    Write-Host "   2. Start services: docker-compose up -d" -ForegroundColor White
    Write-Host "   3. View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "   4. Restart services: docker-compose restart" -ForegroundColor White
    Write-Host "   5. Rebuild if needed: docker-compose build --no-cache" -ForegroundColor White
    Write-Host ""
}

Write-Host "📝 Useful commands:" -ForegroundColor Gray
Write-Host "   docker-compose ps          # View container status" -ForegroundColor DarkGray
Write-Host "   docker-compose logs -f     # View live logs" -ForegroundColor DarkGray
Write-Host "   docker-compose restart     # Restart all services" -ForegroundColor DarkGray
Write-Host "   docker-compose down        # Stop all services" -ForegroundColor DarkGray
Write-Host ""
