import os
import re

def remove_non_ascii(text):
    return text.encode('ascii', 'ignore').decode('ascii')

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = remove_non_ascii(content)
                    
                    if content != new_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Cleaned non-ASCII characters from {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    # Process app and tools directories
    process_directory('d:/doc-scanner/app')
    process_directory('d:/doc-scanner/tools')
    process_directory('d:/doc-scanner/run.py') # Also check run.py
