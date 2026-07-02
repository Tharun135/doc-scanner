import requests
import os

def test_upload():
    url = "http://127.0.0.1:5000/upload"
    file_path = r"d:\doc-scanner\data\siemens_rule_test.txt"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found")
        return

    # Start session first
    room_url = "http://127.0.0.1:5000/start_upload"
    room_resp = requests.post(room_url)
    room_id = room_resp.json().get('room_id')
    print(f"Room ID: {room_id}")

    files = {'file': open(file_path, 'rb')}
    data = {'room_id': room_id}
    
    print("Uploading...")
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Upload success!")
            print(f"Sentences: {len(result.get('sentences', []))}")
            print(f"Total Issues: {result.get('report', {}).get('totalErrors', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("CRASH! Connection reset by peer.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_upload()
