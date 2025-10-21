#!/bin/bash
# Startup script for Render deployment

# Get the port from environment variable
PORT=${PORT:-5000}

echo "🚀 Starting DocScanner AI on port $PORT"
echo "🌐 Environment: ${FLASK_ENV:-production}"
echo "📊 Workers: 2"
echo "🔧 WSGI Module: wsgi:app"
echo "📍 Binding to: 0.0.0.0:$PORT"

# Test if the wsgi module can be imported
echo "🧪 Testing WSGI import..."
python -c "from wsgi import app; print('✅ WSGI app imported successfully')" || echo "❌ WSGI import failed"

# Start Gunicorn with the correct port
exec gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --timeout 120 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    wsgi:app