"""
Quick test to verify upload functionality and show RAG solutions
"""

import requests
import os

def test_upload_and_rag():
    """Test the upload and RAG functionality"""
    
    print("🧪 Testing Upload and RAG System")
    print("=" * 50)
    
    # Test data with issues that will trigger RAG responses
    test_text = """The report was completed by the team. In order to improve performance, we need to optimize the database. Hey guys, this is pretty awesome! The solution is really, really, really good."""
    
    # Create a test file
    test_file_path = "test_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_text)
    
    try:
        # Test file upload
        url = "http://127.0.0.1:5000/upload"
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"📊 Analysis Results:")
            print(f"   - Total sentences: {data['report']['totalSentences']}")
            print(f"   - Total words: {data['report']['totalWords']}")
            print(f"   - Quality score: {data['report']['avgQualityScore']}")
            
            print(f"\n🔍 Detected Issues:")
            for i, sentence_data in enumerate(data['sentences']):
                if sentence_data['feedback']:
                    print(f"\n   Sentence {i+1}: \"{sentence_data['sentence']}\"")
                    for issue in sentence_data['feedback']:
                        print(f"      🚨 Issue: {issue['message']}")
            
            print(f"\n🎯 TO SEE RAG SOLUTIONS:")
            print("1. Open http://127.0.0.1:5000 in your browser")
            print("2. Upload a document (like the sample_test_document.md)")
            print("3. Click on any RED highlighted text")
            print("4. Click 'AI Suggestion' button")
            print("5. See detailed RAG-powered solution with examples!")
            
            return True
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_rag_suggestion():
    """Test the RAG suggestion endpoint directly"""
    
    print(f"\n🤖 Testing RAG Suggestion Endpoint")
    print("=" * 50)
    
    try:
        url = "http://127.0.0.1:5000/ai_suggestion"
        test_data = {
            "feedback": "passive voice detected",
            "sentence": "The bug was fixed by the developer.",
            "document_type": "general"
        }
        
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RAG suggestion successful!")
            print(f"\n📝 RAG Response:")
            print(f"   💡 Suggestion: {data['suggestion'][:200]}...")
            print(f"   📚 Source: {data['source']}")
            print(f"   ⭐ Confidence: {data['confidence']}")
            print(f"   🏷️ Category: {data['category']}")
            
            return True
        else:
            print(f"❌ RAG suggestion failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Doc Scanner Upload & RAG Test")
    print("=" * 50)
    
    upload_ok = test_upload_and_rag()
    rag_ok = test_rag_suggestion()
    
    if upload_ok and rag_ok:
        print(f"\n🏆 SUCCESS: Both upload and RAG systems are working!")
        print(f"\n🌐 Your app is ready at: http://127.0.0.1:5000")
        print("📄 Upload any document to see RAG-powered suggestions!")
    else:
        print(f"\n⚠️ Some issues detected - check the logs above")
