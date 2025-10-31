#!/usr/bin/env python3
"""
Debug script to test document upload functionality and identify where it's hanging.
"""

import os
import sys
import logging
import tempfile
from io import BytesIO

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_parse_file_function():
    """Test the parse_file function with a simple text file."""
    print("\n🔍 Testing parse_file function...")
    
    try:
        # Import the parse_file function
        from app.app import parse_file
        
        # Create a simple test file
        test_content = "This is a test document.\nIt has multiple paragraphs.\n\nThis is the second paragraph."
        
        # Create a mock file object
        class MockFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
                self._position = 0
            
            def read(self):
                return self.content.encode('utf-8')
            
            def seek(self, position):
                self._position = position
        
        # Test with different file types
        test_files = [
            ("test.txt", test_content),
            ("test.md", "# Test Markdown\n\nThis is a **test** document."),
        ]
        
        for filename, content in test_files:
            print(f"  📄 Testing {filename}...")
            mock_file = MockFile(filename, content)
            
            try:
                result = parse_file(mock_file)
                print(f"    ✅ Parsed successfully: {len(result)} characters")
                print(f"    📝 Content preview: {result[:100]}...")
            except Exception as e:
                print(f"    ❌ Parse failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import or setup failed: {e}")
        return False

def test_sentence_extraction():
    """Test the sentence extraction function."""
    print("\n🔍 Testing sentence extraction...")
    
    try:
        from app.app import extract_sentences_with_html_preservation
        
        # Test HTML content
        html_content = "<p>This is the first sentence. This is the second sentence.</p><p>This is another paragraph.</p>"
        
        print("  📝 Testing sentence extraction...")
        sentences = extract_sentences_with_html_preservation(html_content)
        
        print(f"    ✅ Extracted {len(sentences)} sentences")
        for i, sent in enumerate(sentences):
            print(f"    📄 Sentence {i+1}: {sent.text[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentence extraction failed: {e}")
        return False

def test_analysis_function():
    """Test the sentence analysis function."""
    print("\n🔍 Testing sentence analysis...")
    
    try:
        from app.app import analyze_sentence, load_rules
        
        # Load rules
        print("  📚 Loading rules...")
        rules = load_rules()
        print(f"    ✅ Loaded {len(rules)} rules")
        
        # Test sentence analysis
        test_sentence = "This is a simple test sentence that should be analyzed quickly."
        
        print("  🔍 Analyzing test sentence...")
        feedback, readability_scores, quality_score = analyze_sentence(test_sentence, rules)
        
        print(f"    ✅ Analysis complete!")
        print(f"    📊 Feedback items: {len(feedback)}")
        print(f"    📈 Quality score: {quality_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_progress_tracker():
    """Test the progress tracker functionality."""
    print("\n🔍 Testing progress tracker...")
    
    try:
        from app.progress_tracker import get_progress_tracker
        
        progress_tracker = get_progress_tracker()
        if progress_tracker:
            print("    ✅ Progress tracker available")
            
            # Test session creation
            room_id = "test_room_123"
            progress_tracker.start_session(room_id)
            print("    ✅ Session started")
            
            # Test stage updates
            progress_tracker.update_stage(room_id, 0, "Testing stage 1...")
            progress_tracker.update_stage(room_id, 1, "Testing stage 2...")
            print("    ✅ Stage updates work")
            
            # Complete session
            progress_tracker.complete_session(room_id, success=True)
            print("    ✅ Session completed")
            
        else:
            print("    ⚠️ Progress tracker not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Progress tracker failed: {e}")
        return False

def test_full_upload_simulation():
    """Simulate the full upload process to identify where it hangs."""
    print("\n🔍 Testing full upload simulation...")
    
    try:
        # Import required functions
        from app.app import parse_file, extract_sentences_with_html_preservation, analyze_sentence, load_rules
        from app.progress_tracker import get_progress_tracker
        from bs4 import BeautifulSoup
        
        # Mock file
        class MockFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
            
            def read(self):
                return self.content.encode('utf-8')
        
        # Create test file
        test_file = MockFile("test_doc.txt", "This is a test document with multiple sentences. It should be processed quickly. This is the third sentence.")
        
        # Initialize components
        print("  🔧 Initializing components...")
        progress_tracker = get_progress_tracker()
        rules = load_rules()
        room_id = "test_simulation"
        
        if progress_tracker:
            progress_tracker.start_session(room_id)
            print("    ✅ Progress tracker started")
        
        # Stage 1: Upload (simulated)
        if progress_tracker:
            progress_tracker.update_stage(room_id, 0, f"Uploading {test_file.filename}...")
        print("  📤 Stage 1: Upload - OK")
        
        # Stage 2: Parse
        if progress_tracker:
            progress_tracker.update_stage(room_id, 1, f"Parsing {test_file.filename.split('.')[-1].upper()} content...")
        
        print("  📄 Stage 2: Parsing...")
        html_content = parse_file(test_file)
        print(f"    ✅ Parsed: {len(html_content)} characters")
        
        # Stage 3: Extract sentences
        if progress_tracker:
            progress_tracker.update_stage(room_id, 2, "Identifying sentence boundaries...")
        
        print("  ✂️ Stage 3: Extracting sentences...")
        sentences = extract_sentences_with_html_preservation(html_content)
        print(f"    ✅ Extracted: {len(sentences)} sentences")
        
        # Extract plain text
        soup = BeautifulSoup(html_content, "html.parser")
        plain_text = soup.get_text(separator="\n")
        
        # Stage 4: Analysis
        if progress_tracker:
            progress_tracker.update_stage(room_id, 3, "Applying rules...")
        
        print("  🔍 Stage 4: Analysis...")
        sentence_data = []
        for index, sent in enumerate(sentences):
            print(f"    📄 Analyzing sentence {index + 1}/{len(sentences)}...")
            
            feedback, readability_scores, quality_score = analyze_sentence(sent.text, rules)
            sentence_data.append({
                "sentence": sent.text,
                "feedback": feedback,
                "readability_scores": readability_scores,
                "quality_score": quality_score
            })
        
        print(f"    ✅ Analyzed: {len(sentence_data)} sentences")
        
        # Stage 5: Report
        if progress_tracker:
            progress_tracker.update_stage(room_id, 4, "Generating report...")
        
        total_errors = sum(len(s['feedback']) for s in sentence_data)
        print(f"  📊 Stage 5: Report - {total_errors} issues found")
        
        # Complete
        if progress_tracker:
            progress_tracker.complete_session(room_id, success=True)
        
        print("  🎉 Full simulation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Full simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debug tests."""
    print("🚀 DocScanner Upload Debug Test Suite")
    print("=" * 50)
    
    tests = [
        ("Parse File Function", test_parse_file_function),
        ("Sentence Extraction", test_sentence_extraction),
        ("Analysis Function", test_analysis_function),
        ("Progress Tracker", test_progress_tracker),
        ("Full Upload Simulation", test_full_upload_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The upload process should work correctly.")
        print("💡 If the web interface is still hanging, the issue might be:")
        print("   - WebSocket connection problems")
        print("   - Frontend JavaScript errors")
        print("   - Network/browser issues")
        print("   - Missing Flask-SocketIO dependency")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. These issues need to be fixed first.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)