FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install essential system packages
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

# Copy requirements first (to leverage layer caching)
COPY requirements.txt /app/requirements.txt

# 🩷 Step 1: Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# 🩷 Step 2: Install heavy packages like torch and torchvision first
RUN pip install --no-cache-dir torch torchvision

# 🩷 Step 3: Install the rest of the dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire application
COPY . /app

# Environment variables
ENV FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Expose the Flask/Gunicorn port
EXPOSE ${PORT}

# Create non-root user for better security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck to verify container is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT} || exit 1

# Start the Flask app via Gunicorn
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "--workers", "3", "--threads", "4", "--timeout", "120"]
