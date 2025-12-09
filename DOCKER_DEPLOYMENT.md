# 🐳 Docker Deployment Guide for DocScanner

This guide covers containerization and deployment of the DocScanner application using Docker and Docker Compose.

## 📋 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **System Requirements**:
  - 4GB RAM minimum (8GB recommended)
  - 10GB free disk space
  - Optional: NVIDIA GPU with nvidia-docker for GPU acceleration

### Installation

**Windows:**
```powershell
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Docker Compose is included with Docker Desktop
```

**Linux:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 🚀 Quick Start

### 1. Clone and Configure

```bash
cd d:\doc-scanner

# Create environment file (optional, has defaults)
cp .env.example .env
# Edit .env with your preferences
```

### 2. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access the Application

- **DocScanner UI**: http://localhost:5000
- **ChromaDB**: http://localhost:8000
- **Ollama API**: http://localhost:11434

### 4. Stop Services

```bash
# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

---

## 🏗️ Architecture

The Docker setup includes three services:

```
┌─────────────────────────────────────────────┐
│                                             │
│  DocScanner Application (Flask)             │
│  Port: 5000                                 │
│  - Web UI                                   │
│  - Document Analysis                        │
│  - AI Suggestions                           │
│                                             │
└────────┬─────────────┬──────────────────────┘
         │             │
         │             │
    ┌────▼─────┐  ┌───▼──────────┐
    │ ChromaDB │  │    Ollama     │
    │ Port:8000│  │  Port: 11434  │
    │          │  │               │
    │ Vector   │  │  LLM Engine   │
    │ Storage  │  │  (phi3:latest)│
    └──────────┘  └───────────────┘
```

---

## 📦 Docker Services

### 1. **docscanner-app** (Main Application)
- **Image**: Built from Dockerfile
- **Port**: 5000
- **Features**:
  - Flask web server
  - Document processing
  - RAG-powered AI suggestions
- **Health Check**: HTTP GET to http://localhost:5000/

### 2. **docscanner-chromadb** (Vector Database)
- **Image**: chromadb/chroma:latest
- **Port**: 8000
- **Purpose**: Vector embeddings storage for RAG
- **Data**: Persisted in Docker volume `chroma_data`

### 3. **docscanner-ollama** (LLM Engine)
- **Image**: ollama/ollama:latest
- **Port**: 11434
- **Purpose**: Local LLM inference (phi3:latest)
- **Data**: Model storage in volume `ollama_data`
- **GPU Support**: Enabled if NVIDIA GPU available

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set in `docker-compose.yml`:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=phi3:latest

# ChromaDB
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000

# RAG Settings
RAG_ENABLED=1
MAX_DOCUMENTS=10
```

### Volume Mounts

Data persistence through volumes:

```yaml
volumes:
  # Application data (documents, configs)
  - ./data:/app/data
  - ./chroma_db:/app/chroma_db
  - ./logs:/app/logs
  - ./config:/app/config
  
  # Service data (automatic)
  - chroma_data:/chroma/chroma
  - ollama_data:/root/.ollama
```

---

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f chromadb
docker-compose logs -f ollama
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Access Container Shell

```bash
# DocScanner app
docker-compose exec web bash

# ChromaDB
docker-compose exec chromadb sh

# Ollama
docker-compose exec ollama bash
```

### Check Service Health

```bash
# Check all containers
docker-compose ps

# Health check for web service
curl http://localhost:5000/

# ChromaDB heartbeat
curl http://localhost:8000/api/v1/heartbeat

# Ollama status
curl http://localhost:11434/api/tags
```

### Manage Ollama Models

```bash
# List installed models
docker-compose exec ollama ollama list

# Pull a new model
docker-compose exec ollama ollama pull llama2

# Remove a model
docker-compose exec ollama ollama rm modelname
```

---

## 🚢 Production Deployment

### 1. **Using Gunicorn (Recommended)**

Update `Dockerfile` CMD:

```dockerfile
# Install gunicorn
RUN pip install gunicorn

# Use gunicorn instead of Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:application"]
```

Update `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 2. **Reverse Proxy with Nginx**

Create `nginx.conf`:

```nginx
upstream docscanner {
    server web:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://docscanner;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Add to `docker-compose.yml`:

```yaml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
    networks:
      - docscanner-network
```

### 3. **SSL/TLS with Let's Encrypt**

```bash
# Add certbot service
docker-compose exec nginx certbot --nginx -d your-domain.com
```

---

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache web

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Port Already in Use

```bash
# Check what's using the port
netstat -an | findstr :5000

# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use 8080 instead
```

### Out of Memory

```bash
# Increase Docker Desktop memory limit
# Settings -> Resources -> Memory -> 8GB

# Or limit service memory
docker-compose up -d --scale web=1
```

### ChromaDB Connection Issues

```bash
# Check if ChromaDB is healthy
docker-compose exec chromadb curl http://localhost:8000/api/v1/heartbeat

# Restart ChromaDB
docker-compose restart chromadb
```

### Ollama Model Not Found

```bash
# Pull phi3 model manually
docker-compose exec ollama ollama pull phi3:latest

# Verify it's installed
docker-compose exec ollama ollama list
```

---

## 📊 Monitoring

### Resource Usage

```bash
# Monitor all containers
docker stats

# Monitor specific container
docker stats docscanner-app
```

### Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up unused data
docker system prune -a
```

---

## 🔐 Security Best Practices

1. **Use Secrets Management**:
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

2. **Non-root User**: Already configured in Dockerfile
   ```dockerfile
   USER appuser
   ```

3. **Read-only Filesystem**:
   ```yaml
   security_opt:
     - no-new-privileges:true
   read_only: true
   ```

4. **Network Isolation**: Already using custom network
   ```yaml
   networks:
     - docscanner-network
   ```

---

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t docscanner:latest .
      
      - name: Run tests
        run: docker-compose up -d && docker-compose exec -T web python -m pytest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push docscanner:latest
```

---

## 📝 Backup and Restore

### Backup Data

```bash
# Backup all volumes
docker run --rm -v docscanner_chroma_data:/data -v $(pwd):/backup ubuntu tar czf /backup/chroma_backup.tar.gz /data

# Backup application data
tar -czf docscanner_data_backup.tar.gz ./data ./chroma_db ./config
```

### Restore Data

```bash
# Restore volumes
docker run --rm -v docscanner_chroma_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/chroma_backup.tar.gz

# Restore application data
tar -xzf docscanner_data_backup.tar.gz
```

---

## 🎯 Performance Tuning

### 1. **Optimize ChromaDB**
```yaml
chromadb:
  environment:
    - CHROMA_SERVER_AUTHN_CREDENTIALS=test-token
    - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token.TokenAuthenticationServerProvider
```

### 2. **Ollama GPU Acceleration**
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

### 3. **App Caching**
```yaml
web:
  environment:
    - CACHE_TYPE=redis
    - CACHE_REDIS_URL=redis://redis:6379
```

---

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **ChromaDB**: https://docs.trychroma.com/
- **Ollama**: https://github.com/ollama/ollama

---

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section
3. Open GitHub issue with logs and error messages

---

## 📄 License

Same as main DocScanner project license.
