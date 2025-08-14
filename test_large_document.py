#!/usr/bin/env python3
"""
Test with a large document to simulate the 31-sentence issue
"""

import requests
import time

def test_large_document():
    """Test with a document that has many sentences"""
    
    # Create a document with many sentences to trigger the issue
    large_content = """
The document was written by the author. This is the first sentence with issues.
The report was completed by the team. This is another sentence that needs review.
Data analysis was performed by researchers. Complex terminology is utilized throughout.
The system was designed by engineers. Very detailed documentation was provided.
Implementation was conducted by the development team. Extensive testing was performed.
The proposal was reviewed by management. Important decisions were made quickly.
Results were analyzed by statisticians. Comprehensive reports were generated.
The project was supervised by experienced professionals. Multiple phases were completed.
Quality control was maintained by dedicated staff. Rigorous standards were enforced.
The budget was managed by financial experts. Careful planning was executed.
Training was provided by qualified instructors. Thorough preparation was ensured.
The timeline was established by project managers. Clear milestones were defined.
Communication was facilitated by team leaders. Regular updates were shared.
Documentation was prepared by technical writers. Detailed specifications were created.
The database was maintained by IT specialists. Secure backups were performed.
User feedback was collected by research teams. Valuable insights were gathered.
The interface was designed by UX professionals. Intuitive navigation was implemented.
Security measures were implemented by cybersecurity experts. Robust protections were established.
Performance testing was conducted by quality assurance teams. Optimal functionality was verified.
The deployment was managed by operations staff. Smooth transitions were achieved.
Maintenance procedures were developed by support teams. Reliable operations were maintained.
Training materials were created by educational specialists. Effective learning was facilitated.
The evaluation was performed by assessment experts. Accurate measurements were obtained.
Feedback analysis was completed by research analysts. Meaningful patterns were identified.
The optimization was carried out by performance engineers. Significant improvements were achieved.
Risk assessment was conducted by safety professionals. Potential hazards were identified.
The integration was managed by technical architects. Seamless connectivity was established.
Compliance checking was performed by regulatory experts. All requirements were satisfied.
The review process was overseen by senior management. Final approval was obtained.
Implementation timeline was established by planning committees. Realistic deadlines were set.
Quality assurance was maintained throughout the entire process by dedicated teams.
""".strip()
    
    print("🔍 TESTING LARGE DOCUMENT (31+ sentences)")
    print("=" * 60)
    print(f"📝 Content length: {len(large_content)} characters")
    print(f"📝 Approximate sentences: {large_content.count('.')}")
    
    url = "http://localhost:5000/upload"
    files = {'file': ('large_test.txt', large_content.encode('utf-8'), 'text/plain')}
    
    try:
        print("\n📤 Uploading large document...")
        start_time = time.time()
        
        response = requests.post(url, files=files, timeout=60)  # Increased timeout
        
        processing_time = time.time() - start_time
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            
            sentences = result.get('sentences', [])
            print(f"📝 Sentences processed: {len(sentences)}")
            
            total_issues = sum(len(s.get('feedback', [])) for s in sentences)
            print(f"📈 Total issues found: {total_issues}")
            
            if processing_time > 30:
                print("⚠️  Warning: Processing took longer than expected")
            else:
                print("🚀 Processing completed within reasonable time")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - the distribution is likely stuck")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    test_large_document()
