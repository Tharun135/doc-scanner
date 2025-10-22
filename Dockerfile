FROM python:3.11-slim

# Production-ready single-stage Dockerfile
WORKDIR /app

# Install system deps commonly needed to build wheels and run the app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Note: the repo's requirements.txt references the spaCy model wheel URL; if you prefer
# to download via `python -m spacy download en_core_web_sm` at build time, add that here.
# Installing the spaCy model at build-time increases image size.

# Copy application source
COPY . /app

# Environment defaults (can be overridden with -e or an env file)
ENV FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Expose port
EXPOSE ${PORT}

# Create non-root user and set ownership
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck (runs as container user; uses curl from the base image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT} || exit 1

# Start application with Gunicorn pointing at the WSGI app
# Uses a modest worker count; adjust `--workers`/`--threads` for your deployment.
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "--workers", "3", "--threads", "4", "--timeout", "120"]
