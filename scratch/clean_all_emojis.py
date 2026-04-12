import os

def remove_non_ascii(text):
    return text.encode('ascii', 'ignore').decode('ascii')

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        # EXCLUDE heavy/binary dirs
        if any(bad in root for bad in ['.git', 'node_modules', 'chroma_db', '__pycache__']):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Skip binary files
                if file.endswith(('.png', '.jpg', '.pdf', '.docx', '.db', '.bin', '.pkl')):
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = remove_non_ascii(content)
                
                if content != new_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Cleaned non-ASCII characters from {file_path}")
            except Exception:
                pass

if __name__ == "__main__":
    process_directory('d:/doc-scanner')
