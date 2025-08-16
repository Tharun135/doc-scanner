import requests
import json

try:
    files = {'file': ('test.txt', 'this is a test. microsoft should be capitalized.', 'text/plain')}
    response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=10)
    
    print('Status Code:', response.status_code)
    print('Response headers:', dict(response.headers))
    
    if response.status_code == 200:
        data = response.json()
        print('\n=== FULL RESPONSE ===')
        print(json.dumps(data, indent=2))
        
        sentences = data.get('sentences', [])
        print(f'\n=== SENTENCE ANALYSIS ===')
        print(f'Total sentences: {len(sentences)}')
        
        for i, sentence in enumerate(sentences):
            print(f'\nSentence {i+1}:')
            print(f'  Keys: {list(sentence.keys())}')
            print(f'  Content: {sentence.get("content", "N/A")[:100]}...')
            print(f'  Plain: {sentence.get("plain", "N/A")[:100]}...')
            print(f'  Feedback count: {len(sentence.get("feedback", []))}')
            
            feedback = sentence.get('feedback', [])
            for j, issue in enumerate(feedback):
                print(f'    Issue {j+1}: {issue}')
    else:
        print('Error response:', response.text)
        
except Exception as e:
    print('Error occurred:', e)
    import traceback
    traceback.print_exc()
