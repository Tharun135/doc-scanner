# Test Atomic Rules System
# Uploads test document to DocScanner and displays results

$testFile = "test_atomic_rules.md"
$uploadUrl = "http://localhost:8000/upload"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ATOMIC RULES SYSTEM - UPLOAD TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if file exists
if (-not (Test-Path $testFile)) {
    Write-Host "[ERROR] Test file not found: $testFile" -ForegroundColor Red
    exit 1
}

Write-Host "Test file: $testFile" -ForegroundColor White
Write-Host "Upload URL: $uploadUrl" -ForegroundColor White
Write-Host ""

# Check if server is running
try {
    Write-Host "Checking if server is running..." -ForegroundColor Yellow
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "[OK] Server is healthy!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Server not responding. Make sure Flask app is running." -ForegroundColor Red
    Write-Host "   Run: python run.py" -ForegroundColor Yellow
    exit 1
}

# Read file content
$fileContent = Get-Content $testFile -Raw -Encoding UTF8

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$testFile`"",
    "Content-Type: text/markdown$LF",
    $fileContent,
    "--$boundary--$LF"
) -join $LF

Write-Host "Uploading test document..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $uploadUrl -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyLines
    
    Write-Host "[OK] Upload successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ANALYSIS RESULTS" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $sentences = $response.sentences
    $report = $response.aggregated_report
    
    Write-Host "Summary:" -ForegroundColor White
    Write-Host "   Total Sentences: $($report.totalSentences)" -ForegroundColor White
    Write-Host "   Total Words: $($report.totalWords)" -ForegroundColor White
    Write-Host "   Quality Score: $($report.avgQualityScore)%" -ForegroundColor White
    Write-Host ""
    
    # Count violations by severity
    $errorCount = 0
    $warnCount = 0
    $infoCount = 0
    
    foreach ($sentence in $sentences) {
        if ($sentence.feedback) {
            foreach ($feedback in $sentence.feedback) {
                switch ($feedback.severity) {
                    "error" { $errorCount++ }
                    "warn" { $warnCount++ }
                    "info" { $infoCount++ }
                    default { $warnCount++ }
                }
            }
        }
    }
    
    Write-Host "Violations by Severity:" -ForegroundColor White
    Write-Host "   [ERROR] Errors (Must Fix): $errorCount" -ForegroundColor Red
    Write-Host "   [WARN] Warnings (Suggestions): $warnCount" -ForegroundColor Yellow
    Write-Host "   [INFO] Info (Hints): $infoCount" -ForegroundColor Cyan
    Write-Host ""
    
    # Show sample violations
    Write-Host "Sample Violations (First 5):" -ForegroundColor White
    Write-Host ""
    
    $count = 0
    foreach ($sentence in $sentences) {
        if ($sentence.feedback -and $count -lt 5) {
            foreach ($feedback in $sentence.feedback) {
                if ($count -ge 5) { break }
                
                $severityIcon = switch ($feedback.severity) {
                    "error" { "[ERROR]" }
                    "warn" { "[WARN]" }
                    "info" { "[INFO]" }
                    default { "[OTHER]" }
                }
                
                $sentenceText = $sentence.sentence
                if ($sentenceText.Length -gt 80) {
                    $sentenceText = $sentenceText.Substring(0, 77) + "..."
                }
                
                Write-Host "[$severityIcon $($feedback.severity.ToUpper())] $($feedback.rule_id)" -ForegroundColor White
                Write-Host "   Sentence: `"$sentenceText`"" -ForegroundColor Gray
                Write-Host "   Issue: $($feedback.message)" -ForegroundColor Gray
                if ($feedback.suggestion) {
                    Write-Host "   Suggestion: $($feedback.suggestion)" -ForegroundColor Gray
                }
                Write-Host ""
                
                $count++
            }
        }
    }
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[OK] TEST COMPLETE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "View full results in browser:" -ForegroundColor Yellow
    Write-Host "http://localhost:8000" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
