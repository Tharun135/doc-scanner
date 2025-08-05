import requests

def test_upload():
    url = "http://127.0.0.1:5000/upload"
    
    # Create a simple test file content
    test_content = "This is a test document. It has some content to analyze for grammar and style issues."
    
    # Prepare the file for upload
    files = {
        'file': ('test.txt', test_content, 'text/plain')
    }
    
    try:
        print("Testing file upload...")
        response = requests.post(url, files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Upload successful!")
            print(f"Total sentences: {result.get('report', {}).get('totalSentences', 'N/A')}")
            print(f"Total words: {result.get('report', {}).get('totalWords', 'N/A')}")
            print(f"Quality score: {result.get('report', {}).get('avgQualityScore', 'N/A')}")
            
            # Show first few sentences analyzed
            sentences = result.get('sentences', [])
            for i, sentence in enumerate(sentences[:3]):  # Show first 3 sentences
                print(f"\nSentence {i+1}: {sentence['sentence']}")
                if sentence['feedback']:
                    for feedback in sentence['feedback']:
                        print(f"  - {feedback.get('message', 'No message')}")
                else:
                    print("  - No issues found")
        else:
            print(f"Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out - server may be too slow")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()
