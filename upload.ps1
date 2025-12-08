# Easy Upload Script - Drag and drop your file here!
param(
    [Parameter(Mandatory=$false)]
    [string]$FilePath
)

Write-Host ""
Write-Host "📤 FastAPI Document Uploader" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Check server
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ FastAPI server is not running!" -ForegroundColor Red
    Write-Host "Please start it first: python run_fastapi.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Get file path
if (-not $FilePath) {
    Write-Host "Please drag and drop your file here, or enter the path:" -ForegroundColor Yellow
    $FilePath = Read-Host "File path"
}

# Remove quotes if present
$FilePath = $FilePath.Trim('"')

# Check file exists
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
    exit 1
}

$file = Get-Item $FilePath
Write-Host "📄 File: $($file.Name)" -ForegroundColor Cyan
Write-Host "📏 Size: $([math]::Round($file.Length / 1KB, 2)) KB" -ForegroundColor Cyan
Write-Host ""

# Upload
Write-Host "⏳ Uploading..." -ForegroundColor Yellow

try {
    $result = curl.exe -X POST http://localhost:8000/upload `
        -F "file=@$FilePath" `
        -s -w "`n%{http_code}"
    
    $lines = $result -split "`n"
    $statusCode = $lines[-1]
    $body = $lines[0..($lines.Length-2)] -join "`n"
    
    if ($statusCode -eq "200") {
        Write-Host "✅ Upload successful!" -ForegroundColor Green
        Write-Host ""
        
        $data = $body | ConvertFrom-Json
        Write-Host "📊 Results:" -ForegroundColor Cyan
        Write-Host "  File ID: $($data.file_id)" -ForegroundColor White
        Write-Host "  Chunks created: $($data.chunks_ingested)" -ForegroundColor White
        Write-Host "  Format: $($data.file_format)" -ForegroundColor White
        Write-Host ""
        Write-Host "✨ Your document is now searchable!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Test it:" -ForegroundColor Cyan
        Write-Host "  http://localhost:8000/docs" -ForegroundColor Yellow
        Write-Host "  → Go to 'Query' section" -ForegroundColor Gray
        Write-Host "  → Try searching for content from your document" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Upload failed (HTTP $statusCode)" -ForegroundColor Red
        Write-Host $body
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
