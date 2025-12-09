# 🔧 Upload Error Fix - "Failed to fetch"

## Problem Identified

The "Failed to fetch" error during upload occurs because:

1. **Flask Auto-Reload Issue**: The server is running in debug mode with auto-reload enabled
2. **File Change Detection**: The server detects changes in dependencies (transformers library) and restarts constantly
3. **Upload Interruption**: When you upload during a restart, the request fails

## Evidence

From the terminal output:
```
INFO:werkzeug: * Detected change in 'C:\\...\transformers\...' , reloading
INFO:werkzeug: * Restarting with watchdog (windowsapi)
Exception in thread Thread-3 (serve_forever):
...
OSError: [WinError 10038] An operation was attempted on something that is not a socket
```

The server restarts every few seconds due to detecting changes in the transformers library files.

## Solution

### Option 1: Stop Current Server and Restart Without Auto-Reload (Recommended)

1. **Stop the current Flask server** (Press Ctrl+C in the terminal where it's running)

2. **Restart with auto-reload disabled**:
   ```powershell
   # Set environment variable to disable reloader
   $env:FLASK_DEBUG=0
   python run.py
   ```

   OR modify `run.py` temporarily:
   ```python
   # Change this line in run.py:
   app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False
   ```

### Option 2: Use --no-reload Flag

```powershell
flask run --no-reload --host=0.0.0.0 --port=5000
```

### Option 3: Exclude Transformers from Watch

Add to your Flask config or run.py:
```python
import os
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

# In create_app() or run.py:
app.run(
    host='0.0.0.0', 
    port=5000, 
    debug=True,
    use_reloader=False  # Disable auto-reload
)
```

## Quick Fix (Right Now)

Run this command:
```powershell
# Kill the current server
Stop-Process -Name "python" -Force

# Restart without reload
$env:WERKZEUG_RUN_MAIN='true'
python run.py
```

## Verification

After restarting, test:
```powershell
# Should return 200 OK without interruptions
curl http://localhost:5000/
```

Then try uploading a document again.

## Why This Happens

- **Debug Mode**: Werkzeug's auto-reloader watches for file changes
- **Transformers Library**: Has many files that trigger the file watcher
- **Windows File System**: Windows file system events can be more sensitive
- **Race Condition**: Upload request arrives during server restart

## Long-term Solution

For production/stable development:

1. **Disable debug mode** when not actively developing
2. **Use production server** like Gunicorn (but not on Windows)
3. **Configure reloader excludes** for large libraries
4. **Use Docker** to isolate the environment

## Current Server Status

✅ Server IS running on port 5000
❌ Server keeps restarting (auto-reload issue)
⚠️ Uploads fail during restart windows

---

**Immediate Action**: Restart Flask with `use_reloader=False` or `debug=False`
