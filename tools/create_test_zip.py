import zipfile
import os

# Create a test ZIP file with some sample documents
def create_test_zip():
    # Create sample documents
    with open('test1.txt', 'w') as f:
        f.write("This is the first test document. It contains multiple sentences for analysis.")
    
    with open('test2.md', 'w') as f:
        f.write("# Test Markdown Document\n\nThis is a markdown document with **bold text** and *italic text*.\n\nIt has multiple paragraphs for testing.")
    
    # Create ZIP file
    with zipfile.ZipFile('test_documents.zip', 'w') as zipf:
        zipf.write('test1.txt')
        zipf.write('test2.md')
    
    # Clean up individual files
    os.remove('test1.txt')
    os.remove('test2.md')
    
    print("✅ Created test_documents.zip with sample files")

if __name__ == "__main__":
    create_test_zip()