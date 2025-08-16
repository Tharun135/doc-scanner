import requests
import time

# Test the progressive upload endpoint
try:
    files = {'file': ('test.txt', 'this is a test. microsoft should be capitalized.', 'text/plain')}
    response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=10)
    
    print('Status Code:', response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print('Response keys:', list(data.keys()))
        
        # Check if it's a progress response
        if 'analysis_id' in data:
            analysis_id = data['analysis_id']
            print(f'Analysis ID: {analysis_id}')
            print('This endpoint requires polling for results.')
        else:
            # Direct response
            sentences = data.get('sentences', [])
            total_issues = sum(len(s.get('feedback', [])) for s in sentences)
            print(f'Total issues found: {total_issues}')
            
            if sentences:
                for i, sentence in enumerate(sentences):
                    feedback = sentence.get('feedback', [])
                    content = sentence.get('content', sentence.get('plain', 'N/A'))
                    print(f'Sentence {i+1}: "{content}" - {len(feedback)} issues')
                    for issue in feedback:
                        print(f'  - {issue.get("message", "No message")}')
    else:
        print('Error response:', response.text)
        
except Exception as e:
    print('Error occurred:', e)
