# Test upload to FastAPI
Write-Host "Testing FastAPI Upload" -ForegroundColor Cyan
Write-Host ""

# Check if server is running
Write-Host "1. Checking server status..." -NoNewline
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
    Write-Host " Server is running" -ForegroundColor Green
} catch {
    Write-Host " Server not responding" -ForegroundColor Red
    Write-Host "Please start the server first: python run_fastapi.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2. Finding test document..." -NoNewline

# Find or create a test file
$testFile = ".\test_document.txt"
if (-not (Test-Path $testFile)) {
    "This is a test document for FastAPI upload testing.`n`nThe document contains multiple paragraphs to ensure proper chunking." | Out-File -FilePath $testFile -Encoding UTF8
}
Write-Host " Found $testFile" -ForegroundColor Green

Write-Host ""
Write-Host "3. Uploading document..." -NoNewline

# Upload the file
$boundary = [System.Guid]::NewGuid().ToString()
$fileContent = [System.IO.File]::ReadAllBytes((Resolve-Path $testFile).Path)
$fileName = Split-Path $testFile -Leaf

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: text/plain",
    "",
    [System.Text.Encoding]::UTF8.GetString($fileContent),
    "--$boundary--"
) -join "`r`n"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/upload" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host " Success!" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host ""
        Write-Host "Response:" -ForegroundColor Cyan
        Write-Host "  File ID: $($data.file_id)" -ForegroundColor White
        Write-Host "  Chunks: $($data.chunks_ingested)" -ForegroundColor White
        Write-Host ""
        Write-Host "All tests passed!" -ForegroundColor Green
    }
} catch {
    Write-Host " Failed" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
}
