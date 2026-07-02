# DocScanner Docker Distribution Script
# Creates a complete distribution package for testers

Write-Host "🐳 DocScanner Docker Distribution Creator" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$packageName = "docscanner-docker-distribution"
$packageDir = ".\dist\$packageName"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Create distribution directory
Write-Host "📁 Creating distribution directory..." -ForegroundColor Yellow
New-Item -Path $packageDir -ItemType Directory -Force | Out-Null

# Files to include
$filesToCopy = @(
    "docker-compose.yml",
    "Dockerfile",
    ".dockerignore"
)

Write-Host "📋 Copying essential files..." -ForegroundColor Yellow
foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $packageDir -Force
        Write-Host "  ✓ Copied $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Warning: $file not found" -ForegroundColor Red
    }
}

# Copy deployment files
Write-Host "📦 Copying deployment files..." -ForegroundColor Yellow
Copy-Item "deployment" -Destination "$packageDir\deployment" -Recurse -Force
Write-Host "  ✓ Copied deployment directory" -ForegroundColor Green

# Copy configuration
Write-Host "⚙️ Copying configuration..." -ForegroundColor Yellow
Copy-Item "config" -Destination "$packageDir\config" -Recurse -Force
Write-Host "  ✓ Copied config directory" -ForegroundColor Green

# Create .env file
Write-Host "🔧 Creating .env file..." -ForegroundColor Yellow
$envContent = @"
# DocScanner Environment Configuration

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-change-this-in-production

# Service URLs (internal Docker network)
OLLAMA_URL=http://ollama:11434
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000

# Logging
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO

# Application Settings
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=txt,pdf,docx,doc,rtf
"@

$envContent | Out-File -FilePath "$packageDir\.env" -Encoding UTF8
Write-Host "  ✓ Created .env file" -ForegroundColor Green

# Create README for distribution
Write-Host "📝 Creating distribution README..." -ForegroundColor Yellow
$readmeContent = @"
# DocScanner - Docker Distribution Package

## 🚀 Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- 10GB+ free disk space
- Ports 5000, 8000, and 11434 available

### 2. Pull Required Images
``````powershell
docker-compose pull
``````

This will download:
- ChromaDB (~750MB)
- Ollama (~5.8GB)
- DocScanner app (will be built)

### 3. Build the Application
``````powershell
docker-compose build --no-cache
``````

**Expected time:** 5-10 minutes

### 4. Start All Services
``````powershell
docker-compose up -d
``````

### 5. Access the Application
Open your browser: **http://localhost:5000**

### 6. Test the Application
1. Upload a document (TXT, PDF, or DOCX)
2. Click "Analyze Document"
3. Review detected issues
4. Click "Get AI Suggestion" for improvements

### 7. Stop the Services
``````powershell
docker-compose down
``````

---

## 📊 What's Running?

After \`docker-compose up -d\`:

| Service | Port | Purpose |
|---------|------|---------|
| DocScanner Web | 5000 | Main application interface |
| ChromaDB | 8000 | Vector database for RAG |
| Ollama | 11434 | LLM inference engine |

Check status:
``````powershell
docker-compose ps
``````

---

## 🔍 Viewing Logs

``````powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f chromadb
docker-compose logs -f ollama
``````

---

## ⚙️ Configuration

Edit \`.env\` file to customize:
- Port numbers
- Ollama model settings
- Flask environment
- Upload limits

---

## 🐛 Troubleshooting

### Containers keep restarting
``````powershell
docker-compose logs web
``````
Check for port conflicts or missing dependencies.

### Cannot access http://localhost:5000
``````powershell
docker-compose ps
``````
Ensure containers are "Up" and healthy.

### Build fails
``````powershell
docker-compose build --no-cache web
``````
Rebuild without cache to fix dependency issues.

### Out of disk space
``````powershell
docker system prune -a
``````
Clean up unused Docker resources.

---

## 📁 Directory Structure

``````
docscanner-docker-distribution/
├── docker-compose.yml      # Service orchestration
├── Dockerfile              # Application image build
├── .dockerignore          # Files to exclude from build
├── .env                   # Environment configuration
├── deployment/            # Requirements and configs
│   └── requirements.txt   # Python dependencies
├── config/                # Application configuration
│   └── *.json            # Rule configurations
└── README.md             # This file
``````

---

## 🔒 Security Notes

### For Testing (Local Use)
- Default configuration is suitable for local testing
- No authentication required
- Not exposed to internet

### For Production Deployment
1. Change SECRET_KEY in .env
2. Enable HTTPS with reverse proxy
3. Add authentication
4. Restrict network access
5. Regular security updates

---

## 📞 Support

For issues:
1. Check logs: \`docker-compose logs -f\`
2. Review troubleshooting section
3. Rebuild: \`docker-compose build --no-cache\`
4. Report issues to the development team

---

## 🎯 First-Time Ollama Setup

On first run, Ollama will automatically:
1. Start the inference service
2. Wait for document analysis request
3. Pull the phi3 model (~2.5GB) on first use
4. Cache the model for future use

**First AI suggestion will take 2-3 minutes** while model downloads.
Subsequent suggestions will be instant.

---

## 📈 Performance Tips

### Faster Startup
Pre-pull Ollama model:
``````powershell
docker exec -it docscanner-ollama ollama pull phi3:latest
``````

### Better Performance
- Allocate more RAM to Docker Desktop (Settings → Resources → Memory: 8GB+)
- Use SSD for Docker storage
- Enable GPU support if NVIDIA GPU available

### Monitor Resources
``````powershell
docker stats
``````

---

## ✅ Testing Checklist

Before reporting issues, verify:

- [ ] Docker Desktop is running
- [ ] All three containers are "Up"
- [ ] http://localhost:5000 loads
- [ ] Can upload a document
- [ ] Document analysis completes
- [ ] AI suggestions generate
- [ ] No errors in \`docker-compose logs\`

---

**Package Version:** 1.0
**Date:** $timestamp
**Docker Compose Version:** 3.8+
**Minimum Docker Desktop:** 4.0+

For detailed documentation, see: DOCKER_DISTRIBUTION_GUIDE.md
"@

$readmeContent | Out-File -FilePath "$packageDir\README.md" -Encoding UTF8
Write-Host "  ✓ Created README.md" -ForegroundColor Green

# Create startup script for Windows
Write-Host "🚀 Creating startup script..." -ForegroundColor Yellow
$startScript = @"
# DocScanner Quick Start Script
Write-Host "🐳 Starting DocScanner..." -ForegroundColor Cyan

# Check if Docker is running
`$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not `$dockerRunning) {
    Write-Host "❌ Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
Write-Host ""

# Pull images
Write-Host "📥 Pulling Docker images..." -ForegroundColor Yellow
docker-compose pull

# Build application
Write-Host "🏗️ Building DocScanner application..." -ForegroundColor Yellow
docker-compose build

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "✅ DocScanner is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Check status: docker-compose ps" -ForegroundColor Gray
Write-Host "📝 View logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "🛑 Stop services: docker-compose down" -ForegroundColor Gray
Write-Host ""

# Wait for services to be ready
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
docker-compose ps

Write-Host ""
Write-Host "Press any key to open DocScanner in your browser..." -ForegroundColor Cyan
pause

Start-Process "http://localhost:5000"
"@

$startScript | Out-File -FilePath "$packageDir\start-docscanner.ps1" -Encoding UTF8
Write-Host "  ✓ Created start-docscanner.ps1" -ForegroundColor Green

# Create stop script
Write-Host "🛑 Creating stop script..." -ForegroundColor Yellow
$stopScript = @"
# DocScanner Stop Script
Write-Host "🛑 Stopping DocScanner..." -ForegroundColor Yellow

docker-compose down

Write-Host "✅ DocScanner stopped successfully!" -ForegroundColor Green
pause
"@

$stopScript | Out-File -FilePath "$packageDir\stop-docscanner.ps1" -Encoding UTF8
Write-Host "  ✓ Created stop-docscanner.ps1" -ForegroundColor Green

# Copy documentation
Write-Host "📚 Copying documentation..." -ForegroundColor Yellow
if (Test-Path "docs\DOCKER_DISTRIBUTION_GUIDE.md") {
    Copy-Item "docs\DOCKER_DISTRIBUTION_GUIDE.md" -Destination $packageDir -Force
    Write-Host "  ✓ Copied Docker distribution guide" -ForegroundColor Green
}

# Create sample test documents
Write-Host "📄 Creating sample test documents..." -ForegroundColor Yellow
$sampleDir = "$packageDir\sample-documents"
New-Item -Path $sampleDir -ItemType Directory -Force | Out-Null

$samplePassive = @"
The system was tested by the engineers. The results were analyzed and the report was written. 
The findings were presented to the management team. Several improvements were recommended by the team.
"@

$samplePassive | Out-File -FilePath "$sampleDir\test-passive-voice.txt" -Encoding UTF8

$sampleLong = @"
The comprehensive analysis of the system architecture, which was conducted over a period of several weeks by multiple teams working in coordination with various stakeholders across different departments, revealed that there are numerous opportunities for optimization and improvement in both the performance metrics and the overall user experience, particularly in areas where the current implementation does not fully leverage the available technological capabilities.
"@

$sampleLong | Out-File -FilePath "$sampleDir\test-long-sentences.txt" -Encoding UTF8
Write-Host "  ✓ Created sample test documents" -ForegroundColor Green

# Create ZIP archive
Write-Host ""
Write-Host "📦 Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = ".\dist\$packageName-$timestamp.zip"
Compress-Archive -Path $packageDir -DestinationPath $zipPath -Force
Write-Host "  ✓ Created $zipPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Distribution package created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Package location:" -ForegroundColor Yellow
Write-Host "   $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "📁 Package contents:" -ForegroundColor Yellow
Write-Host "   • Docker Compose configuration" -ForegroundColor White
Write-Host "   • Dockerfile for application" -ForegroundColor White
Write-Host "   • Environment configuration" -ForegroundColor White
Write-Host "   • Deployment requirements" -ForegroundColor White
Write-Host "   • Startup/stop scripts" -ForegroundColor White
Write-Host "   • Complete documentation" -ForegroundColor White
Write-Host "   • Sample test documents" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Test the package locally" -ForegroundColor White
Write-Host "   2. Share the ZIP file with testers" -ForegroundColor White
Write-Host "   3. Provide the README.md instructions" -ForegroundColor White
Write-Host ""
Write-Host "📊 Package size:" -ForegroundColor Yellow
$size = (Get-Item $zipPath).Length / 1MB
Write-Host "   $([math]::Round($size, 2)) MB" -ForegroundColor White
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
