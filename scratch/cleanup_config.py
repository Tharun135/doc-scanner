import re
import os

def clean_requirements(file_path, encoding='utf-8'):
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
    except UnicodeError:
        with open(file_path, 'r', encoding='utf-16') as f:
            lines = f.readlines()
        encoding = 'utf-16'
    
    new_lines = []
    for line in lines:
        if 'anthropic' in line or 'openai' in line or 'langchain' in line:
            continue
        new_lines.append(line)
        
    with open(file_path, 'w', encoding=encoding) as f:
        f.writelines(new_lines)

def clean_docker_compose(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove OLLAMA_URL
    content = re.sub(r'\s*-\s*OLLAMA_URL=.*?\n', '\n', content)
    # Remove depends_on ollama
    content = re.sub(r'\s*-\s*ollama\n', '\n', content)
    # Remove ollama service
    content = re.sub(r'\s*ollama:\n\s*image: ollama/ollama.*?(?=\s*volumes:|\Z)', '', content, flags=re.DOTALL)
    # Remove ollama_data volume
    content = re.sub(r'\s*ollama_data:\n\s*driver: local\n', '\n', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

clean_requirements('deployment/requirements.txt')
clean_requirements('fastapi_requirements.txt')
clean_docker_compose('docker-compose.yml')
clean_docker_compose('docker-compose.fastapi.yml')
