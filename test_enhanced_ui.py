import requests
import time

def test_upload_with_ui():
    """Test file upload to see the enhanced UI in action"""
    
    print("🎯 Testing Enhanced Circular Progress UI")
    print("=" * 50)
    
    # Simple test content
    test_content = """
    This is a test document for the enhanced circular progress UI.
    
    The system should display a beautiful circular progress indicator.
    You should see a rotating gradient ring with percentage in the center.
    Below that, there should be a linear progress bar with shimmer effects.
    At the bottom, four stage indicator dots should light up as progress advances.
    
    This enhancement makes the waiting experience much more engaging.
    The glassmorphism design creates a modern, professional appearance.
    """
    
    files = {'file': ('ui_test.txt', test_content, 'text/plain')}
    
    print("📤 Uploading file to see enhanced UI...")
    print("💡 Check your browser to see the circular progress animation!")
    
    try:
        # Use regular upload endpoint to trigger the UI
        response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful! Did you see the enhanced circular progress UI?")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Could not connect. Make sure the server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload_with_ui()
