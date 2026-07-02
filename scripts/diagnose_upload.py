
import requests
import os

def test_upload_flow():
    base_url = "http://localhost:5000"
    
    print("Step 1: Testing /start_upload...")
    try:
        response = requests.post(f"{base_url}/start_upload")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            room_id = data.get('room_id')
            print(f"Room ID: {room_id}")
        else:
            print(f"Error: {response.text}")
            return
    except Exception as e:
        print(f"Connection failed: {e}")
        return
        
    print("\nStep 2: Testing /upload...")
    # Create a dummy file
    with open("test_dummy.txt", "w") as f:
        f.write("This is a test document for DocScanner. It should be processed correctly.")
    
    try:
        with open("test_dummy.txt", "rb") as f:
            files = {'file': f}
            data = {'room_id': room_id}
            response = requests.post(f"{base_url}/upload", files=files, data=data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Upload success!")
                # print(response.json())
            else:
                print(f"Upload failed: {response.text}")
    except Exception as e:
        print(f"Upload failed: {e}")
    finally:
        if os.path.exists("test_dummy.txt"):
            os.remove("test_dummy.txt")

if __name__ == "__main__":
    test_upload_flow()
