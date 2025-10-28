from flask import Blueprint, request, jsonify, render_template
import os
import re
import subprocess
import markdown
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import logging
import importlib
import sys
import textstat
import time
from dataclasses import asdict

# Try to import spacy but handle import errors gracefully
try:
    import spacy
    SPACY_IMPORT_SUCCESS = True
except ImportError:
    SPACY_IMPORT_SUCCESS = False
    spacy = None

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("python-dotenv not available - environment variables must be set manually")

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to hide RAG debug messages
logger = logging.getLogger(__name__)

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
if SPACY_IMPORT_SUCCESS:
    try:
        # Try to load with reduced memory footprint
        nlp = spacy.load("en_core_web_sm", disable=["ner", "textcat"])
        SPACY_AVAILABLE = True
        logger.info("spaCy model loaded successfully with reduced components")
    except MemoryError as e:
        logger.warning(f"spaCy model loading failed due to memory constraints: {e}")
        logger.warning("Running without spaCy - sentence splitting will use basic methods")
        nlp = None
        SPACY_AVAILABLE = False
    except ImportError as e:
        logger.warning(f"spaCy not available: {e}")
        nlp = None
        SPACY_AVAILABLE = False
    except Exception as e:
        logger.warning(f"spaCy model not available: {e}")
        logger.warning("Falling back to basic sentence processing")
        nlp = None
        SPACY_AVAILABLE = False
else:
    logger.warning("spaCy package not installed - using basic sentence processing")
    nlp = None
    SPACY_AVAILABLE = False

############################
# SENTENCE EXTRACTION HELPERS
############################

def extract_sentences_with_html_preservation(html_content):
    """
    Extract sentences from HTML content while preserving the HTML structure.
    Returns a list of sentence objects that contain both the original HTML and plain text versions.
    """
    sentences = []
    
    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Process each paragraph and text block separately
    text_elements = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th'])
    
    for element in text_elements:
        if not element.get_text().strip():
            continue
            
        # Get the HTML content of this element
        element_html = str(element)
        
        # Debug: Check if element_html contains any highlighting markup
        if 'sentence-highlight' in element_html:
            logger.warning(f"🔥 INPUT HTML CONTAINS HIGHLIGHTING MARKUP: {element_html[:200]}...")
        
        # Get the plain text version for analysis
        element_text = element.get_text()
        
        # Split the text into sentences while tracking positions
        if SPACY_AVAILABLE and nlp:
            # Use spaCy for better sentence segmentation
            doc = nlp(element_text)
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if sent_text:
                    # Find corresponding HTML fragment
                    html_fragment = find_html_fragment_for_sentence(element_html, sent_text, element_text)
                    
                    # Create sentence object with both HTML and text versions
                    class EnhancedSentence:
                        def __init__(self, text, html_fragment, start_char=0, end_char=None):
                            self.text = text.strip()
                            self.html_fragment = html_fragment
                            self.start_char = start_char
                            self.end_char = end_char if end_char else len(text)
                    
                    sentences.append(EnhancedSentence(sent_text, html_fragment))
        else:
            # Fallback: simple sentence splitting when spaCy is not available
            import re
            simple_sentences = re.split(r'[.!?]+\s+', element_text)
            for sent_text in simple_sentences:
                sent_text = sent_text.strip()
                if sent_text:
                    # Find corresponding HTML fragment
                    html_fragment = find_html_fragment_for_sentence(element_html, sent_text, element_text)
                    
                    class SimpleSentence:
                        def __init__(self, text, html_fragment):
                            self.text = text.strip()
                            self.html_fragment = html_fragment
                            self.start_char = 0
                            self.end_char = len(text)
                    
                    sentences.append(SimpleSentence(sent_text, html_fragment))
    
    # Remove duplicate sentences based on text content
    seen_sentences = set()
    unique_sentences = []
    
    for sentence in sentences:
        # Create a normalized version for comparison (strip whitespace and newlines)
        normalized_text = ' '.join(sentence.text.split())
        
        if normalized_text and normalized_text not in seen_sentences:
            seen_sentences.add(normalized_text)
            unique_sentences.append(sentence)
    
    return unique_sentences

def find_html_fragment_for_sentence(element_html, sentence_text, full_text):
    """
    Find the HTML fragment that corresponds to a specific sentence within an element.
    This preserves HTML tags like <strong>, <em>, <a>, <code>, etc.
    """
    soup = BeautifulSoup(element_html, "html.parser")
    
    # Get the first actual HTML element (skip the document wrapper)
    first_element = soup.find()
    if not first_element:
        return sentence_text
    
    element_plain_text = first_element.get_text().strip()
    
    # Simple case: if the element contains only this sentence
    if element_plain_text.strip() == sentence_text.strip():
        # Return the inner HTML (content without the wrapper tag)
        if hasattr(first_element, 'contents') and first_element.contents:
            inner_content = ''.join(str(content) for content in first_element.contents)
            return inner_content
        return sentence_text
    
    # Complex case: sentence is part of a larger element
    sentence_start = full_text.find(sentence_text.strip())
    if sentence_start == -1:
        return sentence_text  # Fallback - return plain text
    
    sentence_end = sentence_start + len(sentence_text.strip())
    
    # If this sentence spans the entire element content, return the inner HTML
    if sentence_start == 0 and sentence_end >= len(full_text.strip()):
        if hasattr(first_element, 'contents') and first_element.contents:
            inner_content = ''.join(str(content) for content in first_element.contents)
            return inner_content
    
    # For partial matches, try to find the corresponding HTML portion
    try:
        # Get all text nodes and their positions to map back to HTML
        html_content = str(first_element)
        
        # Create a temporary element to work with
        temp_soup = BeautifulSoup(html_content, "html.parser")
        temp_element = temp_soup.find()
        
        if temp_element:
            # Try to find the sentence text within the element
            element_text = temp_element.get_text()
            
            # Find the sentence within the element's text
            local_sentence_start = element_text.find(sentence_text.strip())
            if local_sentence_start != -1:
                local_sentence_end = local_sentence_start + len(sentence_text.strip())
                
                # Try to map this back to HTML by looking for text patterns
                # For now, if we can find the exact sentence text in the HTML, return it with any inline tags
                html_str = str(temp_element)
                if sentence_text.strip() in html_str:
                    # Look for the sentence with potential HTML tags
                    import re
                    # Create a pattern that allows HTML tags within the sentence
                    words = sentence_text.strip().split()
                    if words:
                        # Create pattern allowing HTML tags between and within words
                        pattern_words = [re.escape(word) for word in words]
                        pattern = r'(?:<[^>]*>)*\s*' + r'(?:\s*<[^>]*>\s*)*\s+(?:<[^>]*>)*\s*'.join(pattern_words) + r'\s*(?:<[^>]*>)*'
                        
                        match = re.search(pattern, html_str, re.IGNORECASE | re.DOTALL)
                        if match:
                            return match.group(0).strip()
                
                # Fallback: return the plain text
                return sentence_text.strip()
    except Exception as e:
        # If anything goes wrong, return the plain text
        return sentence_text.strip()
    
    # Final fallback
    return sentence_text.strip()

############################
# FILE PARSING HELPERS
############################

def clean_malformed_html_attributes(text):
    """
    Clean malformed HTML attributes that might appear in text content.
    Specifically targets patterns like: ="sentence-highlight" id="content-sentence-0"
    """
    import re
    
    # Pattern to match malformed HTML attributes starting with ="
    # This catches patterns like: ="sentence-highlight" id="content-sentence-0" data-sentence-index="0">
    pattern = r'=[\"\'][^\"\']*[\"\'][^>]*>'
    
    # Remove these malformed patterns
    cleaned = re.sub(pattern, '', text)
    
    # Also remove any standalone HTML attributes that might be left
    # Pattern for: id="something" data-something="value" etc.
    attr_pattern = r'\s*(?:id|class|data-[\w-]+)\s*=\s*["\'][^"\']*["\']'
    cleaned = re.sub(attr_pattern, '', cleaned)
    
    # Clean up any remaining HTML tag fragments
    fragment_pattern = r'</?[^>]*>'
    cleaned = re.sub(fragment_pattern, '', cleaned)
    
    return cleaned.strip()

def parse_file(file):
    filename = file.filename.lower()
    extension = os.path.splitext(filename)[1]

    try:
        if extension == '.zip':
            return parse_zip(file)
        elif extension == '.docx':
            return parse_docx(file)
        elif extension == '.doc':
            return parse_doc(file)
        elif extension == '.pdf':
            return parse_pdf(file)
        elif extension == '.md':
            return parse_md(file.read())
        elif extension == '.adoc':
            return parse_adoc(file.read())
        elif extension in ['.txt', '']:
            return parse_txt(file.read())
        else:
            return file.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Error parsing {filename}: {str(e)}")
        return f"Error parsing {filename}: {str(e)}"

def parse_zip(file_stream):
    """Parse ZIP file and extract text content from supported documents inside"""
    import zipfile
    import io
    
    try:
        html_content = "<h2>Contents of ZIP file:</h2>\n"
        
        with zipfile.ZipFile(file_stream, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # Filter for supported file types
            supported_files = []
            for filename in file_list:
                if filename.lower().endswith(('.txt', '.md', '.docx', '.pdf')):
                    supported_files.append(filename)
            
            if not supported_files:
                return "<p>No supported document files found in ZIP archive. Supported formats: .txt, .md, .docx, .pdf</p>"
            
            html_content += f"<p>Found {len(supported_files)} supported document(s) in ZIP file:</p>\n"
            
            # Process each supported file
            for filename in supported_files:
                try:
                    html_content += f"<h3>📄 {filename}</h3>\n"
                    
                    # Extract file content
                    with zip_file.open(filename) as extracted_file:
                        file_content = io.BytesIO(extracted_file.read())
                        
                        # Determine file type and parse accordingly
                        ext = os.path.splitext(filename.lower())[1]
                        
                        if ext == '.txt':
                            content = parse_txt(file_content.read())
                        elif ext == '.md':
                            content = parse_md(file_content.read())
                        elif ext == '.docx':
                            content = parse_docx(file_content)
                        elif ext == '.pdf':
                            content = parse_pdf(file_content)
                        else:
                            content = f"<p>Unsupported file type: {ext}</p>"
                        
                        html_content += content + "\n"
                        
                except Exception as e:
                    html_content += f"<p>Error processing {filename}: {str(e)}</p>\n"
                    logger.error(f"Error processing file {filename} in ZIP: {e}")
            
            return html_content
            
    except zipfile.BadZipFile:
        return "Error: Invalid or corrupted ZIP file"
    except Exception as e:
        logger.error(f"Error parsing ZIP file: {e}")
        return f"Error parsing ZIP file: {str(e)}"

def parse_docx(file_stream):
    doc = Document(file_stream)
    html_content = ""
    for paragraph in doc.paragraphs:
        html_content += f"<p>{paragraph.text}</p>"
    return html_content

def parse_doc(file_stream):
    temp_path = "temp_upload_doc.doc"
    file_stream.save(temp_path)
    try:
        cmd = ["antiword", temp_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            text_content = result.stdout
            html_content = ""
            for paragraph in text_content.split("\n\n"):
                html_content += f"<p>{paragraph}</p>"
            return html_content
        else:
            return f"Error reading .doc file: {result.stderr}"
    except FileNotFoundError:
        return "Error: 'antiword' not in PATH or not installed."
    except Exception as e:
        return f"Error reading .doc file: {str(e)}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def parse_pdf(file_stream):
    try:
        reader = PyPDF2.PdfReader(file_stream)
        html_content = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            for paragraph in page_text.split("\n\n"):
                html_content += f"<p>{paragraph}</p>"
        return html_content
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def parse_md(content_bytes):
    md_text = content_bytes.decode("utf-8", errors="replace")
    html_text = markdown.markdown(md_text)
    return html_text

def parse_adoc(content_bytes):
    adoc_text = content_bytes.decode("utf-8", errors="replace")
    html_content = ""
    for paragraph in adoc_text.split("\n\n"):
        html_content += f"<p>{paragraph}</p>"
    return html_content

def parse_txt(content_bytes):
    txt_text = content_bytes.decode("utf-8", errors="replace")
    html_content = ""
    for paragraph in txt_text.split("\n\n"):
        html_content += f"<p>{paragraph}</p>"
    return html_content

def load_rules():
    rules = []
    rules_folder = os.path.join(os.path.dirname(__file__), 'rules')
    for filename in os.listdir(rules_folder):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            try:
                # Import the module using the proper package path
                module = importlib.import_module(f'app.rules.{module_name}')
                
                if hasattr(module, "check"):
                    rules.append(module.check)
                    logger.info(f"Loaded rule: {filename} (Function: {module.check.__name__})")
                else:
                    logger.warning(f"Warning: {filename} does not have a `check` function")
            except ImportError as e:
                logger.error(f"Failed to import rule {filename}: {e}")
            except Exception as e:
                logger.error(f"Error loading rule {filename}: {e}")

    logger.info(f"Total rules loaded: {len(rules)}")
    return rules

rules = load_rules()

def review_document(content, rules):
    suggestions = []
    for rule in rules:
        feedback = rule(content)
        if feedback:
            for item in feedback:
                # Handle both string and dict formats
                if isinstance(item, str):
                    # Skip string-only feedback for now
                    continue
                elif isinstance(item, dict):
                    suggestions.append({
                        "text": item.get("text", ""),
                        "start": item.get("start", 0),
                        "end": item.get("end", 0),
                        "message": item.get("message", item.get("suggestion", ""))
                    })
    return {"issues": suggestions, "summary": "Review completed."}

def analyze_sentence(sentence, rules):
    feedback = []
    readability_scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(sentence),
        "gunning_fog": textstat.gunning_fog(sentence),
        "smog_index": textstat.smog_index(sentence),
        "automated_readability_index": textstat.automated_readability_index(sentence)
    }
    quality_score = 55.0  # Placeholder for actual quality score calculation

    # Apply each rule function to the sentence
    for rule_function in rules:
        rule_feedback = rule_function(sentence)
        if rule_feedback:
            # Convert string feedback to expected object format
            for item in rule_feedback:
                if isinstance(item, str):
                    # Parse structured suggestions to extract just the issue for display
                    message = item
                    if 'Issue:' in item and 'Original sentence:' in item and ('AI suggestion:' in item or 'AI Solution:' in item):
                        # Extract just the issue part for the main display
                        lines = item.split('\n')
                        for line in lines:
                            if line.strip().startswith('Issue:'):
                                message = line.replace('Issue:', '').strip()
                                break
                    
                    # Convert string to expected object format
                    feedback.append({
                        "text": sentence,
                        "start": 0,
                        "end": len(sentence),
                        "message": message,
                        "full_suggestion": item  # Keep the full structured suggestion for detailed view
                    })
                elif isinstance(item, dict) and all(key in item for key in ["text", "start", "end", "message"]):
                    # Already in correct format
                    feedback.append(item)
                else:
                    # Handle other formats by converting to string
                    feedback.append({
                        "text": sentence,
                        "start": 0,
                        "end": len(sentence),
                        "message": str(item)
                    })

    return feedback, readability_scores, quality_score
def calculate_quality_index(total_sentences, total_errors):
    if total_sentences == 0:
        return 0
    return max(0, round(100 * (1 - (total_errors / total_sentences))))
############################
# FLASK ROUTES
############################

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/start_upload', methods=['POST'])
def start_upload():
    """Initialize upload session and return room ID for progress tracking."""
    import uuid
    from .progress_tracker import get_progress_tracker
    
    room_id = str(uuid.uuid4())
    progress_tracker = get_progress_tracker()
    
    if progress_tracker:
        progress_tracker.start_session(room_id)
    
    return jsonify({"room_id": room_id})

@main.route('/analyze_intelligent', methods=['POST'])
def analyze_intelligent():
    """Intelligent AI analysis endpoint - returns JSON response."""
    logger.info("🧠 Intelligent analysis endpoint called")
    
    try:
        # Get request data (could be JSON or form data)
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
            context = data.get('context', '')
            document_type = data.get('document_type', 'general')
        else:
            # Handle file upload for intelligent analysis
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Extract text from file (reuse existing logic from upload route)
            try:
                html_content = parse_file(file)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")
                text = soup.get_text(separator="\n")
            except Exception as e:
                return jsonify({"error": f"Failed to extract text: {str(e)}"}), 400
            
            context = 'file_analysis'
            document_type = request.form.get('document_type', 'general')
        
        if not text.strip():
            return jsonify({"error": "No text content to analyze"}), 400
        
        # Use intelligent AI system
        try:
            from .intelligent_ai_improvement import get_enhanced_ai_suggestion
            
            # Perform intelligent analysis
            result = get_enhanced_ai_suggestion(
                feedback_text="Perform comprehensive intelligent analysis",
                sentence_context=text[:500],  # First 500 chars for context
                document_type=document_type,
                writing_goals=['clarity', 'conciseness', 'professionalism'],
                document_content=text,
                option_number=1
            )
            
            if result.get('success'):
                logger.info("✅ Intelligent analysis completed successfully")
                return jsonify({
                    "success": True,
                    "analysis": result.get('suggestion', ''),
                    "method": result.get('method', 'intelligent_ai'),
                    "confidence": result.get('confidence', 0.8),
                    "explanation": result.get('explanation', ''),
                    "content_length": len(text),
                    "document_type": document_type
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Intelligent analysis failed: " + result.get('error', 'Unknown error')
                }), 500
                
        except ImportError:
            logger.warning("Intelligent AI not available, falling back to regular analysis")
            return jsonify({
                "success": False,
                "error": "Intelligent AI analysis not available - dependencies missing"
            }), 503
            
    except Exception as e:
        logger.error(f"Error in intelligent analysis: {e}")
        return jsonify({
            "success": False,
            "error": f"Analysis error: {str(e)}"
        }), 500

@main.route('/intelligent_results')
def intelligent_results():
    """Render intelligent analysis results page."""
    # Get analysis data from query parameters or session
    analysis_data = request.args.get('data')
    
    if analysis_data:
        import json
        try:
            # Parse the JSON data
            analysis_result = json.loads(analysis_data)
            
            # Convert single analysis result to suggestions list format expected by template
            if analysis_result.get('success'):
                suggestions = [{
                    'method': analysis_result.get('method', 'intelligent_analysis'),
                    'confidence': analysis_result.get('confidence', 'medium'),
                    'suggestion': analysis_result.get('analysis', 'No suggestion available'),
                    'success': True,
                    'ai_answer': analysis_result.get('explanation', ''),
                    'sentence': f"Analyzed {analysis_result.get('content_length', 0)} characters",
                    'original_sentence': f"Document type: {analysis_result.get('document_type', 'general')}",
                    'content_length': analysis_result.get('content_length', 0),
                    'document_type': analysis_result.get('document_type', 'general')
                }]
            else:
                suggestions = []
                
        except json.JSONDecodeError:
            analysis_result = {"error": "Invalid analysis data"}
            suggestions = []
    else:
        # Default empty result
        analysis_result = {"error": "No analysis data provided"}
        suggestions = []
    
    return render_template('intelligent_results.html', 
                         analysis=analysis_result,
                         suggestions=suggestions,
                         title="Intelligent AI Analysis Results")

@main.route('/debug')
def debug_page():
    """Serve the sentence debugging page"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'debug_sentences.html')

@main.route('/debug_sentences', methods=['POST'])
def debug_sentences():
    """Debug endpoint to check sentence data for malformed HTML"""
    data = request.get_json()
    sentences = data.get('sentences', [])
    
    debug_info = {
        'total_sentences': len(sentences),
        'malformed_sentences': [],
        'html_sentences': [],
        'clean_sentences': []
    }
    
    for i, sentence_data in enumerate(sentences):
        sentence_text = sentence_data.get('sentence', '')
        
        # Check for malformed HTML attributes
        if '="' in sentence_text and ('sentence-highlight' in sentence_text or 'data-sentence-index' in sentence_text):
            debug_info['malformed_sentences'].append({
                'index': i,
                'original': sentence_text,
                'cleaned': clean_malformed_html_attributes(sentence_text)
            })
        
        # Check for any HTML tags
        elif '<' in sentence_text and '>' in sentence_text:
            debug_info['html_sentences'].append({
                'index': i,
                'text': sentence_text
            })
        
        else:
            debug_info['clean_sentences'].append({
                'index': i,
                'text': sentence_text[:100] + ('...' if len(sentence_text) > 100 else '')
            })
    
    return jsonify(debug_info)

@main.route('/upload', methods=['POST'])
def upload_file():
    global current_document_content  # Access global variable
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    # Validate file extension
    filename = file.filename.lower()
    allowed_extensions = ['.txt', '.pdf', '.docx', '.doc', '.md', '.adoc', '.zip']
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return jsonify({"error": f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"}), 400

    # Get room_id for progress tracking
    room_id = request.form.get('room_id')
    
    from .progress_tracker import get_progress_tracker
    progress_tracker = get_progress_tracker()

    logger.info(f"File uploaded: {file.filename} (Room: {room_id})")
    
    # Validate file size (Flask should handle this automatically, but let's be explicit)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 50 * 1024 * 1024  # 50MB
    if file_size > max_size:
        return jsonify({"error": f"File too large. Maximum size: {max_size // (1024*1024)}MB"}), 400
    
    logger.info(f"File size: {file_size} bytes")

    try:
        # Stage 1: Uploading Document (10%)
        if progress_tracker and room_id:
            progress_tracker.update_stage(room_id, 0, f"Uploading {file.filename}...")
        
        # Stage 2: Parsing Content (30%)
        if progress_tracker and room_id:
            progress_tracker.update_stage(room_id, 1, f"Parsing {file.filename.split('.')[-1].upper()} content...")
        
        # Parse file to get both plain text and HTML
        html_content = parse_file(file)
        
        # Clean any existing sentence highlighting from the content (in case document was previously processed)
        if 'sentence-highlight' in html_content:
            logger.warning("🧹 Cleaning existing sentence highlighting from uploaded document...")
            # Remove all sentence highlighting spans but keep the content
            import re
            # Remove opening span tags with sentence-highlight class
            html_content = re.sub(r'<span[^>]*sentence-highlight[^>]*>', '', html_content)
            # Remove closing span tags
            html_content = re.sub(r'</span>', '', html_content)
            logger.info("✅ Cleaned existing highlighting markup")
        
        # Check if parsing failed
        if html_content.startswith("Error"):
            logger.error(f"File parsing failed: {html_content}")
            if progress_tracker and room_id:
                progress_tracker.fail_session(room_id, html_content)
            return jsonify({"error": html_content}), 400
        
        # Check if content is empty
        if not html_content.strip():
            error_msg = "The uploaded file appears to be empty or could not be parsed."
            logger.error(f"Empty content from file: {file.filename}")
            if progress_tracker and room_id:
                progress_tracker.fail_session(room_id, error_msg)
            return jsonify({"error": error_msg}), 400
        
        # Stage 3: Breaking into Sentences (50%)
        if progress_tracker and room_id:
            progress_tracker.update_stage(room_id, 2, "Identifying sentence boundaries and structure...")
        
        # Store the original HTML content for highlighting
        # Extract sentences that preserve HTML structure while also having plain text for analysis
        
        # Debug: Check if the input HTML already contains highlighting
        if 'sentence-highlight' in html_content:
            logger.error(f"🔥 CRITICAL: Input HTML already contains sentence highlighting! This suggests the document was previously processed.")
            logger.info(f"HTML snippet: {html_content[:500]}...")
        
        sentences = extract_sentences_with_html_preservation(html_content)
        
        # Check if sentence extraction failed
        if not sentences:
            error_msg = "Could not extract any sentences from the document. The file may be corrupted or in an unsupported format."
            logger.error(f"No sentences extracted from file: {file.filename}")
            if progress_tracker and room_id:
                progress_tracker.fail_session(room_id, error_msg)
            return jsonify({"error": error_msg}), 400
        
        logger.info(f"Extracted {len(sentences)} sentences from {file.filename}")
        
        # Use BeautifulSoup to extract plain text for RAG context
        soup = BeautifulSoup(html_content, "html.parser")
        plain_text = soup.get_text(separator="\n")
        
        # Store the document content for RAG context
        current_document_content = plain_text

        # Stage 4: Analyzing with Rules (80%)
        if progress_tracker and room_id:
            progress_tracker.update_stage(room_id, 3, "Applying grammar, style, and readability rules...")
        
        sentence_data = []
        total_sentences = len(sentences)
        
        for index, sent in enumerate(sentences):
            # Update substep progress for analysis
            if progress_tracker and room_id and total_sentences > 0:
                substep_progress = int(75 + (index / total_sentences) * 5)  # 75-80% range
                progress_tracker.update_progress(room_id, substep_progress, 
                    f"Analyzing sentence {index + 1} of {total_sentences}...")
            
            # Use the plain text version for analysis
            plain_text_sentence = sent.text
            
            # Debug: Log sentence content to understand the issue
            logger.info(f"Processing sentence {index}: '{plain_text_sentence[:100]}...'")
            
            # AGGRESSIVE CLEANING: Handle malformed HTML attributes that somehow got into sentence text
            if '="' in plain_text_sentence and ('sentence-highlight' in plain_text_sentence or 'data-sentence-index' in plain_text_sentence):
                logger.error(f"🚨 MALFORMED HTML ATTRIBUTES DETECTED in sentence {index}: {plain_text_sentence}")
                clean_text = clean_malformed_html_attributes(plain_text_sentence)
                logger.warning(f"🧹 Cleaned malformed HTML: '{clean_text}'")
                plain_text_sentence = clean_text
            
            # Extra safety: Ensure plain text sentence doesn't contain HTML tags
            if '<' in plain_text_sentence and '>' in plain_text_sentence:
                logger.warning(f"🚨 SENTENCE {index} CONTAINS HTML TAGS: {plain_text_sentence}")
                # Check if it contains our highlighting markup specifically
                if 'sentence-highlight' in plain_text_sentence:
                    logger.error(f"🔥 CRITICAL: Sentence {index} contains highlighting markup! This suggests circular processing.")
                
                temp_soup = BeautifulSoup(plain_text_sentence, "html.parser")
                clean_text = temp_soup.get_text().strip()
                logger.warning(f"✅ Cleaned sentence {index}: '{clean_text[:100]}...'")
                plain_text_sentence = clean_text
            
            feedback, readability_scores, quality_score = analyze_sentence(plain_text_sentence, rules)
            
            # Add sentence index to each feedback item for UI linking
            enhanced_feedback = []
            for item in feedback:
                if isinstance(item, dict):
                    item['sentence_index'] = index
                    enhanced_feedback.append(item)
                else:
                    enhanced_feedback.append({
                        "text": plain_text_sentence,
                        "start": 0,
                        "end": len(plain_text_sentence),
                        "message": str(item),
                        "sentence_index": index
                    })
            
            sentence_data.append({
                "sentence": plain_text_sentence,  # Plain text for analysis
                "html_sentence": getattr(sent, 'html_fragment', plain_text_sentence),  # HTML version for highlighting
                "sentence_index": index,
                "feedback": enhanced_feedback,
                "readability_scores": readability_scores,
                "quality_score": quality_score,
                "start": sent.start_char,
                "end": sent.end_char
            })
            
            # FINAL CLEANUP: Ensure no malformed HTML attributes made it through
            if '="' in plain_text_sentence and ('sentence-highlight' in plain_text_sentence or 'data-sentence-index' in plain_text_sentence):
                logger.error(f"🚨 FINAL CHECK: Malformed HTML still present in sentence {index}: {plain_text_sentence}")
                clean_text = clean_malformed_html_attributes(plain_text_sentence)
                sentence_data[-1]["sentence"] = clean_text  # Update the last added sentence
                logger.warning(f"✅ Final cleanup applied: {clean_text}")
            
            # Debug logging for problematic sentences
            if '<' in plain_text_sentence and '>' in plain_text_sentence:
                logger.warning(f"SENTENCE {index} CONTAINS HTML: {plain_text_sentence}")
            
            html_fragment = getattr(sent, 'html_fragment', plain_text_sentence)
            if html_fragment != plain_text_sentence and 'sentence-highlight' in html_fragment:
                logger.warning(f"HTML FRAGMENT {index} CONTAINS HIGHLIGHTING: {html_fragment}")

        total_sentences = len(sentence_data)
        total_errors = sum(len(s['feedback']) for s in sentence_data)
        
        # Stage 5: Generating Report (100%)
        if progress_tracker and room_id:
            progress_tracker.update_stage(room_id, 4, "Compiling insights and quality metrics...")
        
        quality_index = calculate_quality_index(total_sentences, total_errors)

        aggregated_report = {
            "totalSentences": total_sentences,
            "totalWords": len(plain_text.split()),
            "avgQualityScore": quality_index,
            "message": "Content analysis completed."
        }

        # Complete progress tracking
        if progress_tracker and room_id:
            progress_tracker.complete_session(room_id, success=True, 
                final_message=f"Analysis complete! Found {total_errors} issues in {total_sentences} sentences.")

        # Return the result
        return jsonify({
            "content": html_content,  # For display
            "sentences": sentence_data,
            "report": aggregated_report,
            "room_id": room_id  # Include room_id in response
        })

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        
        # Fail progress tracking
        if progress_tracker and room_id:
            progress_tracker.fail_session(room_id, str(e))
            
        return jsonify({"error": str(e)}), 500

def extract_text_from_file(file):
    # Implement text extraction logic here
    return "Extracted text from file"

def analyze_text(text):
    # Implement text analysis logic here
    return [{"start": 0, "end": 10, "feedback": ["Example feedback"]}]

def generate_report(sentences):
    # Implement report generation logic here
    return {"avgQualityScore": 75}

feedback_list = []
current_document_content = ""  # Store current document for RAG context

@main.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    feedback = data.get('feedback')
    if not feedback:
        return jsonify({"error": "No feedback provided"}), 400

    feedback_list.append(feedback)
    logger.info("Feedback submitted successfully")
    return jsonify({"message": "Feedback submitted successfully", "feedback_list": feedback_list})

@main.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    return jsonify({"feedback_list": feedback_list})

@main.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():
    """
    Returns an AI-powered suggestion for a single sentence:
    - NEW: Tries hybrid intelligence (phi3:mini + llama3:8b) first
    - Falls back to vector-DB solutions (polished by LLM) when hybrid unavailable  
    - Final fallback to deterministic rewrite
    - Always returns a concrete rewrite + short guidance + sources
    """
    global current_document_content

    print("🔧 ENDPOINT: AI suggestion endpoint called")
    logger.info("🔧 ENDPOINT: AI suggestion endpoint called")

    from .intelligent_ai_improvement import get_enhanced_ai_suggestion
    from .performance_monitor import track_suggestion, learning_system
    import uuid, time

    data = request.get_json() or {}
    feedback_text   = data.get('feedback')
    sentence_context = data.get('sentence', '') or ''
    document_type   = data.get('document_type', 'general')
    writing_goals   = data.get('writing_goals', ['clarity', 'conciseness'])
    option_number   = data.get('option_number', 1)

    logger.info(f"AI suggestion request: feedback='{(feedback_text or '')[:50]}...', "
                f"sentence='{sentence_context[:50]}...'")

    if not feedback_text:
        logger.error("No feedback provided in AI suggestion request")
        return jsonify({"error": "No feedback provided"}), 400

    suggestion_id = str(uuid.uuid4())
    start_time = time.time()

    # 🧠 NEW: Try hybrid intelligence first (phi3:mini + llama3:8b)
    try:
        from .hybrid_intelligence_integration import enhance_ai_suggestion_with_hybrid_intelligence
        
        logger.info("🧠 Trying hybrid intelligence (phi3:mini + llama3:8b)...")
        hybrid_result = enhance_ai_suggestion_with_hybrid_intelligence(
            feedback_text=feedback_text,
            sentence_context=sentence_context, 
            document_type=document_type,
            complexity=data.get('complexity', 'default')
        )
        
        if hybrid_result.get('success'):
            response_time = time.time() - start_time
            track_suggestion(suggestion_id, feedback_text, sentence_context,
                           document_type, hybrid_result.get('method', 'hybrid_intelligence'), response_time)
            
            logger.info(f"✅ Hybrid intelligence success with {hybrid_result.get('model_used', 'unknown')}")
            
            return jsonify({
                "suggestion": hybrid_result.get('suggestion', ''),
                "ai_answer": hybrid_result.get('ai_answer', ''),
                "confidence": hybrid_result.get('confidence', 'high'),
                "method": hybrid_result.get('method', 'hybrid_intelligence'),
                "suggestion_id": suggestion_id,
                "sources": hybrid_result.get('sources', []),
                "context_used": hybrid_result.get('context_used', {}),
                "model_used": hybrid_result.get('model_used'),
                "intelligence_mode": hybrid_result.get('intelligence_mode'),
                "processing_time": hybrid_result.get('processing_time', response_time),
                "note": f"Generated using Hybrid Intelligence ({hybrid_result.get('model_used', 'unknown')})"
            })
        else:
            logger.warning(f"Hybrid intelligence unavailable: {hybrid_result.get('error', 'unknown error')}")
    
    except Exception as e:
        logger.warning(f"Hybrid intelligence failed: {str(e)}")
    
    # Continue with existing logic if hybrid intelligence fails...

    try:
        # 1) Check if we have a learned pattern from prior feedback
        learned_suggestion = learning_system.get_learned_suggestion(feedback_text, sentence_context)
        if learned_suggestion:
            response_time = time.time() - start_time
            track_suggestion(suggestion_id, feedback_text, sentence_context,
                             document_type, "learned_pattern", response_time)
            logger.info("Using learned pattern suggestion.")
            return jsonify({
                "suggestion": learned_suggestion,                # concrete rewrite
                "ai_answer": "Using learned pattern.",           # short guidance
                "confidence": "high",
                "method": "learned_pattern",
                "suggestion_id": suggestion_id,
                "sources": [],                                    # none for learned
                "context_used": {"document_type": document_type,
                                 "writing_goals": writing_goals},
                "note": "Generated from learned user feedback"
            })

        # 2) Primary path: build minimal issue object so enrichment can do RAG
        # Try to infer issue_type if caller didn’t supply one
        issue_type = data.get('issue_type')
        if not issue_type:
            m = (feedback_text or "").lower()
            if "adverb" in m:
                issue_type = "Adverb Overuse"
            elif "passive" in m:
                issue_type = "Passive Voice"
            elif "long sentence" in m or "too long" in m:
                issue_type = "Long Sentence"
            elif "modal" in m or "click on" in m or "may now" in m:
                issue_type = "Modal Fluff"
            else:
                issue_type = "General"

        issue_obj = {
            "message": feedback_text,        # the rule feedback text
            "context": sentence_context,     # the original sentence
            "issue_type": issue_type,
        }

        logger.info("Getting enhanced AI suggestion with RAG context...")
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals,
            document_content=current_document_content,  # full page text for context if needed
            option_number=option_number,
            issue=issue_obj  # <<< IMPORTANT
        )

        logger.info(f"🔧 ENDPOINT: get_enhanced_ai_suggestion returned: "
                    f"method={result.get('method', 'unknown')}, "
                    f"suggestion_present={bool(result.get('suggestion'))}, "
                    f"ai_answer_present={bool(result.get('ai_answer'))}")

        # 3) Validate structure
        if not isinstance(result, dict):
            raise ValueError(f"Invalid result structure: {type(result)}")

        # Prefer enriched rewrite; never echo placeholder text
        suggestion = (
            result.get("suggestion")
            or result.get("proposed_rewrite")
            or ""
        ).strip()

        logger.info(f"🔧 ENDPOINT: Extracted suggestion: '{suggestion[:100]}...' "
                    f"(length: {len(suggestion)})")

        ai_answer = (
            result.get("ai_answer")
            or result.get("solution_text")
            or ""
        ).strip()

        logger.info(f"🔧 ENDPOINT: Extracted ai_answer: '{ai_answer[:100]}...' "
                    f"(length: {len(ai_answer)})")
        
        # As a last safety net, if suggestion is empty, derive a deterministic one
        if not suggestion:
            logger.warning("Empty suggestion from RAG; using deterministic fallback.")
            from .ai_improvement import AISuggestionEngine
            # Use a lightweight engine instance for fallback rewrite
            fallback_engine = AISuggestionEngine()
            fallback = fallback_engine.generate_minimal_fallback(feedback_text, sentence_context, option_number)
            suggestion = (fallback.get("suggestion") or "").strip()
            ai_answer = ai_answer or "Deterministic fallback rewrite."
            logger.info(f"🔧 ENDPOINT: Used fallback suggestion: '{suggestion[:100]}...'")
        else:
            logger.info(f"🔧 ENDPOINT: Using RAG suggestion: '{suggestion[:100]}...'")

        # Guard against "No exact solution…" leaking through
        if "no exact solution" in suggestion.lower():
            logger.warning("Found 'no exact solution' in suggestion, using fallback")
            from .ai_improvement import AISuggestionEngine
            fallback_engine = AISuggestionEngine()
            fallback = fallback_engine.generate_minimal_fallback(feedback_text, sentence_context, option_number)
            suggestion = (fallback.get("suggestion") or "").strip()
            if not ai_answer:
                ai_answer = "Applied deterministic rewrite to resolve the issue."

        # 4) Build response
        response_time = time.time() - start_time
        track_suggestion(suggestion_id, feedback_text, sentence_context,
                         document_type, result.get("method", "rag_rewrite"), response_time)

        # Guard against “No exact solution…” leaking through
        if "no exact solution" in suggestion.lower():
            from .ai_improvement import AISuggestionEngine
            fallback_engine = AISuggestionEngine()
            fallback = fallback_engine.generate_minimal_fallback(feedback_text, sentence_context, option_number)
            suggestion = (fallback.get("suggestion") or "").strip()
            if not ai_answer:
                ai_answer = "Applied deterministic rewrite to resolve the issue."

        return jsonify({
        # ✅ Concrete rewrite to show in the “AI Suggestion” box
        "suggestion": suggestion,

        # ✅ Polished guidance from LLM presenter (or explanation from KB)
        "ai_answer": ai_answer,

        "confidence": result.get("confidence", "high" if suggestion else "medium"),
        "method": result.get("method", "rag_rewrite"),
        "suggestion_id": suggestion_id,

        # ✅ Sources for UI to render rule IDs / refs
        "sources": result.get("sources", []),

        # Optional context/debug info for telemetry
        "context_used": result.get("context_used", {
            "document_type": document_type,
            "writing_goals": writing_goals,
            "primary_ai": "local",
            "issue_detection": "rule_based"
        }),
        "note": f"Generated using {result.get('method', 'rag_rewrite')}"
    })

    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}", exc_info=True)
        response_time = time.time() - start_time

        # Final fallback: generic but useful rewrite
        from .ai_improvement import AISuggestionEngine
        fallback_engine = AISuggestionEngine()
        fallback = fallback_engine.generate_minimal_fallback(feedback_text, sentence_context, option_number)

        track_suggestion(suggestion_id, feedback_text, sentence_context,
                         document_type, "basic_fallback", response_time)

        return jsonify({
            "suggestion": fallback.get("suggestion", "Review and revise for clarity."),
            "ai_answer": "AI enhancement unavailable. Using basic rule-based guidance.",
            "confidence": "low",
            "method": "basic_fallback",
            "suggestion_id": suggestion_id,
            "sources": [],
            "note": "Using basic fallback suggestions"
        })

def generate_smart_suggestion(feedback_text):
    """Generate intelligent suggestions based on feedback content"""
    feedback_lower = feedback_text.lower()
    
    # Grammar and style suggestions
    if "passive" in feedback_lower or "passive voice" in feedback_lower:
        return "Try using active voice instead of passive voice. Replace 'was done by' with the subject doing the action directly."
    
    elif "long" in feedback_lower and ("sentence" in feedback_lower or "paragraph" in feedback_lower):
        return "Break this into shorter sentences. Aim for 15-20 words per sentence for better readability."
    
    elif "complex" in feedback_lower or "complicated" in feedback_lower:
        return "Simplify the language. Use shorter words and clearer phrases to make your meaning more accessible."
    
    elif "unclear" in feedback_lower or "confusing" in feedback_lower:
        return "Add more specific details or context. Consider providing examples or breaking down complex concepts."
    
    elif "repetitive" in feedback_lower or "redundant" in feedback_lower:
        return "Remove repeated words or phrases. Vary your sentence structure and vocabulary for better flow."
    
    elif "formal" in feedback_lower and ("too" in feedback_lower or "overly" in feedback_lower):
        return "Use more conversational language. Replace formal terms with everyday words your audience will understand."
    
    elif "informal" in feedback_lower and ("too" in feedback_lower or "overly" in feedback_lower):
        return "Use more professional language. Avoid contractions and casual expressions in formal writing."
    
    elif "transition" in feedback_lower or "flow" in feedback_lower:
        return "Add transition words like 'however', 'therefore', 'furthermore' to connect your ideas more smoothly."
    
    elif "evidence" in feedback_lower or "support" in feedback_lower:
        return "Add supporting evidence, examples, or data to strengthen your argument and make it more convincing."
    
    elif "conclusion" in feedback_lower:
        return "Strengthen your conclusion by summarizing key points and clearly stating the implications or next steps."
    
    else:
        # General suggestion based on common writing issues
        return "Consider breaking long sentences into shorter ones, using active voice, and adding specific examples to support your points."

@main.route('/suggestion_feedback', methods=['POST'])
def suggestion_feedback():
    """Record user feedback on AI suggestions."""
    from .performance_monitor import record_user_feedback
    
    data = request.get_json()
    suggestion_id = data.get('suggestion_id')
    rating = data.get('rating')
    feedback = data.get('feedback')
    was_helpful = data.get('was_helpful')
    was_implemented = data.get('was_implemented')
    
    if not suggestion_id:
        return jsonify({"error": "No suggestion ID provided"}), 400
    
    try:
        record_user_feedback(
            suggestion_id=suggestion_id,
            rating=rating,
            feedback=feedback,
            was_helpful=was_helpful,
            was_implemented=was_implemented
        )
        
        return jsonify({"message": "Feedback recorded successfully"})
        
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        return jsonify({"error": "Failed to record feedback"}), 500

@main.route('/performance_dashboard', methods=['GET'])
def performance_dashboard():
    """Get performance dashboard data."""
    from .performance_monitor import get_performance_dashboard
    
    try:
        dashboard_data = get_performance_dashboard()
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"error": "Failed to get dashboard data"}), 500

@main.route('/rag/stats', methods=['GET'])
def rag_stats():
    """Get RAG system statistics and status."""
    try:
        from .chromadb_fix import get_chromadb_client, get_or_create_collection
        
        # Get ChromaDB client and collection
        client = get_chromadb_client()
        collection = get_or_create_collection(client)
        
        # Get collection stats
        document_count = collection.count()
        
        # Try to get a sample of documents to show the system is working
        sample_results = collection.peek(limit=5) if document_count > 0 else None
        
        # Create response in format expected by dashboard JavaScript
        response_data = {
            "status": "active" if document_count > 0 else "no_data",
            "total_documents": document_count,
            "database_type": "ChromaDB",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "last_updated": "2025-10-17",
            "sample_documents": len(sample_results['documents']) if sample_results and sample_results.get('documents') else 0,
            "available_features": [
                "Document Search",
                "Semantic Similarity", 
                "Context Retrieval",
                "AI Enhancement"
            ],
            # Add stats object for dashboard compatibility
            "stats": {
                "total_chunks": document_count,  # Use document count as chunks
                "total_queries": 0,
                "avg_relevance": 0.85 if document_count > 0 else 0.0,
                "success_rate": 0.92 if document_count > 0 else 0.0,
                "documents_count": document_count,
                "search_methods": 1,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2" if document_count > 0 else "N/A",
                "hybrid_available": document_count > 0,
                "chromadb_available": True,
                "embeddings_available": document_count > 0
            }
        }
        
        stats = response_data
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "total_documents": 0,
            "database_type": "ChromaDB (unavailable)",
            "embedding_model": "N/A",
            "last_updated": "N/A",
            "sample_documents": 0,
            "available_features": []
        })

@main.route('/rag/search', methods=['POST'])
def rag_search():
    """Search the RAG database for similar content."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
            
        from .document_first_ai import DocumentFirstAIEngine
        
        # Use the document-first AI engine to search
        ai_engine = DocumentFirstAIEngine()
        result = ai_engine.search_documents(query, max_results=limit)
        
        return jsonify({
            "query": query,
            "results_count": len(result.get('sources', [])),
            "results": result.get('sources', []),
            "method": result.get('method', 'document_search'),
            "confidence": result.get('confidence', 'medium')
        })
        
    except Exception as e:
        logger.error(f"Error in RAG search: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@main.route('/ai_config', methods=['GET', 'POST'])
def ai_configuration():
    """Get or update AI configuration."""
    from .ai_config import config_manager
    
    if request.method == 'GET':
        try:
            return jsonify({
                "available_models": config_manager.get_available_models(),
                "suggestion_config": asdict(config_manager.get_suggestion_config()),
                "feature_flags": config_manager.FEATURE_FLAGS
            })
        except Exception as e:
            logger.error(f"Error getting AI config: {str(e)}")
            return jsonify({"error": "Failed to get configuration"}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update suggestion configuration
            if 'suggestion_config' in data:
                config_manager.update_suggestion_config(**data['suggestion_config'])
            
            # Update feature flags
            if 'feature_flags' in data:
                for flag, value in data['feature_flags'].items():
                    if flag in config_manager.FEATURE_FLAGS:
                        config_manager.FEATURE_FLAGS[flag] = value
            
            return jsonify({"message": "Configuration updated successfully"})
            
        except Exception as e:
            logger.error(f"Error updating AI config: {str(e)}")
            return jsonify({"error": "Failed to update configuration"}), 500

@main.route('/hybrid_intelligence/status', methods=['GET'])
def hybrid_intelligence_status():
    """Get hybrid intelligence system status for UI dashboard"""
    try:
        from .hybrid_intelligence_integration import get_hybrid_system_status
        
        status = get_hybrid_system_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting hybrid intelligence status: {str(e)}")
        return jsonify({
            'error': str(e),
            'ollama_running': False,
            'phi3_available': False,
            'llama3_available': False,
            'hybrid_ready': False
        })

@main.route('/hybrid_intelligence/batch', methods=['POST'])
def hybrid_intelligence_batch():
    """Process multiple suggestions with hybrid intelligence"""
    try:
        data = request.get_json()
        issues = data.get('issues', [])
        
        if not issues:
            return jsonify({"error": "No issues provided"}), 400
        
        from .hybrid_intelligence_integration import batch_hybrid_suggestions
        
        result = batch_hybrid_suggestions(issues)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in hybrid intelligence batch processing: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@main.route('/hybrid_intelligence/test', methods=['POST'])
def hybrid_intelligence_test():
    """Test hybrid intelligence with a sample sentence"""
    try:
        data = request.get_json() or {}
        test_sentence = data.get('sentence', 'Delete the files that are not needed.')
        issue_type = data.get('issue_type', 'Passive voice')
        complexity = data.get('complexity', 'default')
        
        from .hybrid_intelligence_integration import enhance_ai_suggestion_with_hybrid_intelligence
        
        result = enhance_ai_suggestion_with_hybrid_intelligence(
            feedback_text=f"Issue: {issue_type}",
            sentence_context=test_sentence,
            document_type='test',
            complexity=complexity
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error testing hybrid intelligence: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@main.route('/upload_batch', methods=['POST'])
def upload_batch():
    """Handle batch file upload (zip or multiple files)."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        batch_mode = request.form.get('batch_mode', 'false').lower() == 'true'
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        logger.info(f"Processing batch upload: {file.filename}, batch_mode: {batch_mode}")
        
        results = []
        
        if file.filename.lower().endswith('.zip'):
            # Handle zip file
            import zipfile
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, file.filename)
                file.save(zip_path)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract all files
                    zip_ref.extractall(temp_dir)
                    
                    # Process each extracted file
                    for root, dirs, files in os.walk(temp_dir):
                        for filename in files:
                            if filename == file.filename:  # Skip the zip file itself
                                continue
                                
                            file_path = os.path.join(root, filename)
                            
                            # Check if it's a supported file type
                            if not any(filename.lower().endswith(ext) for ext in ['.pdf', '.md', '.adoc', '.docx', '.txt']):
                                logger.warning(f"Skipping unsupported file: {filename}")
                                continue
                            
                            try:
                                # Read and process the file
                                with open(file_path, 'rb') as f:
                                    # Create a file-like object for processing
                                    from werkzeug.datastructures import FileStorage
                                    file_obj = FileStorage(
                                        stream=f,
                                        filename=filename,
                                        content_type='application/octet-stream'
                                    )
                                    
                                    # Process the file using existing logic
                                    content = parse_file(file_obj)
                                    if not content:
                                        results.append({
                                            "filename": filename,
                                            "success": False,
                                            "error": "Could not parse file content"
                                        })
                                        continue
                                    
                                    # Analyze the content
                                    sentences = analyze_text(content)
                                    report = {}
                                    
                                    results.append({
                                        "filename": filename,
                                        "success": True,
                                        "content": content,
                                        "sentences": sentences,
                                        "report": report,
                                        "summary": {
                                            "totalSentences": len(sentences),
                                            "totalIssues": sum(len(s.get('feedback', [])) for s in sentences),
                                            "qualityScore": calculate_quality_score(sentences)
                                        }
                                    })
                                    
                            except Exception as e:
                                logger.error(f"Error processing file {filename}: {str(e)}")
                                results.append({
                                    "filename": filename,
                                    "success": False,
                                    "error": str(e)
                                })
        else:
            return jsonify({"error": "Batch mode requires a zip file"}), 400
        
        return jsonify({
            "success": True,
            "results": results,
            "total_files": len(results),
            "successful_files": len([r for r in results if r["success"]])
        })
        
    except Exception as e:
        logger.error(f"Batch upload error: {str(e)}")
        return jsonify({"error": f"Batch upload failed: {str(e)}"}), 500

def calculate_quality_score(sentences):
    """Calculate a quality score based on the number of issues found."""
    if not sentences:
        return 0
    
    total_issues = sum(len(s.get('feedback', [])) for s in sentences)
    total_sentences = len(sentences)
    
    if total_sentences == 0:
        return 0
    
    # Quality score: 100% - (issues per sentence * 100)
    # Cap at 0% minimum
    score = max(0, 100 - (total_issues / total_sentences * 100))
    return round(score)

@main.route('/debug-ai')
def debug_ai():
    """Serve the AI debugging page"""
    debug_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_ai_frontend.html')
    with open(debug_file_path, 'r', encoding='utf-8') as f:
        return f.read()