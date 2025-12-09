# Setup Git Hooks for Documentation Quality Checks
# Run this script once to install the pre-commit hook

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Git Hooks Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$hooksDir = ".git\hooks"
$preCommitSource = ".git\hooks\pre-commit.ps1"
$preCommitDest = ".git\hooks\pre-commit"

# Check if .git directory exists
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Not a git repository!" -ForegroundColor Red
    Write-Host "Please run this script from the root of your git repository." -ForegroundColor Yellow
    exit 1
}

Write-Host "Installing pre-commit hook..." -ForegroundColor Yellow

# Create pre-commit hook that calls PowerShell script
$hookContent = @"
#!/bin/sh
# Pre-commit hook - calls PowerShell script for Windows compatibility

# Check if PowerShell is available
if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -ExecutionPolicy Bypass -File .git/hooks/pre-commit.ps1
    exit `$?
elif command -v pwsh >/dev/null 2>&1; then
    pwsh -ExecutionPolicy Bypass -File .git/hooks/pre-commit.ps1
    exit `$?
else
    # Fallback to bash version
    echo "PowerShell not found, using bash version..."
    
    # Get staged .md files
    STAGED_MD_FILES=`$(git diff --cached --name-only --diff-filter=ACM | grep "\.md`$")
    
    if [ -z "`$STAGED_MD_FILES" ]; then
        echo "✅ No markdown files to check"
        exit 0
    fi
    
    echo "Files to check:"
    echo "`$STAGED_MD_FILES" | sed 's/^/  - /'
    
    # Run batch checker
    python batch_check.py `$STAGED_MD_FILES --errors-only --quiet
    
    EXIT_CODE=`$?
    
    if [ `$EXIT_CODE -eq 0 ]; then
        echo "✅ Documentation quality checks passed!"
        exit 0
    else
        echo "❌ Documentation quality checks failed!"
        echo "Please fix the errors before committing."
        exit 1
    fi
fi
"@

# Write the hook
Set-Content -Path $preCommitDest -Value $hookContent -Encoding UTF8

Write-Host "[OK] Pre-commit hook installed!" -ForegroundColor Green

# Test the hook
Write-Host ""
Write-Host "Testing pre-commit hook..." -ForegroundColor Yellow

try {
    $testResult = & python batch_check.py --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Hook is working correctly!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Hook installed but test failed" -ForegroundColor Yellow
        Write-Host "Make sure Python and dependencies are installed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Could not test hook: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The pre-commit hook will now run automatically when you commit." -ForegroundColor White
Write-Host ""
Write-Host "To bypass the hook (not recommended), use:" -ForegroundColor Cyan
Write-Host "  git commit --no-verify" -ForegroundColor White
Write-Host ""
Write-Host "To test the hook manually:" -ForegroundColor Cyan
Write-Host "  python batch_check.py README.md" -ForegroundColor White
Write-Host ""
