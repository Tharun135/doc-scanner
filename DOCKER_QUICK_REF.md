# 🚀 DocScanner Docker - Quick Reference

## ⚡ Quick Start Commands

```powershell
# Windows - Use the helper script
.\docker-start.ps1

# Or use Docker Compose directly
docker-compose up -d               # Start all services
docker-compose stop                # Stop services
docker-compose logs -f             # View logs
docker-compose down                # Stop and remove containers
```

## 🌐 URLs

- **App**: <http://localhost:5000>
- **ChromaDB**: <http://localhost:8000>
- **Ollama**: <http://localhost:11434>

## 📋 Essential Commands

| Action | Command |
|--------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose stop` |
| **Restart** | `docker-compose restart` |
| **Logs** | `docker-compose logs -f` |
| **Status** | `docker-compose ps` |
| **Shell** | `docker-compose exec web bash` |
| **Clean** | `docker-compose down` |
| **Clean All** | `docker-compose down -v` |

## 🔍 Health Checks

```powershell
curl http://localhost:5000/                    # Web app
curl http://localhost:8000/api/v1/heartbeat    # ChromaDB
curl http://localhost:11434/api/tags           # Ollama
```

## 🛠️ Troubleshooting

```powershell
# View errors
docker-compose logs web --tail=50

# Rebuild
docker-compose build --no-cache

# Restart service
docker-compose restart web

# Check what's using port 5000
netstat -an | findstr :5000
```

## 📦 Data Locations

- **Volumes**: `chroma_data`, `ollama_data`
- **Mounted**: `./data`, `./chroma_db`, `./logs`, `./config`

## 🎯 Production

Use `Dockerfile.production` with Gunicorn:

```yaml
services:
  web:
    build:
      dockerfile: Dockerfile.production
```

---

**Full Documentation**: See `DOCKER_DEPLOYMENT.md`
