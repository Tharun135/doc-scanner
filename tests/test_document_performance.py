"""
Performance Analysis - Document Processing Time
Test what's causing the 30-second delay for 27 sentences
"""

import time
import requests
import os

def test_document_processing_performance():
    """Analyze where the time is spent during document processing."""
    print("⏱️ DOCUMENT PROCESSING PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Create a test document with 27 sentences
    test_sentences = [
        "This is the first test sentence.",
        "We need to analyze document processing speed.",
        "The API should process documents quickly.",
        "JSON and HTML formatting should be correct.",
        "Users expect fast response times.",
        "Performance optimization is critical for user experience.",
        "Local AI processing should be efficient.",
        "Grammar rules need to be applied consistently.",
        "Sentence analysis should not take too long.",
        "We have implemented lazy loading for better performance.",
        "SpaCy models should load only when needed.",
        "The RAG system provides intelligent suggestions.",
        "Technical terms must be properly capitalized.",
        "Passive voice should be detected accurately.",
        "Long sentences may need to be shortened.",
        "Word choice affects document quality.",
        "Style guidelines help maintain consistency.",
        "Terminology usage should follow best practices.",
        "Computer device terms require special attention.",
        "Cloud computing concepts need proper formatting.",
        "AI and machine learning terms are important.",
        "User interface elements should be described clearly.",
        "Software development practices vary across teams.",
        "Quality metrics help track improvement progress.",
        "Performance benchmarks guide optimization efforts.",
        "Document analysis results provide valuable insights.",
        "This is the final sentence for our test document."
    ]
    
    test_content = " ".join(test_sentences)
    print(f"📄 Test document: {len(test_sentences)} sentences, {len(test_content.split())} words")
    
    # Create test file
    test_file_path = "performance_test.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    try:
        print(f"\n🚀 Starting upload at {time.strftime('%H:%M:%S')}")
        start_time = time.time()
        
        # Upload and time the processing
        with open(test_file_path, 'rb') as f:
            files = {'file': ('performance_test.txt', f, 'text/plain')}
            print(f"📤 Uploading file...")
            response = requests.post("http://127.0.0.1:5000/upload", files=files, timeout=60)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ Processing completed at {time.strftime('%H:%M:%S')}")
        print(f"📊 PERFORMANCE RESULTS:")
        print(f"   Total processing time: {processing_time:.2f} seconds")
        print(f"   Time per sentence: {processing_time/len(test_sentences):.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            sentences_analyzed = len(result.get('sentences', []))
            total_words = result.get('report', {}).get('totalWords', 0)
            
            print(f"   ✅ Sentences processed: {sentences_analyzed}")
            print(f"   ✅ Words processed: {total_words}")
            
            # Performance analysis
            if processing_time > 20:
                print(f"\n🔴 VERY SLOW: {processing_time:.1f}s for {len(test_sentences)} sentences")
                print(f"   Expected: <3s for {len(test_sentences)} sentences")
                print(f"   Actual: {processing_time/len(test_sentences):.2f}s per sentence")
                print(f"   \n🔍 Likely bottlenecks:")
                print(f"   - Rule processing taking too long")
                print(f"   - spaCy model loading for each rule")
                print(f"   - RAG/AI processing adding delays")
                print(f"   - Multiple rule executions per sentence")
            elif processing_time > 10:
                print(f"\n🟡 SLOW: {processing_time:.1f}s is acceptable but could be better")
            else:
                print(f"\n🟢 GOOD: {processing_time:.1f}s is acceptable performance")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_document_processing_performance()
