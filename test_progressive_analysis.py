"""
Test script to demonstrate the progressive analysis feature
"""

import requests
import time
import json

def test_progressive_analysis():
    """Test the progressive analysis endpoint"""
    
    print("🔍 Testing Progressive Analysis Feature")
    print("=" * 50)
    
    # Test file content
    test_content = """
    This is a test document to demonstrate the progressive analysis feature.
    
    The system should show real-time progress updates as it processes this document.
    Each sentence will be analyzed individually, and users can see the percentage completion.
    
    This sentence is intentionally written in passive voice to trigger some feedback.
    Complex grammatical structures and long sentences may also be detected by the analysis engine.
    
    The progress indicator shows different stages: parsing, segmentation, analysis, and reporting.
    Users will see animated progress bars and detailed status messages throughout the process.
    
    This enhancement significantly improves user experience during document analysis.
    """
    
    # Create a test file
    files = {'file': ('test_progressive.txt', test_content, 'text/plain')}
    
    print("📤 Starting progressive analysis...")
    
    try:
        # Send file for progressive analysis
        response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            
            if analysis_id:
                print(f"✅ Analysis started with ID: {analysis_id}")
                print("\n📊 Progress Updates:")
                print("-" * 30)
                
                # Poll for progress
                completed = False
                while not completed:
                    progress_response = requests.get(f'http://127.0.0.1:5000/analysis_progress/{analysis_id}')
                    
                    if progress_response.status_code == 200:
                        progress = progress_response.json()
                        
                        percentage = progress.get('percentage', 0)
                        message = progress.get('message', 'Processing...')
                        stage = progress.get('stage', 'unknown')
                        
                        print(f"[{percentage:3.0f}%] {stage.upper()}: {message}")
                        
                        if progress.get('completed'):
                            completed = True
                            if progress.get('error'):
                                print(f"❌ Error: {progress['error']}")
                            else:
                                print("✅ Analysis completed successfully!")
                                if progress.get('result'):
                                    result = progress['result']
                                    report = result.get('report', {})
                                    print(f"\n📋 Analysis Summary:")
                                    print(f"   Total Sentences: {report.get('totalSentences', 'N/A')}")
                                    print(f"   Total Words: {report.get('totalWords', 'N/A')}")
                                    print(f"   Quality Score: {report.get('avgQualityScore', 'N/A')}%")
                        else:
                            time.sleep(0.5)  # Wait before next poll
                    else:
                        print(f"❌ Failed to get progress: {progress_response.status_code}")
                        break
            else:
                print("❌ No analysis ID returned")
        else:
            print(f"❌ Failed to start analysis: {response.status_code}")
            print(response.text)
            
    except requests.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_progressive_analysis()
