# 🧪 Quick Tester Guide

## For Someone Testing DocScanner

### ⚡ Fastest Way to Share

#### Option 1: GitHub (Best for Developers)
```powershell
# Share this link:
https://github.com/Tharun135/doc-scanner

# They run:
git clone https://github.com/Tharun135/doc-scanner.git
cd doc-scanner
docker-compose up -d
```

#### Option 2: Packaged ZIP (Best for Non-Developers)
```powershell
# Create package:
.\create-tester-package.ps1

# Share the generated ZIP file via:
- Google Drive
- Dropbox
- Email (if small enough)
- WeTransfer
```

---

## 📦 What You Need to Do

### 1. Create the Package
```powershell
cd d:\doc-scanner
.\create-tester-package.ps1
```

This creates: `DocScanner-TesterPackage.zip` (~5-10 MB)

### 2. Upload Somewhere
- **Google Drive:** drive.google.com
- **Dropbox:** dropbox.com
- **OneDrive:** onedrive.live.com
- **WeTransfer:** wetransfer.com (for large files)

### 3. Share With Testers

Send them:
```
Hi!

Please test DocScanner - an AI writing assistant.

Download: [YOUR LINK HERE]
Instructions: Included in ZIP (TESTER_INSTRUCTIONS.md)

Quick Start:
1. Install Docker Desktop
2. Extract ZIP
3. Run: docker-compose up -d
4. Open: http://localhost:5000

Testing time: 15-30 minutes

Thanks!
```

---

## 🎯 What Testers Need

### Requirements:
- **Docker Desktop** (https://docker.com) - OR -
- **Python 3.11+** for non-Docker testing

### Their Steps:
1. Extract the ZIP
2. Read `TESTER_INSTRUCTIONS.md`
3. Run `docker-compose up -d`
4. Test the features
5. Report back

---

## 📋 Testing Checklist for Them

Give them this checklist:

```
DocScanner Testing Checklist:

Setup:
[ ] Docker installed and running
[ ] Extracted ZIP file
[ ] Ran docker-compose up -d
[ ] Opened http://localhost:5000

Document Upload:
[ ] Uploaded PDF
[ ] Uploaded TXT
[ ] Uploaded DOCX

Features:
[ ] Document analysis works
[ ] Passive voice detected
[ ] Long sentences detected
[ ] Vague terms detected
[ ] AI suggestions button works
[ ] AI suggestions are helpful
[ ] Export to CSV works
[ ] CSV contains correct data

Feedback:
[ ] Report any bugs
[ ] Note confusing UI elements
[ ] Suggest improvements
```

---

## 🚀 Alternative: Cloud Demo

Instead of asking them to install, deploy to cloud:

### Deploy to Render (Free)
```bash
# Push to GitHub first
git push

# Go to render.com
# Create new Web Service
# Connect GitHub repo
# Deploy!
```

Then share: `https://your-app.onrender.com`

**Pros:** No installation needed
**Cons:** Takes 5 minutes to set up

---

## 📧 Sample Email Template

```
Subject: Testing Request - DocScanner AI Writing Assistant

Hi [Name],

I'm working on DocScanner, an AI-powered writing assistant for technical documentation. Could you help test it?

**Download:** [INSERT LINK]

**What it does:**
- Detects passive voice
- Identifies long sentences
- Suggests improvements using AI
- Works with PDF, TXT, DOCX files

**Testing Steps:**
1. Download and extract ZIP
2. Follow TESTER_INSTRUCTIONS.md
3. Test with the included sample-test.txt
4. Report any issues or feedback

**Requirements:**
- Docker Desktop (https://docker.com)
- 15-30 minutes

**Questions?** See QUICK_START.md in the package.

Thanks for your help!

[Your Name]
```

---

## 🎬 Quick Video Demo (Optional)

Record a 2-minute video showing:
1. Opening the app
2. Uploading a document
3. Getting AI suggestions
4. Exporting results

Share on:
- YouTube (unlisted link)
- Loom.com
- Google Drive

---

## ✅ Summary

**Easiest for you:** Run `create-tester-package.ps1`
**Easiest for them:** Download ZIP, run Docker
**No installation:** Deploy to Render/Railway

Choose based on your testers' technical level!
