# 🚀 Quick Start Guide - DocScanner

## Current Status: Building Docker Containers...

Your Docker containers are currently being built. This will take **5-10 minutes** the first time.

---

## ✅ What to Do After Build Completes

### 1. Check if services are running:
```powershell
docker-compose ps
```

You should see 3 services:
- `docscanner-app` (port 5000)
- `docscanner-chromadb` (port 8000)  
- `docscanner-ollama` (port 11434)

### 2. View logs:
```powershell
docker-compose logs -f
```

Press `Ctrl+C` to exit logs.

### 3. Access DocScanner:
Open your browser to: **http://localhost:5000**

---

## 📝 Common Commands

```powershell
# Stop services (keeps data)
docker-compose stop

# Start services again
docker-compose start

# Restart all services
docker-compose restart

# View logs for specific service
docker-compose logs -f web

# Stop and remove containers (keeps data volumes)
docker-compose down

# Full cleanup (removes everything including data)
docker-compose down -v
```

---

## 🔧 If Something Goes Wrong

### Port Already in Use:
```powershell
# Check what's using port 5000
netstat -an | findstr :5000

# Kill the process or change port in docker-compose.yml
```

### Service Won't Start:
```powershell
# Check logs
docker-compose logs web

# Rebuild
docker-compose build --no-cache web
docker-compose up -d
```

### Ollama Model Not Downloaded:
```powershell
# The first time, Ollama needs to download the phi3 model
# This happens automatically but takes 5-10 minutes
# Check progress:
docker-compose logs -f ollama
```

---

## 📊 Monitor Progress

While building, you can open a new terminal and run:
```powershell
# Watch container status
docker-compose ps

# See resource usage
docker stats
```

---

## ⏱️ First-Time Setup Timeline

1. **Building images**: 5-10 minutes (happening now)
2. **Starting containers**: 30 seconds
3. **Downloading phi3 model**: 5-10 minutes (automatic)
4. **Ready to use**: After model downloads

---

## 🎯 Next Steps After Startup

1. Open http://localhost:5000
2. Upload a document (PDF, TXT, DOCX)
3. Click "Analyze Document"
4. Get AI-powered writing suggestions!

---

## 💡 Tip

Keep the terminal open to see logs. If you close it, services keep running in background.

To stop: `docker-compose stop`
