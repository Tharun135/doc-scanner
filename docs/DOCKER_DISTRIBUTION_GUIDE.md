# Docker Distribution Guide for DocScanner

This guide explains how to distribute and deploy DocScanner using Docker containers.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Distribution Options](#distribution-options)
- [Building Docker Images](#building-docker-images)
- [Deploying Containers](#deploying-containers)
- [Troubleshooting](#troubleshooting)
- [For Testers](#for-testers)

---

## 🔧 Prerequisites

### On Your Development Machine
- Docker Desktop installed and running
- Docker Compose (comes with Docker Desktop)
- Git (for version control)
- 10GB+ free disk space

### On Tester/User Machines
- Docker Desktop installed
- 10GB+ free disk space
- Internet connection (for downloading images)

---

## 📦 Distribution Options

### Option 1: Docker Hub (Recommended for Wide Distribution)
Push your images to Docker Hub so others can pull them easily.

```powershell
# 1. Build the image
docker-compose build

# 2. Tag the image
docker tag doc-scanner-web:latest yourusername/docscanner:latest

# 3. Login to Docker Hub
docker login

# 4. Push the image
docker push yourusername/docscanner:latest
```

**Testers can then pull and run:**
```powershell
docker pull yourusername/docscanner:latest
docker-compose up -d
```

### Option 2: Save as TAR File (For Offline Distribution)
Export Docker images to files for sharing without internet.

```powershell
# Save the image to a tar file
docker save doc-scanner-web:latest -o docscanner-app.tar

# Compress it (optional, saves space)
Compress-Archive -Path docscanner-app.tar -DestinationPath docscanner-app.tar.zip
```

**Testers load it:**
```powershell
# Load the image
docker load -i docscanner-app.tar

# Or if compressed
Expand-Archive docscanner-app.tar.zip
docker load -i docscanner-app.tar
```

### Option 3: GitHub Container Registry (Best for Private Projects)
Use GitHub's container registry (ghcr.io) for private distribution.

```powershell
# 1. Create a Personal Access Token (PAT) on GitHub with 'write:packages' permission

# 2. Login to GitHub Container Registry
$env:CR_PAT | docker login ghcr.io -u USERNAME --password-stdin

# 3. Tag your image
docker tag doc-scanner-web:latest ghcr.io/yourusername/docscanner:latest

# 4. Push to GitHub
docker push ghcr.io/yourusername/docscanner:latest
```

---

## 🏗️ Building Docker Images

### Clean Build (Recommended)
Always build without cache to ensure all dependencies are fresh:

```powershell
# Build web application image (no cache)
docker-compose build --no-cache web

# Or build all services
docker-compose build --no-cache
```

### Quick Build (Uses Cache)
Faster but may cause issues if dependencies changed:

```powershell
docker-compose build
```

### Build Progress
The build process takes 5-10 minutes and includes:
1. Downloading Python 3.11 base image
2. Installing system dependencies (gcc, g++, make)
3. Installing Python packages (~500MB)
4. Downloading spaCy language model
5. Setting up application files

**Expected build time:** 5-10 minutes on first build

---

## 🚀 Deploying Containers

### Start All Services
```powershell
docker-compose up -d
```

This starts:
- **DocScanner Web App** (port 5000)
- **ChromaDB** (port 8000) - Vector database
- **Ollama** (port 11434) - LLM inference engine

### Check Container Status
```powershell
docker-compose ps
```

Expected output:
```
NAME                  IMAGE                    STATUS
docscanner-app        doc-scanner-web          Up (healthy)
docscanner-chromadb   chromadb/chroma:latest   Up
docscanner-ollama     ollama/ollama:latest     Up
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f chromadb
docker-compose logs -f ollama
```

### Access the Application
Once containers are running:
- **Web Interface:** http://localhost:5000
- **ChromaDB API:** http://localhost:8000
- **Ollama API:** http://localhost:11434

### Stop All Services
```powershell
docker-compose down
```

### Stop and Remove All Data
```powershell
docker-compose down -v
```
⚠️ **Warning:** This deletes all uploaded documents and vector embeddings!

---

## 🎯 For Testers

### Quick Start Package
Create a distribution package for testers:

```powershell
# Run the distribution script
.\create-tester-package.ps1
```

This creates `docscanner-tester-package.zip` containing:
- docker-compose.yml
- .env configuration
- README for testers
- Sample test documents

### Tester Instructions

1. **Install Docker Desktop**
   - Windows: https://www.docker.com/products/docker-desktop
   - Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

2. **Extract the Package**
   ```powershell
   Expand-Archive docscanner-tester-package.zip
   cd docscanner-tester-package
   ```

3. **Pull Required Images**
   ```powershell
   docker-compose pull
   ```
   This downloads:
   - ChromaDB (~750MB)
   - Ollama (~5.8GB)
   - DocScanner app (~9GB)

4. **Start the Application**
   ```powershell
   docker-compose up -d
   ```

5. **Access the Application**
   - Open browser: http://localhost:5000
   - Upload test documents
   - Test AI suggestions

6. **Stop When Done**
   ```powershell
   docker-compose down
   ```

---

## 🔧 Troubleshooting

### Issue: "Flask not installed" Error

**Symptom:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Rebuild without cache:
```powershell
docker-compose down
docker-compose build --no-cache web
docker-compose up -d
```

### Issue: Containers Keep Restarting

**Check logs:**
```powershell
docker-compose logs web
```

**Common causes:**
1. Port already in use (5000, 8000, or 11434)
2. Missing environment variables
3. Volume permission issues

**Solution:**
```powershell
# Stop conflicting services
netstat -ano | findstr :5000

# Or change ports in docker-compose.yml
ports:
  - "5001:5000"  # Change to different port
```

### Issue: "ChromaDB unhealthy" Error

**This is expected** - ChromaDB container doesn't have curl/python for health checks.

**The service still works fine!** We removed the health check dependency.

### Issue: Ollama Not Responding

**Check if Ollama is running:**
```powershell
curl http://localhost:11434/api/tags
```

**If not responding:**
```powershell
docker-compose restart ollama
docker logs docscanner-ollama
```

### Issue: Build Takes Too Long

**Expected build times:**
- First build: 5-10 minutes
- With cache: 1-2 minutes
- Exporting layers: 2-5 minutes

**If stuck for >15 minutes:**
```powershell
# Cancel and try again
Ctrl+C
docker-compose build --no-cache web
```

### Issue: Out of Disk Space

**Check Docker disk usage:**
```powershell
docker system df
```

**Clean up:**
```powershell
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 🎛️ Configuration

### Environment Variables

Edit `.env` or `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_URL=http://ollama:11434
  - CHROMADB_HOST=chromadb
  - CHROMADB_PORT=8000
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
```

### Resource Limits

For systems with limited resources:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### GPU Support (Optional)

Ollama can use NVIDIA GPUs:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

**Requirements:**
- NVIDIA GPU
- NVIDIA Docker Runtime installed

---

## 📊 Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (docscanner-network)                    │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ DocScanner   │───▶│   ChromaDB   │    │  Ollama  │ │
│  │  Web App     │    │ Vector Store │◀───│   LLM    │ │
│  │  (Flask)     │    │              │    │ Inference │ │
│  │              │    │              │    │          │ │
│  │ Port: 5000   │    │ Port: 8000   │    │Port:11434│ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│         │                    │                  │       │
│         ▼                    ▼                  ▼       │
│  ┌──────────┐    ┌────────────────┐    ┌────────────┐ │
│  │  ./data  │    │  chroma_data   │    │ ollama_data│ │
│  │./chroma_db│   │   (volume)     │    │  (volume)  │ │
│  │  ./logs  │    └────────────────┘    └────────────┘ │
│  │ ./config │                                          │
│  └──────────┘                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Notes

### Production Deployment

1. **Change default ports** if deploying publicly
2. **Use environment variables** for sensitive config
3. **Enable HTTPS** with a reverse proxy (nginx)
4. **Restrict network access** with firewall rules
5. **Regular updates** - pull latest images weekly

### Example Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name docscanner.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📝 Pre-Distribution Checklist

Before sharing with testers:

- [ ] Build completes without errors
- [ ] All containers start successfully
- [ ] Web interface accessible at http://localhost:5000
- [ ] Document upload works
- [ ] AI suggestions generate correctly
- [ ] Passive voice detection works
- [ ] RAG system returns relevant suggestions
- [ ] Test with multiple document types (TXT, PDF, DOCX)
- [ ] Check logs for errors
- [ ] Create tester package with instructions
- [ ] Test package on a clean machine

---

## 🚀 Next Steps

1. **Build the images:**
   ```powershell
   docker-compose build --no-cache
   ```

2. **Test locally:**
   ```powershell
   docker-compose up -d
   curl http://localhost:5000
   ```

3. **Create distribution package:**
   ```powershell
   .\create-tester-package.ps1
   ```

4. **Choose distribution method:**
   - Docker Hub (public/private)
   - GitHub Container Registry (private)
   - TAR file (offline)

5. **Share with testers:**
   - Send package ZIP
   - Provide instructions
   - Set up support channel

---

## 📞 Support

For issues with Docker deployment:

1. Check logs: `docker-compose logs -f`
2. Check this troubleshooting guide
3. Rebuild without cache
4. Report issues on GitHub

---

**Last Updated:** November 24, 2025
**Docker Compose Version:** 3.8
**Docker Desktop Version:** 4.35+
