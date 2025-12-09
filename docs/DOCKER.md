Docker build & compose for DocScanner

Single-container (recommended for simple deployments / Render / Azure Web Apps):

Build image:

```powershell
docker build -t docscanner-app .
```

Run:

```powershell
docker run -p 5000:5000 --env-file .env -e PORT=5000 docscanner-app
```

Multi-container (Flask + ChromaDB + Ollama):

```powershell
docker-compose up --build
```

Notes:
- Edit `.env` (copy from `.env.example`) to set secrets and service URLs.
- The `Dockerfile` installs dependencies from `requirements.txt` and uses `run.py` as the entrypoint.
- If you need the spaCy model installed at build-time, either include it in `requirements.txt` or uncomment `python -m spacy download en_core_web_sm` in the `Dockerfile`.
