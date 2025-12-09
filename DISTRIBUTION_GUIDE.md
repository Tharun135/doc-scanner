# 📦 DocScanner - Distribution Guide

## How to Share DocScanner for Testing

This guide shows you how to package and distribute DocScanner so others can test it on their systems.

---

## 🎯 **Option 1: GitHub Repository (Recommended)**

### For You (Sharing):
```powershell
# Make sure all changes are committed
git add .
git commit -m "Dockerized DocScanner with RAG and AI features"
git push origin branch-15-newfeature

# Or push to main branch
git checkout main
git merge branch-15-newfeature
git push origin main
```

### For Testers (Using):
```bash
# Clone the repository
git clone https://github.com/Tharun135/doc-scanner.git
cd doc-scanner

# Start with Docker (recommended)
docker-compose up -d

# Or run with Python
python run.py
```

**Share this URL:** `https://github.com/Tharun135/doc-scanner`

---

## 🐳 **Option 2: Docker Image (Easiest for Testers)**

### Step 1: Build and Save Docker Image

```powershell
# Build the image
docker-compose build

# Save image to file
docker save docscanner-web:latest -o docscanner-image.tar

# Compress it (optional, reduces size significantly)
Compress-Archive -Path docscanner-image.tar -DestinationPath docscanner-image.zip
```

### Step 2: Share the File

Upload `docscanner-image.zip` to:
- Google Drive
- Dropbox
- OneDrive
- File sharing service

### Step 3: Instructions for Testers

Create a file `TESTER_INSTRUCTIONS.md`:

```markdown
# DocScanner Testing Instructions

## Prerequisites
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Start Docker Desktop and wait for it to be ready

## Installation Steps

1. Extract `docscanner-image.zip`
2. Open PowerShell/Terminal in the extracted folder
3. Load the Docker image:
   ```powershell
   docker load -i docscanner-image.tar
   ```
4. Download `docker-compose.yml` from the package
5. Start the application:
   ```powershell
   docker-compose up -d
   ```
6. Open browser: http://localhost:5000

## Testing
1. Upload a document (PDF, TXT, DOCX)
2. Click "Analyze Document"
3. Review AI-powered suggestions
4. Test different features

## Stop Testing
```powershell
docker-compose stop
```
```

---

## 📂 **Option 3: Complete Package (No Docker Required)**

### Create Distribution Package

```powershell
# Create distribution directory
New-Item -ItemType Directory -Path "DocScanner-Distribution" -Force

# Copy necessary files
Copy-Item -Path "app" -Destination "DocScanner-Distribution\app" -Recurse
Copy-Item -Path "config" -Destination "DocScanner-Distribution\config" -Recurse
Copy-Item -Path "deployment\requirements.txt" -Destination "DocScanner-Distribution\"
Copy-Item -Path "run.py" -Destination "DocScanner-Distribution\"
Copy-Item -Path "wsgi.py" -Destination "DocScanner-Distribution\"
Copy-Item -Path "README.md" -Destination "DocScanner-Distribution\"

# Create setup script
@"
# DocScanner Setup Script
Write-Host "Setting up DocScanner..." -ForegroundColor Cyan

# Check Python
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

Write-Host "Setup complete! Run: python run.py" -ForegroundColor Green
"@ | Out-File -FilePath "DocScanner-Distribution\setup.ps1" -Encoding UTF8

# Create run script
@"
# DocScanner Run Script
.\venv\Scripts\Activate.ps1
python run.py
"@ | Out-File -FilePath "DocScanner-Distribution\start.ps1" -Encoding UTF8

# Compress
Compress-Archive -Path "DocScanner-Distribution\*" -DestinationPath "DocScanner-Portable.zip"
```

### Instructions for Testers

```markdown
# DocScanner Portable - Testing Instructions

## Prerequisites
- Python 3.11 or higher
- Internet connection (for first-time setup)

## Installation

1. Extract `DocScanner-Portable.zip`
2. Open PowerShell in the extracted folder
3. Run setup:
   ```powershell
   .\setup.ps1
   ```

## Running

```powershell
.\start.ps1
```

Open browser: http://localhost:5000

## Stopping

Press `Ctrl+C` in the terminal
```

---

## 🌐 **Option 4: Cloud Deployment (Public Access)**

Deploy to a cloud platform so testers can access via URL without installation.

### Deploy to Render.com (Free)

1. Push code to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r deployment/requirements.txt`
   - **Start Command:** `gunicorn wsgi:application`
6. Deploy!

Share the URL: `https://your-app.onrender.com`

### Deploy to Railway.app (Free)

1. Go to https://railway.app
2. Connect GitHub repository
3. Deploy automatically
4. Share the generated URL

### Deploy to Heroku

```powershell
# Install Heroku CLI
# Then:
heroku login
heroku create docscanner-app
git push heroku main
```

---

## 📋 **Option 5: Release Package on GitHub**

### Create a Release

```powershell
# Tag the version
git tag -a v1.0.0 -m "DocScanner v1.0.0 - Initial release"
git push origin v1.0.0
```

### On GitHub:
1. Go to your repository
2. Click "Releases" → "Create a new release"
3. Select tag `v1.0.0`
4. Add release notes
5. Upload assets:
   - `DocScanner-Portable.zip`
   - `docker-compose.yml`
   - `TESTER_INSTRUCTIONS.md`

---

## 📝 **What to Include in Test Package**

### Essential Files:
- ✅ `README.md` - Overview and features
- ✅ `QUICK_START.md` - Quick start guide
- ✅ `TESTER_INSTRUCTIONS.md` - Testing instructions
- ✅ `docker-compose.yml` - Docker setup
- ✅ `requirements.txt` - Python dependencies
- ✅ Sample document - For testing

### Optional:
- Screenshots
- Demo video
- Known issues list
- Feedback form link

---

## 🎬 **Create Tester Package Script**

Save this as `create-tester-package.ps1`:

```powershell
# DocScanner Tester Package Creator
Write-Host "Creating DocScanner Tester Package..." -ForegroundColor Cyan

# Create package directory
$packageDir = "DocScanner-TesterPackage"
New-Item -ItemType Directory -Path $packageDir -Force

# Copy Docker files
Copy-Item "docker-compose.yml" -Destination "$packageDir\"
Copy-Item "Dockerfile" -Destination "$packageDir\"
Copy-Item ".dockerignore" -Destination "$packageDir\"

# Copy documentation
Copy-Item "README.md" -Destination "$packageDir\"
Copy-Item "QUICK_START.md" -Destination "$packageDir\"
Copy-Item "DOCKER_QUICK_REF.md" -Destination "$packageDir\"

# Copy application files
Copy-Item -Path "app" -Destination "$packageDir\app" -Recurse
Copy-Item -Path "config" -Destination "$packageDir\config" -Recurse
Copy-Item -Path "deployment" -Destination "$packageDir\deployment" -Recurse

# Copy scripts
Copy-Item "run.py" -Destination "$packageDir\"
Copy-Item "wsgi.py" -Destination "$packageDir\"
Copy-Item "docker-start.ps1" -Destination "$packageDir\"

# Create tester instructions
@"
# 🧪 DocScanner Testing Instructions

## Quick Start (Docker - Recommended)

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Open PowerShell in this folder
3. Run: ``docker-compose up -d``
4. Wait 2-3 minutes for setup
5. Open: http://localhost:5000

## Testing Checklist

- [ ] Upload a PDF document
- [ ] Upload a TXT document
- [ ] Upload a DOCX document
- [ ] Run document analysis
- [ ] Check AI suggestions
- [ ] Test "Get AI Suggestion" button
- [ ] Export results to CSV
- [ ] Test RAG knowledge base features

## Reporting Issues

Please report any issues with:
- System info (Windows/Mac/Linux)
- Error messages
- Screenshots
- Steps to reproduce

## Stop Testing

``docker-compose stop``

---

**Need Help?** See QUICK_START.md for detailed instructions.
"@ | Out-File -FilePath "$packageDir\TESTER_INSTRUCTIONS.md" -Encoding UTF8

# Create sample test document
@"
This is a sample document for testing DocScanner.

Some sentences may have passive voice issues. The document was created for testing purposes.
Various terms might be vague or unclear. Multiple long sentences could potentially benefit from being split into shorter, more concise statements that are easier to read and understand, especially for technical documentation where clarity and brevity are highly valued by readers.

Test different features:
1. Passive voice detection
2. Long sentence analysis
3. Vague term identification
4. AI-powered suggestions
"@ | Out-File -FilePath "$packageDir\sample-test.txt" -Encoding UTF8

# Compress everything
Compress-Archive -Path "$packageDir\*" -DestinationPath "DocScanner-TesterPackage.zip" -Force

Write-Host ""
Write-Host "✅ Package created: DocScanner-TesterPackage.zip" -ForegroundColor Green
Write-Host ""
Write-Host "Share this file with testers!" -ForegroundColor Cyan
Write-Host "Size: $((Get-Item DocScanner-TesterPackage.zip).Length / 1MB) MB" -ForegroundColor Yellow
```

---

## 📧 **Email Template for Testers**

```
Subject: DocScanner Testing - AI-Powered Writing Assistant

Hi [Name],

I'd like you to test DocScanner, an AI-powered writing assistant that provides real-time suggestions for technical documentation.

**Features to Test:**
✅ Document analysis (PDF, TXT, DOCX)
✅ Passive voice detection
✅ Long sentence splitting
✅ Vague term identification
✅ AI-powered suggestions using RAG
✅ CSV export

**Quick Start:**
1. Download attached package
2. Extract the ZIP file
3. Follow TESTER_INSTRUCTIONS.md

**With Docker (Easiest):**
- Install Docker Desktop
- Run: docker-compose up -d
- Open: http://localhost:5000

**Without Docker:**
- Requires Python 3.11+
- Run: python run.py

**Please Test:**
- Upload sample documents
- Check AI suggestion quality
- Report any bugs or issues
- Share feedback on UX/UI

**Expected Testing Time:** 15-30 minutes

Let me know if you have any questions!

Best regards,
[Your Name]
```

---

## 🚀 **Recommended Distribution Strategy**

### For Beta Testing:
1. ✅ **GitHub Repository** - Share repo link
2. ✅ **Docker Compose** - Simplest for testers
3. ✅ **Test Instructions** - Clear documentation

### For Public Release:
1. ✅ **GitHub Release** - Official release page
2. ✅ **Cloud Demo** - Live demo on Render/Railway
3. ✅ **Docker Hub** - Push image to registry

---

## 📦 **Summary**

**Easiest for Testers:**
```powershell
# You: Share GitHub link
# Testers: 
git clone https://github.com/Tharun135/doc-scanner.git
cd doc-scanner
docker-compose up -d
```

**Most Professional:**
- GitHub Release with packaged ZIP
- Cloud demo deployment
- Comprehensive documentation

**Choose based on your audience's technical level!**
