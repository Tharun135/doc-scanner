import subprocess
import sys
import time

# Run the test in a separate process
result = subprocess.run([
    sys.executable, 'quick_format_test.py'
], cwd='D:/doc-scanner', capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
