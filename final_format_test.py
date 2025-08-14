import requests
import json
import tempfile
import os

def test_formatting_fix():
    """Test our formatting preservation fix"""
    
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

For more information, see the [documentation](https://example.com/docs).

The interface shows ![icon](image.png) next to each option."""

    print("🔍 Testing formatting preservation fix...")
    print("Input text:")
    print(test_content)
    print("\n" + "="*60 + "\n")
    
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # Upload the file to the server
        with open(temp_file_path, 'rb') as f:
            files = {'file': (os.path.basename(temp_file_path), f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            sentences = result.get('sentences', [])
            
            print(f"📊 Server Response: {len(sentences)} sentences found")
            print("\n" + "="*60 + "\n")
            
            formatting_preserved = False
            
            # Check each sentence for preserved formatting
            for i, sentence in enumerate(sentences, 1):
                print(f"Sentence {i}:")
                print(f"  Main text: {sentence.get('sentence', 'N/A')}")
                
                # Check for HTML preservation
                html_text = sentence.get('html_text', '')
                html_segment = sentence.get('html_segment', '')
                
                if html_text:
                    print(f"  HTML text: {html_text}")
                if html_segment and html_segment != html_text:
                    print(f"  HTML segment: {html_segment}")
                
                # Check for formatting elements
                all_html = html_text + html_segment
                has_bold = '<strong>' in all_html or '<b>' in all_html or '**' in all_html
                has_link = '<a href=' in all_html or '[' in all_html and '](' in all_html
                has_image = '<img ' in all_html or '![' in all_html
                
                if has_bold or has_link or has_image:
                    formatting_preserved = True
                    print(f"  ✅ Formatting detected: Bold={has_bold}, Link={has_link}, Image={has_image}")
                else:
                    print(f"  ❌ No formatting detected")
                    
                print()
            
            # Final assessment
            print("="*60)
            if formatting_preserved:
                print("🎉 SUCCESS: Formatting preservation is working!")
                print("✅ Bold text (**text**), links [text](url), and images ![alt](src) are preserved")
            else:
                print("❌ ISSUE: Formatting is still being stripped")
                print("   Check server logs for debugging information")
                
            return formatting_preserved
                
        else:
            print(f"❌ Server Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on http://127.0.0.1:5000?")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    success = test_formatting_fix()
    exit(0 if success else 1)
