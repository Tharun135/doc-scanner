import requests
import time

# Test both endpoints to see which one you might be using
test_content = 'this is a test. microsoft should be capitalized.'

print("=== Testing /upload endpoint ===")
try:
    files = {'file': ('test.txt', test_content, 'text/plain')}
    response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=10)
    
    print('Status Code:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        sentences = data.get('sentences', [])
        total_issues = sum(len(s.get('feedback', [])) for s in sentences)
        print(f'Issues found: {total_issues}')
        if total_issues > 0:
            print('✅ /upload is working correctly!')
        else:
            print('❌ /upload found no issues')
    else:
        print('❌ /upload failed with error:', response.text)
except Exception as e:
    print('❌ /upload error:', e)

print("\n=== Testing /upload_progressive endpoint ===")
try:
    files = {'file': ('test.txt', test_content, 'text/plain')}
    response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=10)
    
    print('Status Code:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        if 'analysis_id' in data:
            print('✅ /upload_progressive started analysis with ID:', data['analysis_id'])
            print('Note: This endpoint requires polling for completion')
        else:
            sentences = data.get('sentences', [])
            if sentences:
                total_issues = sum(len(s.get('feedback', [])) for s in sentences)
                print(f'Issues found: {total_issues}')
                if total_issues > 0:
                    print('✅ /upload_progressive is working correctly!')
                else:
                    print('❌ /upload_progressive found no issues')
            else:
                print('❌ /upload_progressive returned no sentences')
    else:
        print('❌ /upload_progressive failed with error:', response.text)
except Exception as e:
    print('❌ /upload_progressive error:', e)

print("\n=== Summary ===")
print("If you're seeing 'no issues', check which endpoint your frontend is using.")
print("Both endpoints should now work with the new rules format.")
