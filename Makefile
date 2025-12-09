# DocScanner Docker Management Makefile
# Simplifies common Docker Compose operations

.PHONY: help build start stop restart logs shell clean backup restore test

# Default target
help:
	@echo "DocScanner Docker Management Commands:"
	@echo ""
	@echo "  make build       - Build all Docker images"
	@echo "  make start       - Start all services in background"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make logs-web    - View logs from web service only"
	@echo "  make shell       - Open shell in web container"
	@echo "  make ps          - List running containers"
	@echo "  make clean       - Stop and remove containers (keeps data)"
	@echo "  make clean-all   - Stop and remove containers AND data volumes"
	@echo "  make backup      - Backup all data volumes"
	@echo "  make restore     - Restore data from backup"
	@echo "  make test        - Run application tests"
	@echo "  make ollama-pull - Pull phi3 model for Ollama"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start services
start:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "DocScanner UI: http://localhost:5000"
	@echo "ChromaDB: http://localhost:8000"
	@echo "Ollama: http://localhost:11434"

# Stop services
stop:
	docker-compose stop

# Restart services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# View web service logs only
logs-web:
	docker-compose logs -f web

# Open shell in web container
shell:
	docker-compose exec web bash

# List running containers
ps:
	docker-compose ps

# Stop and remove containers (keeps volumes)
clean:
	docker-compose down
	@echo "✅ Containers stopped and removed. Data volumes preserved."

# Stop and remove containers AND volumes
clean-all:
	docker-compose down -v
	@echo "⚠️  All containers and data volumes removed!"

# Backup data volumes
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	docker run --rm -v docscanner_chroma_data:/data -v $(PWD)/backups:/backup ubuntu tar czf /backup/chroma_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz /data
	tar -czf backups/app_data_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data chroma_db config
	@echo "✅ Backup created in backups/"

# Restore from latest backup
restore:
	@echo "Restoring from latest backup..."
	@ls -t backups/chroma_backup_*.tar.gz | head -1 | xargs -I {} docker run --rm -v docscanner_chroma_data:/data -v $(PWD)/backups:/backup ubuntu tar xzf {}
	@ls -t backups/app_data_backup_*.tar.gz | head -1 | xargs -I {} tar -xzf {}
	@echo "✅ Restore complete"

# Run tests
test:
	docker-compose exec web python -m pytest tests/ -v

# Pull Ollama phi3 model
ollama-pull:
	docker-compose exec ollama ollama pull phi3:latest
	@echo "✅ phi3:latest model downloaded"

# Quick deployment (build + start)
deploy: build start
	@echo "✅ Deployment complete!"

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:5000/ > /dev/null 2>&1 && echo "✅ Web: Healthy" || echo "❌ Web: Unhealthy"
	@curl -f http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1 && echo "✅ ChromaDB: Healthy" || echo "❌ ChromaDB: Unhealthy"
	@curl -f http://localhost:11434/api/tags > /dev/null 2>&1 && echo "✅ Ollama: Healthy" || echo "❌ Ollama: Unhealthy"

# Watch logs in real-time
watch:
	watch -n 2 docker-compose ps

# Docker stats
stats:
	docker stats docscanner-app docscanner-chromadb docscanner-ollama
