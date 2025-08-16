import requests
import time

# Wait for server to start
time.sleep(2)

try:
    files = {'file': ('test.txt', 'this is a test. microsoft should be capitalized.', 'text/plain')}
    response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=10)
    
    print('Status Code:', response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        sentences = data.get('sentences', [])
        print('Number of sentences:', len(sentences))
        
        total_issues = sum(len(s.get('feedback', [])) for s in sentences)
        print('Total issues found:', total_issues)
        
        if sentences:
            for i, sentence in enumerate(sentences):
                feedback = sentence.get('feedback', [])
                plain_text = sentence.get('plain', sentence.get('content', 'N/A'))
                print(f'Sentence {i+1}: "{plain_text}" - {len(feedback)} issues')
                for issue in feedback:
                    print(f'  - {issue.get("message", "No message")}')
        else:
            print('No sentences found!')
            print('Available keys in response:', list(data.keys()))
    else:
        print('Error response:', response.text)
        
except Exception as e:
    print('Error occurred:', e)
