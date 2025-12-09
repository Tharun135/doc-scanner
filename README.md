# Doc Scanner - Project Structure

This project has been reorganized for better maintainability and clarity.

## 📁 Root Directory Files

Only essential files are kept in the root:

- `run.py` - Main application runner
- `wsgi.py` - WSGI entry point for deployment
- `docker-compose.yml` - Docker composition
- `Dockerfile` - Docker container definition
- `render.yaml` - Render deployment configuration
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules
- `.dockerignore` - Docker ignore rules

## 📂 Folder Structure

### `/app/`

Core Flask application code

- Main application modules
- Routes and blueprints
- Core business logic

### `/config/`

Configuration files

- JSON configuration files
- Rule definitions
- System settings

### `/data/`

Data files and databases

- Sample documents
- Database files (*.db)
- JSONL data files
- Test data and uploads

### `/deployment/`

Deployment related files

- Requirements files
- AWS Elastic Beanstalk config
- Deployment scripts

### `/docs/`

Documentation

- Markdown documentation
- README files
- System guides and summaries

### `/scripts/`

Utility scripts

- Batch files
- Shell scripts
- Alternative run scripts
- JavaScript utilities

### `/static/`

Static web assets

- CSS files
- JavaScript files
- Images and icons

### `/tests/`

Test files

- Unit tests
- Integration tests
- Test utilities

### `/tools/`

Development and utility tools

- `/tools/analysis/` - Analysis and exploration tools
- `/tools/debug/` - Debug utilities
- `/tools/demo/` - Demo and example scripts
- `/tools/setup/` - Setup and installation tools
- Other utility Python scripts

### `/chroma_db/`

ChromaDB vector database storage

### `/venv/`

Python virtual environment

## 🚀 Quick Start

1. **Run the application:**

   ```bash
   python run.py
   ```

2. **Deploy with Docker:**

   ```bash
   docker-compose up
   ```

3. **Run tests:**

   ```bash
   python -m pytest tests/
   ```

## 📋 Development

- Main application code: `/app/`
- Add new tests: `/tests/`
- Configuration changes: `/config/`
- Debug issues: `/tools/debug/`
- Analysis tools: `/tools/analysis/`

This structure keeps the root clean while organizing all functionality into logical directories.

