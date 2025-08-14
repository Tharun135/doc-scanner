import subprocess
import time

# Wait for server to be ready
time.sleep(2)

# Run the test
result = subprocess.run([
    'D:/doc-scanner/venv/Scripts/python.exe', 
    'debug_highlighting_issue.py'
], cwd='D:/doc-scanner', capture_output=True, text=True)

print("=== DEBUG OUTPUT ===")
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)
print(f"\nReturn code: {result.returncode}")
