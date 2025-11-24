# DocScanner Tester Package Creator
# Run this script to create a distribution package for testers

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  DocScanner Tester Package Creator  " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create package directory
$packageDir = "DocScanner-TesterPackage"
Write-Host "[1/8] Creating package directory..." -ForegroundColor Yellow
if (Test-Path $packageDir) {
    Remove-Item -Path $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null

# Copy Docker files
Write-Host "[2/8] Copying Docker configuration..." -ForegroundColor Yellow
Copy-Item "docker-compose.yml" -Destination "$packageDir\"
Copy-Item "Dockerfile" -Destination "$packageDir\"
Copy-Item ".dockerignore" -Destination "$packageDir\"

# Copy documentation
Write-Host "[3/8] Copying documentation..." -ForegroundColor Yellow
Copy-Item "README.md" -Destination "$packageDir\" -ErrorAction SilentlyContinue
Copy-Item "QUICK_START.md" -Destination "$packageDir\" -ErrorAction SilentlyContinue
Copy-Item "DOCKER_QUICK_REF.md" -Destination "$packageDir\" -ErrorAction SilentlyContinue

# Copy application files
Write-Host "[4/8] Copying application code..." -ForegroundColor Yellow
Copy-Item -Path "app" -Destination "$packageDir\app" -Recurse -Force
Copy-Item -Path "config" -Destination "$packageDir\config" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "deployment" -Destination "$packageDir\deployment" -Recurse -Force

# Copy scripts
Write-Host "[5/8] Copying startup scripts..." -ForegroundColor Yellow
Copy-Item "run.py" -Destination "$packageDir\"
Copy-Item "wsgi.py" -Destination "$packageDir\"
Copy-Item "docker-start.ps1" -Destination "$packageDir\"

# Create tester instructions
Write-Host "[6/8] Creating tester instructions..." -ForegroundColor Yellow
@"
# DocScanner Testing Instructions

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Desktop: https://www.docker.com/products/docker-desktop
- 4GB RAM minimum, 8GB recommended
- 10GB free disk space

### Steps

1. **Start Docker Desktop** and wait for it to be ready
2. **Open PowerShell** in this folder
3. **Run the helper script:**
   ``````powershell
   .\docker-start.ps1
   ``````
   Select option 1 to start everything

4. **Or use Docker Compose directly:**
   ``````powershell
   docker-compose up -d
   ``````

5. **Wait 2-3 minutes** for initial setup
6. **Open browser:** http://localhost:5000

---

## Testing Checklist

Please test the following features:

### Document Upload
- [ ] Upload PDF document
- [ ] Upload TXT document  
- [ ] Upload DOCX document

### Analysis Features
- [ ] Run document analysis
- [ ] Check passive voice detection
- [ ] Check long sentence detection
- [ ] Check vague term detection

### AI Features
- [ ] Click "Get AI Suggestion" button
- [ ] Verify AI suggestions make sense
- [ ] Test multiple suggestions
- [ ] Check suggestion quality

### Export
- [ ] Export results to CSV
- [ ] Verify CSV contains all data

### RAG Knowledge Base
- [ ] Upload reference documents
- [ ] Check if suggestions use uploaded docs
- [ ] Test document-first AI

---

## Sample Test Document

Use ``sample-test.txt`` included in this package, or create your own with:
- Passive voice sentences
- Long, complex sentences
- Vague terms like "some", "various"

---

## Reporting Issues

Please report:
- **System Info:** Windows/Mac/Linux version
- **Error Messages:** Copy exact error text
- **Screenshots:** Of any visual issues
- **Steps to Reproduce:** What you did before the issue

---

## Stopping DocScanner

``````powershell
docker-compose stop
``````

To remove everything (including data):
``````powershell
docker-compose down -v
``````

---

## Alternative: Run Without Docker

### Prerequisites
- Python 3.11+
- pip

### Steps
``````powershell
# Install dependencies
pip install -r deployment/requirements.txt
python -m spacy download en_core_web_sm

# Run
python run.py
``````

Open: http://localhost:5000

---

## Need Help?

See ``QUICK_START.md`` for detailed instructions.

## Feedback

Please share:
- What worked well
- What was confusing
- Feature requests
- Bug reports

Thank you for testing! 🚀
"@ | Out-File -FilePath "$packageDir\TESTER_INSTRUCTIONS.md" -Encoding UTF8

# Create sample test document
Write-Host "[7/8] Creating sample test document..." -ForegroundColor Yellow
@"
DocScanner Test Document
========================

This document contains various writing issues for testing DocScanner's analysis features.

Passive Voice Examples
----------------------
The configuration file was created by the system administrator.
Settings must be verified before deployment can be initiated.
The data has been processed and stored in the database.

Long Sentence Examples
----------------------
The PROFINET IO Connector enables this connector to function as a PROFINET Controller and establish connections with IO Devices, which allows for comprehensive network communication and data exchange between various industrial automation components in a manufacturing environment.

Configuration of the system requires multiple steps including initial setup, parameter validation, network connectivity verification, security certificate installation, and final testing procedures to ensure proper operation.

Vague Term Examples
--------------------
Some of the properties require configuration.
Various settings need to be adjusted.
Multiple parameters must be checked.
Several options are available for customization.

Technical Writing Issues
------------------------
You can configure the settings manually or automatically depending on your requirements and the specific use case scenario that you are working with in your particular deployment environment.

The system provides various features and capabilities that enable users to perform different tasks and operations with multiple tools and options available.

Instructions for Testing
------------------------
1. Upload this document to DocScanner
2. Run the analysis
3. Check for detected issues:
   - Passive voice (3 examples above)
   - Long sentences (2 examples above)
   - Vague terms (4 examples above)
4. Click "Get AI Suggestion" on different issues
5. Verify the suggestions improve the writing
6. Export results to CSV

Expected Results
----------------
- Passive voice: Should be converted to active voice
- Long sentences: Should be split into shorter sentences
- Vague terms: Should be replaced with specific terms
- Technical issues: Should be simplified

Additional Test Cases
---------------------
Test the following scenarios:
- Upload multiple documents
- Test different file formats (PDF, DOCX, TXT)
- Upload very long documents (>1000 words)
- Test with technical documentation
- Test with different writing styles

Performance Testing
-------------------
- Check response time for analysis
- Monitor memory usage
- Test concurrent document uploads
- Verify stability over extended use

Thank you for testing DocScanner!
"@ | Out-File -FilePath "$packageDir\sample-test.txt" -Encoding UTF8

# Compress everything
Write-Host "[8/8] Creating ZIP package..." -ForegroundColor Yellow
$zipName = "DocScanner-TesterPackage.zip"
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}
Compress-Archive -Path "$packageDir\*" -DestinationPath $zipName -Force

# Calculate size
$sizeInMB = [math]::Round((Get-Item $zipName).Length / 1MB, 2)

# Success message
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Package Created Successfully!     " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package: $zipName" -ForegroundColor Cyan
Write-Host "Size: $sizeInMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Share this file with testers!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Upload to cloud storage (Google Drive, Dropbox, etc.)" -ForegroundColor Gray
Write-Host "2. Share download link with testers" -ForegroundColor Gray
Write-Host "3. Include the testing instructions" -ForegroundColor Gray
Write-Host ""

# Cleanup
Remove-Item -Path $packageDir -Recurse -Force

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
