# Tests Directory

This directory contains all test files, debug scripts, and demo code for the Doc Scanner project.

## File Organization

### 🧪 **Test Files**
- `test_*.py` - Python test scripts for various components
- `test_*.md` - Markdown test documents
- `test_*.txt` - Text test files

### 🐛 **Debug Scripts**
- `debug_rag_status.py` - Debug RAG (Retrieval Augmented Generation) functionality
- `debug_url_regex.py` - Debug URL detection patterns

### 🎯 **Demo Scripts**
- `demo_suggestion_flow.py` - Demonstrate the suggestion generation workflow

## Test Categories

### **Core Functionality Tests**
- `test_complete_rag_flow.py` - End-to-end RAG system testing
- `test_migration_success.py` - Verify LlamaIndex migration success
- `test_knowledge_base.py` - Knowledge base functionality tests

### **AI & Suggestion Tests**
- `test_passive_voice_fix.py` - Passive voice detection and correction
- `test_formatted_suggestions.py` - Suggestion formatting tests
- `test_response_structure.py` - AI response structure validation

### **Text Processing Tests**
- `test_sentence_processing.py` - Sentence analysis and processing
- `test_word_splitting.py` - Word tokenization and splitting
- `test_special_chars.py` - Special character handling

### **URL & Content Detection**
- `test_url_highlighting.py` - URL detection and highlighting
- `test_html_url_detection.py` - HTML content URL extraction
- `test_improved_url_detection.py` - Enhanced URL pattern matching

### **Integration Tests**
- `test_full_integration.py` - Complete system integration tests
- `test_api_endpoint.py` - API endpoint functionality
- `test_rewriting_integration.py` - Text rewriting system tests

### **Edge Case Tests**
- `test_edge_cases.py` - Unusual input scenarios
- `test_edge_cases_root.py` - Additional edge case scenarios
- `test_no_technical_terms.py` - Non-technical content handling

## Running Tests

### Individual Test Files
```bash
# Run a specific test
python tests/test_migration_success.py

# Run debug script
python tests/debug_rag_status.py

# Run demo
python tests/demo_suggestion_flow.py
```

### All Tests (if using pytest)
```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

## Test Data Files

### Sample Content
- `test_media.md` - Markdown test document
- `test_url_highlighting.md` - URL highlighting test content
- `test_upload.txt` - Sample upload content
- `test_excessive_exclamation.txt` - Punctuation test content

### Templates
- `test_note_template.md` - Note template for testing
- `test_note_only.md` - Note-only content test

## Contributing Tests

When adding new tests:

1. **Name your test files** with the `test_` prefix
2. **Include docstrings** explaining what the test does
3. **Test both success and failure cases** when applicable
4. **Add your test description** to this README
5. **Use meaningful test data** that represents real-world scenarios

## Test Environment Setup

Most tests require the Doc Scanner application to be properly initialized:

```python
import sys
import os
# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
```

## Current Test Count
- **Total files**: 63
- **Python test scripts**: ~45
- **Debug/Demo scripts**: 3
- **Test data files**: ~15

---

*All test files have been organized in this central location for better project structure and maintainability.*
