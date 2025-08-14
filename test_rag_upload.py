import requests
import json

# Test file upload to check RAG integration
url = "http://127.0.0.1:5000/upload_progressive"

# Test content with various issues
test_content = """The document was written by the author. This is a very long sentence that contains multiple clauses and ideas that should probably be broken down into shorter, more digestible pieces for better readability and clarity. The report was completed by the team very quickly."""

with open("test_rag_upload.txt", "w") as f:
    f.write(test_content)

try:
    with open("test_rag_upload.txt", "rb") as f:
        files = {"file": ("test_rag_upload.txt", f, "text/plain")}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        analysis_id = result.get("analysis_id")
        print(f"Analysis ID: {analysis_id}")
        
        # Get progress
        progress_url = f"http://127.0.0.1:5000/progress/{analysis_id}"
        progress_response = requests.get(progress_url)
        if progress_response.status_code == 200:
            progress = progress_response.json()
            print(f"Progress: {json.dumps(progress, indent=2)}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {e}")
