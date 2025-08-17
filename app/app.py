from flask import Blueprint, request, jsonify, render_template, Response
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
import json
import uuid
from dataclasses import asdict

# Import smart rule filtering for performance - temporarily disabled for debugging
# from .smart_rule_filter import analyze_sentence_smart, get_smart_performance_stats

# Import Enhanced RAG System for intelligent suggestions
try:
    from .enhanced_rag_complete import get_enhanced_suggestion, get_rag_status
    RAG_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Enhanced RAG system imported successfully")
except ImportError as e:
    RAG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhanced RAG system not available: {e}")

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

# Load spaCy English model lazily when needed
nlp = None
SPACY_AVAILABLE = None

def get_spacy_model():
    """Lazy loading of spaCy model - only load when actually needed."""
    global nlp, SPACY_AVAILABLE
    
    if SPACY_AVAILABLE is None:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            SPACY_AVAILABLE = True
            logger.info("spaCy model loaded successfully (lazy loading)")
        except Exception as e:
            logger.warning(f"spaCy model not available: {e}")
            nlp = None
            SPACY_AVAILABLE = False
    
    return nlp if SPACY_AVAILABLE else None

def enhance_issue_with_rag(issue: dict, context: str = "", timeout_seconds: int = 2) -> dict:
    """Enhance an issue with the RAG system for intelligent suggestions."""
    if not RAG_AVAILABLE:
        return {
            "enhanced_response": issue.get('message', ''),
            "method": "original"
        }
    
    try:
        # For performance: skip RAG enhancement for basic pattern-based issues
        issue_message = issue.get('message', '')
        message_lower = issue_message.lower()
        
        # Skip RAG for simple, repetitive issues to improve performance
        if any(skip_pattern in message_lower for skip_pattern in [
            'consider rewriting as:', 'consider removing unnecessary modifier',
            'remove \'very\' or use a stronger word'
        ]):
            return {
                "enhanced_response": issue.get('message', ''),
                "method": "skip_repetitive"
            }
        
        # Extract issue details
        issue_text = issue.get('text', '')
        
        # Determine issue type from message
        issue_type = "general"
        if "passive voice" in message_lower:
            issue_type = "passive_voice"
        elif "long sentence" in message_lower or "sentence length" in message_lower:
            issue_type = "long_sentence"
        elif "modifier" in message_lower or "unnecessary" in message_lower:
            issue_type = "modifier"
        elif "clarity" in message_lower:
            issue_type = "clarity"
        elif "grammar" in message_lower:
            issue_type = "grammar"
        
        # Quick timeout for RAG enhancement to prevent blocking (cross-platform)
        import threading
        import time
        
        result_container = {}
        
        def rag_worker():
            try:
                result_container['result'] = get_enhanced_suggestion(
                    issue_text=issue_text,
                    issue_type=issue_type,
                    context=context[:300]  # Reduced context for faster processing
                )
            except Exception as e:
                result_container['error'] = str(e)
        
        # Start RAG enhancement in thread with timeout
        thread = threading.Thread(target=rag_worker)
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        if thread.is_alive():
            # Timeout occurred
            logger.warning("RAG enhancement timed out")
            return {
                "enhanced_response": issue.get('message', ''),
                "method": "timeout_fallback"
            }
        
        if 'result' in result_container:
            return result_container['result']
        elif 'error' in result_container:
            raise Exception(result_container['error'])
        
    except (TimeoutError, Exception) as e:
        logger.warning(f"RAG enhancement failed or timed out: {e}")
        return {
            "enhanced_response": issue.get('message', ''),
            "method": "original_with_error",
            "error": str(e)
        }

############################
# PARSING HELPERS
############################

def parse_file_content(file_content, filename):
    """Parse file content from bytes, avoiding file stream issues"""
    filename_lower = filename.lower()
    extension = os.path.splitext(filename_lower)[1]

    try:
        if extension == '.docx':
            # For DOCX, we need to create a BytesIO object
            from io import BytesIO
            file_stream = BytesIO(file_content)
            return parse_docx(file_stream)
        elif extension == '.doc':
            # For DOC, we need to save temporarily
            from io import BytesIO
            file_stream = BytesIO(file_content)
            return parse_doc_from_content(file_content, filename)
        elif extension == '.pdf':
            # For PDF, we need to create a BytesIO object
            from io import BytesIO
            file_stream = BytesIO(file_content)
            return parse_pdf(file_stream)
        elif extension == '.md':
            # Decode content and parse
            if isinstance(file_content, bytes):
                content = file_content.decode('utf-8', errors='replace')
            else:
                content = file_content
            return parse_md(content)
        elif extension == '.adoc':
            # Decode content and parse
            if isinstance(file_content, bytes):
                content = file_content.decode('utf-8', errors='replace')
            else:
                content = file_content
            return parse_adoc(content)
        elif extension in ['.txt', '']:
            # Decode content and parse
            if isinstance(file_content, bytes):
                content = file_content.decode('utf-8', errors='replace')
            else:
                content = file_content
            return parse_txt(content)
        else:
            if isinstance(file_content, bytes):
                content = file_content.decode('utf-8', errors='replace')
            else:
                content = file_content
            return content
    except Exception as e:
        logger.error(f"Error parsing {filename}: {str(e)}")
        return f"Error parsing {filename}: {str(e)}"

def parse_file(file):
    filename = file.filename.lower()
    extension = os.path.splitext(filename)[1]

    try:
        # Ensure file pointer is at the beginning
        file.seek(0)
        
        if extension == '.docx':
            return parse_docx(file)
        elif extension == '.doc':
            return parse_doc(file)
        elif extension == '.pdf':
            return parse_pdf(file)
        elif extension == '.md':
            # Read the content and decode it properly
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return parse_md(content)
        elif extension == '.adoc':
            # Read the content and decode it properly
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return parse_adoc(content)
        elif extension in ['.txt', '']:
            # Read the content and decode it properly
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return parse_txt(content)
        else:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return content
    except Exception as e:
        logger.error(f"Error parsing {filename}: {str(e)}")
        return f"Error parsing {filename}: {str(e)}"

def parse_docx(file_stream):
    try:
        # Ensure file pointer is at the beginning
        file_stream.seek(0)
        doc = Document(file_stream)
        html_content = ""
        for paragraph in doc.paragraphs:
            html_content += f"<p>{paragraph.text}</p>"
        return html_content
    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        return f"Error parsing DOCX: {str(e)}"

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

def parse_doc_from_content(file_content, filename):
    """Parse DOC file from content bytes"""
    temp_path = f"temp_upload_{uuid.uuid4().hex}.doc"
    try:
        # Write content to temporary file
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(file_content)
        
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
        # Ensure file pointer is at the beginning
        file_stream.seek(0)
        reader = PyPDF2.PdfReader(file_stream)
        html_content = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            for paragraph in page_text.split("\n\n"):
                html_content += f"<p>{paragraph}</p>"
        return html_content
    except Exception as e:
        logger.error(f"Error reading PDF: {str(e)}")
        return f"Error reading PDF: {str(e)}"

def parse_md(content):
    # Handle both bytes and string input
    if isinstance(content, bytes):
        md_text = content.decode("utf-8", errors="replace")
    else:
        md_text = content
    html_text = markdown.markdown(md_text)
    return html_text

def parse_adoc(content):
    # Handle both bytes and string input
    if isinstance(content, bytes):
        adoc_text = content.decode("utf-8", errors="replace")
    else:
        adoc_text = content
    html_content = ""
    for paragraph in adoc_text.split("\n\n"):
        html_content += f"<p>{paragraph}</p>"
    return html_content

def parse_txt(content):
    # Handle both bytes and string input
    if isinstance(content, bytes):
        txt_text = content.decode("utf-8", errors="replace")
    else:
        txt_text = content
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

# Lazy loading of rules
_rules_cache = None

def get_rules():
    """Lazy loading of rules - only load when actually needed."""
    global _rules_cache
    if _rules_cache is None:
        logger.info("🔧 Loading rules (lazy loading)")
        _rules_cache = load_rules()
        logger.info(f"✅ Rules loaded successfully: {len(_rules_cache)} rules available")
    else:
        logger.info(f"♻️ Using cached rules: {len(_rules_cache)} rules available")
    return _rules_cache

def review_document(content, rules):
    suggestions = []
    for rule in rules:
        feedback = rule(content)
        if feedback:
            for item in feedback:
                # Handle both string and dict formats
                if isinstance(item, str):
                    # Convert string feedback to dict format
                    suggestions.append({
                        "text": "",  # String suggestions often don't specify exact text
                        "start": 0,
                        "end": 0,
                        "message": item
                    })
                elif isinstance(item, dict):
                    suggestions.append({
                        "text": item.get("text", ""),
                        "start": item.get("start", 0),
                        "end": item.get("end", 0),
                        "message": item.get("message", item.get("suggestion", ""))
                    })
    return {"issues": suggestions, "summary": "Review completed."}

def analyze_sentence(sentence, rules):
    """
    Direct sentence analysis - bypassing smart filter for debugging.
    """
    logger.info(f"🔍 Analyzing sentence with {len(rules)} rules: '{sentence[:50]}...'")
    
    feedback = []
    readability_scores = {}
    
    # Direct rule execution
    for i, rule_function in enumerate(rules):
        try:
            rule_name = getattr(rule_function, '__name__', f'rule_{i}')
            if hasattr(rule_function, '__module__'):
                module_name = rule_function.__module__
                if 'rules.' in module_name:
                    rule_name = module_name.split('rules.')[-1]
            
            logger.info(f"� Executing rule: {rule_name}")
            rule_result = rule_function(sentence)
            
            if rule_result:
                logger.info(f"✅ Rule '{rule_name}' found {len(rule_result)} issues")
                # Handle both list and single item results
                if isinstance(rule_result, list):
                    feedback.extend(rule_result)
                else:
                    feedback.append(rule_result)
            else:
                logger.info(f"➖ Rule '{rule_name}' found no issues")
                
        except Exception as rule_error:
            logger.warning(f"⚠️ Rule '{rule_name}' failed: {rule_error}")
            continue
    
    # Calculate quality score
    quality_score = max(0, 100 - (len(feedback) * 10))
    
    logger.info(f"🎯 Direct analysis complete: {len(feedback)} total issues found, quality: {quality_score}")
    
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
    # Add cache-busting headers
    from flask import make_response
    import time
    
    response = make_response(render_template('index.html', cache_bust=int(time.time())))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main.route('/fresh')
def fresh_interface():
    """Completely fresh interface with new progress display - no caching"""
    # Create a fresh template with cache-busting
    fresh_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>🚀 Fresh Progress Display v2.0 - Doc Scanner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); color: white; min-height: 100vh; }
        .container { padding: 2rem; }
        .banner { background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; text-align: center; padding: 1rem; margin-bottom: 2rem; border-radius: 10px; font-weight: bold; font-size: 1.2rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
        .upload-area { border: 2px dashed #FFD700; border-radius: 10px; padding: 2rem; text-align: center; margin: 2rem 0; background: rgba(255, 255, 255, 0.1); }
        .btn-primary { background: linear-gradient(45deg, #007bff, #0056b3); border: none; padding: 0.8rem 2rem; border-radius: 25px; }
        .btn-success { background: linear-gradient(45deg, #28a745, #20c997); border: none; padding: 0.8rem 2rem; border-radius: 25px; }
        #newProgressOverlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(18,28,58,0.95); z-index: 99999; display: none; align-items: center; justify-content: center; }
        .progress-container { text-align: center; color: #FFD700; background: rgba(0, 0, 0, 0.8); padding: 2rem; border-radius: 15px; min-width: 400px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); }
        .progress-title { font-size: 1.5rem; margin-bottom: 1rem; color: #FFD700; }
        .progress-percentage { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; color: #FFD700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
        .progress-bar { background: rgba(255, 255, 255, 0.1); border-radius: 10px; height: 20px; margin: 1rem 0; overflow: hidden; position: relative; }
        .progress-fill { background: linear-gradient(45deg, #FFD700, #FFA500); height: 100%; width: 0%; border-radius: 10px; transition: width 0.3s ease; }
        .progress-message { font-size: 1rem; color: #ffffff; margin-top: 1rem; min-height: 1.5rem; }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spinner { animation: rotate 2s linear infinite; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">🚀 FRESH PROGRESS DISPLAY v2.0 LOADED! 🚀 NO CACHE! 🚀</div>
        <div class="row justify-content-center">
            <div class="col-md-8">
                <h1 class="text-center mb-4"><i class="fas fa-file-text"></i> Document Scanner - Fresh Interface</h1>
                <div class="upload-area">
                    <i class="fas fa-cloud-upload-alt fa-3x mb-3" style="color: #FFD700;"></i>
                    <h3>Upload Your Document</h3>
                    <p>Select a file to see the NEW progress display in action</p>
                    <input type="file" id="fileInput" class="form-control mb-3" accept=".txt,.docx,.pdf">
                    <button id="uploadBtn" class="btn btn-primary"><i class="fas fa-upload"></i> Upload & Analyze</button>
                </div>
                <div class="text-center">
                    <button id="testBtn" class="btn btn-success me-2">🚀 Test Fresh Progress Display 🚀</button>
                    <button id="debugBtn" class="btn btn-warning">🔍 Debug Info</button>
                </div>
                <div id="results" class="mt-4"></div>
            </div>
        </div>
    </div>
    <div id="newProgressOverlay">
        <div class="progress-container">
            <div class="progress-title"><i class="fas fa-brain spinner"></i> Fresh Progress Display v2.0</div>
            <div class="progress-percentage" id="progressPercent">0%</div>
            <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
            <div class="progress-message" id="progressMsg">Initializing fresh system...</div>
            <div style="margin-top: 1rem; font-size: 0.8rem; color: #4ecdc4;">✅ Fresh Interface - No Cache Issues ✅</div>
        </div>
    </div>
    <script>
        console.log('🚀 Fresh interface loaded!');
        function showProgress() { console.log('Showing fresh progress overlay'); document.getElementById('newProgressOverlay').style.display = 'flex'; }
        function updateProgress(percent, message) { console.log(`Fresh progress: ${percent}% - ${message}`); document.getElementById('progressPercent').textContent = percent + '%'; document.getElementById('progressFill').style.width = percent + '%'; document.getElementById('progressMsg').textContent = message; }
        function hideProgress() { console.log('Hiding fresh progress overlay'); document.getElementById('newProgressOverlay').style.display = 'none'; }
        document.getElementById('testBtn').addEventListener('click', function() {
            console.log('Testing fresh progress display...');
            showProgress();
            const stages = [
                { percent: 10, message: '🚀 Fresh system starting...' },
                { percent: 30, message: 'Loading components...' },
                { percent: 60, message: 'Processing data...' },
                { percent: 85, message: 'Finalizing results...' },
                { percent: 100, message: '✅ Fresh test complete!' }
            ];
            let i = 0;
            function runTest() {
                if (i < stages.length) {
                    updateProgress(stages[i].percent, stages[i].message);
                    i++;
                    setTimeout(runTest, 1500);
                } else {
                    setTimeout(() => { hideProgress(); alert('🚀 Fresh Progress Test Complete!'); }, 2000);
                }
            }
            runTest();
        });
        document.getElementById('debugBtn').addEventListener('click', function() {
            const info = `Fresh Interface Debug Info: URL: ${window.location.href} Timestamp: ${new Date().toISOString()} Cache Headers: Set to no-cache Progress Overlay ID: newProgressOverlay Elements Found: ${document.getElementById('newProgressOverlay') ? 'YES' : 'NO'} Console: Check for fresh interface logs`;
            alert(info);
            console.log('Fresh interface debug info:', info);
        });
        document.getElementById('uploadBtn').addEventListener('click', function() {
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files[0]) { alert('Please select a file first'); return; }
            showProgress();
            updateProgress(0, 'Starting fresh upload...');
            let progress = 0;
            const uploadInterval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress > 100) progress = 100;
                updateProgress(Math.round(progress), `Uploading: ${Math.round(progress)}%`);
                if (progress >= 100) {
                    clearInterval(uploadInterval);
                    setTimeout(() => {
                        hideProgress();
                        document.getElementById('results').innerHTML = `<div class="alert alert-success"><h4>✅ Fresh Upload Complete!</h4><p>File: ${fileInput.files[0].name}</p><p>Progress display working perfectly!</p></div>`;
                    }, 1000);
                }
            }, 500);
        });
    </script>
</body>
</html>"""
    return fresh_html

def extract_formatted_sentence_html(block_soup, plain_sentence, original_html_block):
    """
    Extract the HTML segment that corresponds to a specific sentence.
    This preserves formatting like bold, links, and images within the sentence.
    """
    try:
        # Get the text content of the entire block
        full_text = block_soup.get_text(separator=" ").strip()
        
        # If this block contains only one sentence (or is very short), return the full formatted block
        import re
        
        # Count probable sentence boundaries (. ! ? followed by space and capital letter)
        sentence_boundaries = list(re.finditer(r'[.!?]+\s+(?=[A-Z])', full_text))
        
        # If there are no clear sentence boundaries, or the text is short, return the full block
        if len(sentence_boundaries) == 0 or len(full_text) < 150:
            # Single sentence or short content - return with original formatting
            return original_html_block
        
        # For multi-sentence blocks, we have a choice:
        # 1. Return the full block (will have highlighting issues with multiple sentences)
        # 2. Return plain text (loses formatting)
        # 3. Try to smartly extract the HTML for just this sentence (complex)
        
        # Let's use a smart approach: if the sentence appears to be a complete standalone
        # sentence that starts or ends the paragraph, try to preserve formatting
        
        # Check if our sentence is at the start of the full text
        if full_text.startswith(plain_sentence.rstrip('.!?')):
            # This sentence is at the beginning - we can try to extract its HTML
            # For now, return the original block but flag it for better handling
            return original_html_block
            
        # Check if our sentence is at the end of the full text  
        if full_text.rstrip('.!?').endswith(plain_sentence.rstrip('.!?')):
            # This sentence is at the end - we can try to extract its HTML
            return original_html_block
            
        # For sentences in the middle of multi-sentence paragraphs,
        # we'll use plain text for now to avoid highlighting confusion
        # TODO: Implement precise HTML extraction for middle sentences
        return f"<p>{plain_sentence}</p>"
            
    except Exception as e:
        logger.warning(f"Error extracting sentence HTML: {e}")
        return f"<p>{plain_sentence}</p>"

@main.route('/upload', methods=['POST'])
def upload_file():
    global current_document_content  # Access global variable
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    logger.info(f"File uploaded: {file.filename}")

    try:
        # Parse file to get both plain text and HTML
        html_content = parse_file(file)
        # Use BeautifulSoup to extract plain text from HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # ENHANCED FIX: Advanced text extraction to preserve sentence integrity
        # Remove script and style elements that might interfere
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Use space as separator to prevent breaking sentences with formatting
        plain_text = soup.get_text(separator=" ")
        
        # Enhanced text cleaning and normalization
        import re
        # Replace multiple spaces/tabs/newlines with single space
        plain_text = re.sub(r'\s+', ' ', plain_text)
        # Clean up spacing around punctuation
        plain_text = re.sub(r'\s+([.!?,:;])', r'\1', plain_text)
        # Ensure proper spacing after punctuation
        plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
        # Remove extra spaces around parentheses and brackets
        plain_text = re.sub(r'\s*([()[\]{}])\s*', r'\1', plain_text)
        # Clean up spaces around hyphens and dashes
        plain_text = re.sub(r'\s+(-+)\s+', r' \1 ', plain_text)
        plain_text = plain_text.strip()
        
        # Store the document content for RAG context
        current_document_content = plain_text

        # Process paragraph blocks for sentence segmentation
        paragraph_blocks = []
        
        # Process different HTML elements that represent text blocks
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'li', 'blockquote'])
        
        for element in text_elements:
            # Skip elements that are inside other elements we're already processing
            if element.parent and element.parent.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                continue
                
            # Extract text properly to maintain sentence boundaries
            # Use get_text on the entire element to preserve sentence structure
            block_text = element.get_text(separator=" ").strip()
            
            # Clean and normalize the block text
            if block_text.strip():
                block_text = re.sub(r'\s+', ' ', block_text.strip())
                # Only add if it's substantial content (not just punctuation)
                if len(block_text.strip()) > 2 and not re.match(r'^[.!?,:;\s]*$', block_text):
                    paragraph_blocks.append({
                        'plain': block_text,
                        'html': str(element)  # Store both plain and HTML
                    })

        # ENHANCED: Process paragraph blocks for sentence segmentation with HTML preservation
        sentences = []
        
        # Process each paragraph block
        for block_data in paragraph_blocks:
            plain_block = block_data['plain']
            html_block = block_data['html']
            
            spacy_nlp = get_spacy_model()
            if spacy_nlp:
                # Use spaCy to split plain text into sentences
                doc = spacy_nlp(plain_block)
                
                # Get all sentences from this block
                sentence_list = list(doc.sents)
                
                for sent in sentence_list:
                    plain_sentence = re.sub(r'\s+', ' ', sent.text.strip())
                    
                    # ENHANCED: Skip very short fragments, pure punctuation, or whitespace
                    if (len(plain_sentence) > 8 and 
                        not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                        len(plain_sentence.split()) >= 2):
                        
                        # ENHANCED: Extract the specific HTML for this sentence with formatting preserved
                        from bs4 import BeautifulSoup
                        block_soup = BeautifulSoup(html_block, 'html.parser')
                        html_sentence = extract_formatted_sentence_html(block_soup, plain_sentence, html_block)
                        
                        # Log sentence processing for debugging
                        if len(sentence_list) > 1:
                            logger.debug(f"Processing sentence {len(sentences)+1} from multi-sentence paragraph: {plain_sentence[:50]}...")
                        
                        # Create enhanced sentence object with both plain and HTML versions
                        class EnhancedSentence:
                            def __init__(self, plain_text, html_text):
                                self.text = plain_text  # For spaCy compatibility and analysis
                                self.html_text = html_text  # For display with formatting
                                self.start_char = 0  # Will be updated in position mapping
                                self.end_char = len(plain_text)
                        
                        sentences.append(EnhancedSentence(plain_sentence, html_sentence))
                        
            else:
                # Enhanced fallback: regex splitting when spaCy is not available
                import re
                simple_sentences = re.split(r'[.!?]+\s+(?=[A-Z0-9])', plain_block)
                
                for sent_text in simple_sentences:
                    cleaned_sent = sent_text.strip()
                    # ENHANCED: Match the stricter filtering from spaCy path
                    if (cleaned_sent and 
                        len(cleaned_sent) > 8 and 
                        not re.match(r'^[.!?,:;\s\-_]*$', cleaned_sent) and
                        len(cleaned_sent.split()) >= 2):
                        
                        # ENHANCED: Extract the specific HTML for this sentence with formatting preserved
                        from bs4 import BeautifulSoup
                        block_soup = BeautifulSoup(html_block, 'html.parser')
                        html_sent = extract_formatted_sentence_html(block_soup, cleaned_sent, html_block)
                        
                        class SimpleSentence:
                            def __init__(self, plain_text, html_text):
                                self.text = plain_text
                                self.html_text = html_text
                                self.start_char = 0
                                self.end_char = len(plain_text)
                        
                        sentences.append(SimpleSentence(cleaned_sent, html_sent))

        sentence_data = []
        
        # NEW APPROACH: Analyze each sentence individually with the new rules format
        logger.info(f"🔍 Analyzing {len(sentences)} sentences individually with {len(get_rules())} rules")
        rules = get_rules()
        
        for index, sentence in enumerate(sentences):
            sentence_feedback = []
            sentence_text = sentence.text
            
            # Apply each rule to this sentence
            for rule in rules:
                try:
                    rule_result = rule(sentence_text)
                    if rule_result:
                        # Handle both list and single item results
                        if isinstance(rule_result, list):
                            for issue in rule_result:
                                if isinstance(issue, str):
                                    sentence_feedback.append({
                                        "text": "",
                                        "start": 0,
                                        "end": len(sentence_text),
                                        "message": issue,
                                        "sentence_index": index
                                    })
                                elif isinstance(issue, dict):
                                    sentence_feedback.append({
                                        "text": issue.get("text", ""),
                                        "start": issue.get("start", 0),
                                        "end": issue.get("end", len(sentence_text)),
                                        "message": issue.get("message", issue.get("suggestion", "")),
                                        "sentence_index": index
                                    })
                        else:
                            if isinstance(rule_result, str):
                                sentence_feedback.append({
                                    "text": "",
                                    "start": 0,
                                    "end": len(sentence_text),
                                    "message": rule_result,
                                    "sentence_index": index
                                })
                except Exception as e:
                    logger.warning(f"⚠️ Rule failed for sentence {index}: {e}")
                    continue
            
            # Add sentence data with feedback - ENHANCED: Use original HTML blocks
            sentence_data.append({
                "content": sentence.html_text,
                "plain": sentence_text,
                "sentence": sentence_text,  # ADDED: Frontend expects this property
                "html_segment": sentence.html_text,  # ADDED: Frontend expects this property
                "feedback": sentence_feedback,
                "index": index,
                # NEW: Add additional properties to help with highlighting
                "is_formatted": '<' in sentence.html_text and '>' in sentence.html_text,
                "html_content": sentence.html_text  # Full HTML block for better highlighting
            })
        
        total_issues = sum(len(s['feedback']) for s in sentence_data)
        logger.info(f"✅ Sentence-by-sentence analysis completed: {total_issues} total issues found")
        
        # Calculate summary statistics
        total_sentences = len(sentence_data)
        total_errors = sum(len(s['feedback']) for s in sentence_data)
        quality_index = calculate_quality_index(total_sentences, total_errors)

        aggregated_report = {
            "totalSentences": total_sentences,
            "totalWords": len(plain_text.split()),
            "avgQualityScore": quality_index,
            "message": "Content analysis completed."
}

        # Return the result
        return jsonify({
            "content": html_content,  # For display
            "sentences": sentence_data,
            "report": aggregated_report
        })

    except Exception as e:
        logger.error(f"Error processing file: {e}")
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

# Global progress tracking
analysis_progress = {}

@main.route('/test_route', methods=['GET'])
def test_route():
    """Simple test route to verify route registration"""
    return jsonify({"message": "Test route working", "status": "success"})

@main.route('/upload_progressive', methods=['POST'])
def upload_file_progressive():
    """Progressive file upload with real-time progress updates"""
    import threading
    global current_document_content
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    logger.info(f"🚀 Starting progressive analysis for {file.filename} with ID: {analysis_id}")
    
    # Read file content immediately while we're in the request context
    try:
        file.seek(0)  # Ensure we're at the beginning
        file_content = file.read()
        filename = file.filename
        logger.info(f"📁 File content read: {len(file_content)} bytes for {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to read file content: {e}")
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 400
    
    # Store initial progress
    analysis_progress[analysis_id] = {
        "stage": "parsing",
        "percentage": 0,
        "message": "Initializing analysis...",
        "completed": False,
        "error": None,
        "result": None
    }
    logger.info(f"📊 Initial progress stored: {analysis_progress[analysis_id]}")
    
    def run_analysis():
        """Run the analysis in a background thread"""
        try:
            # Immediate feedback - show we're starting
            analysis_progress[analysis_id].update({
                "stage": "parsing",
                "percentage": 1,
                "message": "Starting file analysis..."
            })
            logger.info(f"🎬 Analysis thread started for: {analysis_id}")
            time.sleep(0.5)  # Small delay to show initial state
            
            # Stage 1: File parsing (5%)
            analysis_progress[analysis_id].update({
                "stage": "parsing",
                "percentage": 5,
                "message": f"Parsing {filename}..."
            })
            logger.info(f"🔍 Stage 1 - Parsing started: {analysis_progress[analysis_id]}")
            
            # Add longer delay to show parsing stage
            time.sleep(2.0)
            
            # Parse the file content instead of the file object
            html_content = parse_file_content(file_content, filename)
            current_document_content = html_content  # Store original HTML for context
            logger.info(f"✅ File parsed successfully, {len(html_content)} characters")
            
            # Stage 2: Sentence segmentation (15%) - FIXED: Use proper HTML-aware processing
            analysis_progress[analysis_id].update({
                "stage": "segmentation", 
                "percentage": 15,
                "message": "Breaking down into sentences with HTML preservation..."
            })
            logger.info(f"✂️ Stage 2 - Segmentation started: {analysis_progress[analysis_id]}")
            
            # Add longer delay to show segmentation stage
            time.sleep(1.5)
            
            # FIXED: Use the same working sentence processing as upload_file function
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Process paragraph blocks for sentence segmentation
            paragraph_blocks = []
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'li', 'blockquote'])
            
            for element in text_elements:
                # Skip nested elements
                if element.parent and element.parent.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    continue
                    
                block_text = element.get_text(separator=" ").strip()
                if block_text.strip() and len(block_text.strip()) > 2:
                    import re
                    block_text = re.sub(r'\s+', ' ', block_text.strip())
                    if not re.match(r'^[.!?,:;\s]*$', block_text):
                        paragraph_blocks.append({
                            'plain': block_text,
                            'html': str(element)
                        })
            
            # Process each paragraph block for sentences
            sentences = []
            for block_data in paragraph_blocks:
                plain_block = block_data['plain']
                html_block = block_data['html']
                
                spacy_nlp = get_spacy_model()
                if spacy_nlp:
                    doc = spacy_nlp(plain_block)
                    sentence_list = list(doc.sents)
                    
                    for sent in sentence_list:
                        import re
                        plain_sentence = re.sub(r'\s+', ' ', sent.text.strip())
                        
                        if (len(plain_sentence) > 8 and 
                            not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                            len(plain_sentence.split()) >= 2):
                            
                            from bs4 import BeautifulSoup
                            block_soup = BeautifulSoup(html_block, 'html.parser')
                            html_sentence = extract_formatted_sentence_html(block_soup, plain_sentence, html_block)
                            
                            sentences.append({
                                'sentence': plain_sentence,
                                'html_segment': html_sentence,
                                'plain': plain_sentence
                            })
                else:
                    # Fallback without spaCy
                    import re
                    simple_sentences = re.split(r'[.!?]+\s+', plain_block)
                    for sent_text in simple_sentences:
                        if sent_text.strip() and len(sent_text.strip()) > 8:
                            sentences.append({
                                'sentence': sent_text.strip(),
                                'html_segment': f'<p>{sent_text.strip()}</p>',
                                'plain': sent_text.strip()
                            })
            
            logger.info(f"📝 Extracted {len(sentences)} sentences using HTML-aware processing")
            
            total_sentences = len(sentences)
            sentence_data = []
            logger.info(f"📝 Found {total_sentences} sentences to analyze")
            
            # Stage 3: FIXED - Sentence-by-sentence analysis with new rules format (15% - 85%)
            analysis_progress[analysis_id].update({
                "stage": "analysis",
                "percentage": 40,
                "message": "Analyzing sentences individually with all rules..."
            })
            logger.info(f"🔍 Stage 3 - Sentence-by-sentence analysis started")
            
            # Analyze each sentence individually with the new rules format
            try:
                rules = get_rules()
                logger.info(f"📚 Loaded {len(rules)} rules for sentence-by-sentence analysis")
                
                sentence_data = []
                total_issues = 0
                
                for index, sentence in enumerate(sentences):
                    sentence_feedback = []
                    # FIXED: Access sentence content correctly from dictionary format
                    sentence_text = sentence.get('sentence', '')  # Get plain text for rule analysis
                    sentence_html = sentence.get('html_segment', f'<p>{sentence_text}</p>')  # Get HTML for display
                    
                    # Apply each rule to this sentence
                    for rule in rules:
                        try:
                            rule_result = rule(sentence_text)
                            if rule_result:
                                # Handle both list and single item results
                                if isinstance(rule_result, list):
                                    for issue in rule_result:
                                        if isinstance(issue, str):
                                            sentence_feedback.append({
                                                "text": "",
                                                "start": 0,
                                                "end": len(sentence_text),
                                                "message": issue,
                                                "sentence_index": index
                                            })
                                        elif isinstance(issue, dict):
                                            sentence_feedback.append({
                                                "text": issue.get("text", ""),
                                                "start": issue.get("start", 0),
                                                "end": issue.get("end", len(sentence_text)),
                                                "message": issue.get("message", issue.get("suggestion", "")),
                                                "sentence_index": index
                                            })
                                else:
                                    if isinstance(rule_result, str):
                                        sentence_feedback.append({
                                            "text": "",
                                            "start": 0,
                                            "end": len(sentence_text),
                                            "message": rule_result,
                                            "sentence_index": index
                                        })
                        except Exception as e:
                            logger.warning(f"⚠️ Rule failed for sentence {index}: {e}")
                            continue
                    
                    # Add sentence data with feedback - FIXED: Use properly processed HTML content
                    sentence_data.append({
                        "content": sentence_html,  # Use extracted HTML segment
                        "plain": sentence_text,   # Plain text for analysis
                        "sentence": sentence_text,  # Frontend expects this property
                        "html_segment": sentence_html,  # Use extracted HTML segment
                        "feedback": sentence_feedback,
                        "index": index
                    })
                    
                    total_issues += len(sentence_feedback)
                    
                    # Update progress for each sentence
                    progress = 40 + int((index + 1) / len(sentences) * 40)  # 40% to 80%
                    analysis_progress[analysis_id].update({
                        "percentage": progress,
                        "message": f"Analyzed sentence {index + 1}/{len(sentences)}, found {len(sentence_feedback)} issues"
                    })
                
                logger.info(f"✅ Sentence-by-sentence analysis completed: {total_issues} total issues found")
                
                # Show progress for analysis completion
                analysis_progress[analysis_id].update({
                    "stage": "analysis",
                    "percentage": 85,
                    "message": f"Analysis complete: {total_issues} issues found across {len(sentences)} sentences"
                })
                
            except Exception as analysis_error:
                logger.error(f"❌ Error in sentence-by-sentence analysis: {analysis_error}")
                # Fallback to empty analysis - FIXED: Use correct format for frontend
                sentence_data = []
                for index, sent in enumerate(sentences):
                    sentence_data.append({
                        "content": f"<p>{sent.text}</p>",
                        "plain": sent.text,
                        "sentence": sent.text,  # ADDED: Frontend expects this property
                        "html_segment": f"<p>{sent.text}</p>",  # ADDED: Frontend expects this property
                        "feedback": [],
                        "index": index
                    })
            
            # Stage 4: Generating report (90%)
            analysis_progress[analysis_id].update({
                "stage": "reporting",
                "percentage": 90,
                "message": "Generating analysis report..."
            })
            logger.info(f"📊 Stage 4 - Reporting started: {analysis_progress[analysis_id]}")
            
            # Add longer delay to show reporting stage
            time.sleep(2.0)
            
            total_errors = sum(len(s['feedback']) for s in sentence_data)
            # FIXED: Calculate total words from processed sentences
            total_words = sum(len(s.get('sentence', '').split()) for s in sentence_data)
            quality_index = calculate_quality_index(total_sentences, total_errors)

            aggregated_report = {
                "totalSentences": total_sentences,
                "totalWords": total_words,
                "avgQualityScore": quality_index,
                "message": "Content analysis completed."
            }
            
            result = {
                "content": html_content,
                "sentences": sentence_data,
                "report": aggregated_report
            }
            
            # Stage 5: Complete (100%)
            analysis_progress[analysis_id].update({
                "stage": "complete",
                "percentage": 100,
                "message": "Analysis complete!",
                "completed": True,
                "result": result
            })
            logger.info(f"🎉 Analysis completed successfully: {analysis_id}")
            logger.info(f"📊 Final result summary: {total_sentences} sentences, {total_errors} issues, quality: {quality_index}%")
            logger.info(f"📄 Content length: {len(result.get('content', ''))} characters")
            logger.info(f"🔍 First few issues: {[s.get('feedback', [])[:2] for s in sentence_data[:3] if s.get('feedback')]}")
            
        except Exception as e:
            analysis_progress[analysis_id].update({
                "stage": "error",
                "percentage": 0,
                "message": f"Error: {str(e)}",
                "error": str(e),
                "completed": True
            })
            logger.error(f"Progressive analysis error in thread: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # Start the analysis in a background thread
    analysis_thread = threading.Thread(target=run_analysis)
    analysis_thread.daemon = True
    analysis_thread.start()
    
    logger.info(f"🎯 Analysis thread started, returning analysis_id: {analysis_id}")
    
    # Return immediately with the analysis ID
    return jsonify({
        "analysis_id": analysis_id,
        "success": True
    })

@main.route('/analysis_progress/<analysis_id>')
def get_analysis_progress(analysis_id):
    """Get the current progress of an analysis"""
    from flask import make_response
    
    progress = analysis_progress.get(analysis_id, {
        "stage": "unknown",
        "percentage": 0,
        "message": "Analysis not found",
        "completed": True,
        "error": "Analysis ID not found"
    })
    
    logger.info(f"� Progress requested for {analysis_id}")
    logger.info(f"🔍 Progress data: {progress}")
    if 'result' in progress:
        result = progress['result']
        logger.info(f"🔍 Result structure: {type(result)} with keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if isinstance(result, dict):
            logger.info(f"🔍 Result content: sentences={len(result.get('sentences', []))}, report keys={list(result.get('report', {}).keys())}, content length={len(result.get('content', ''))}")
    
    # Create response with no-cache headers
    response = make_response(jsonify(progress))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main.route('/analysis_stream/<analysis_id>')
def analysis_stream(analysis_id):
    """Server-Sent Events stream for real-time progress updates"""
    def generate():
        while True:
            progress = analysis_progress.get(analysis_id, {})
            if not progress:
                yield f"data: {json.dumps({'error': 'Analysis not found'})}\n\n"
                break
                
            yield f"data: {json.dumps(progress)}\n\n"
            
            if progress.get('completed', False):
                # Cleanup after completion
                if analysis_id in analysis_progress:
                    # Keep result for a short time then clean up
                    import threading
                    def cleanup():
                        time.sleep(30)  # Keep for 30 seconds
                        analysis_progress.pop(analysis_id, None)
                    threading.Thread(target=cleanup).start()
                break
                
            time.sleep(0.5)  # Update every 500ms
    
    return Response(generate(), mimetype='text/plain')

feedback_list = []

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
    global current_document_content  # Access global variable
    
    from .ai_improvement import get_enhanced_ai_suggestion
    from .performance_monitor import track_suggestion, learning_system
    import uuid
    import time
    
    data = request.get_json()
    feedback_text = data.get('feedback')
    sentence_context = data.get('sentence', '')
    document_type = data.get('document_type', 'general')
    writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
    
    logger.info(f"AI suggestion request: feedback='{feedback_text[:50]}...', sentence='{sentence_context[:50]}...'")
    
    if not feedback_text:
        logger.error("No feedback provided in AI suggestion request")
        return jsonify({"error": "No feedback provided"}), 400

    suggestion_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        # First try learned suggestions from user feedback
        learned_suggestion = learning_system.get_learned_suggestion(feedback_text, sentence_context)
        
        if learned_suggestion:
            response_time = time.time() - start_time
            track_suggestion(suggestion_id, feedback_text, sentence_context, 
                           document_type, "learned_pattern", response_time)
            
            logger.info(f"Using learned pattern suggestion for: {feedback_text[:30]}...")
            return jsonify({
                "suggestion": learned_suggestion,
                "ai_answer": "Using learned pattern from previous user feedback.",
                "confidence": "high",
                "method": "learned_pattern",
                "suggestion_id": suggestion_id,
                "note": "Generated using learned patterns from user feedback"
            })
        
        # Use enhanced AI suggestion system with RAG
        logger.info("Getting enhanced AI suggestion with RAG context...")
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals,
            document_content=current_document_content  # Pass document content for RAG
        )
        
        # Validate result structure
        if not result or not isinstance(result, dict):
            raise ValueError(f"Invalid result structure: {type(result)}")
            
        if 'suggestion' not in result:
            raise ValueError(f"Missing 'suggestion' in result: {list(result.keys())}")
            
        if not result['suggestion'] or not str(result['suggestion']).strip():
            raise ValueError("Empty or whitespace-only suggestion returned")
        
        response_time = time.time() - start_time
        track_suggestion(suggestion_id, feedback_text, sentence_context, 
                        document_type, result.get("method", "unknown"), response_time)
        
        logger.info(f"AI suggestion successful using method: {result.get('method', 'unknown')}")
        return jsonify({
            "suggestion": result["suggestion"],
            "ai_answer": result.get("ai_answer", ""),
            "confidence": result.get("confidence", "medium"),
            "method": result.get("method", "unknown"),
            "suggestion_id": suggestion_id,
            "context_used": result.get("context_used", {}),
            "sources": result.get("sources", []),
            "note": f"Generated using {result.get('method', 'unknown')} approach"
        })
        
    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        response_time = time.time() - start_time
        
        # Final fallback
        suggestion = generate_smart_suggestion(feedback_text)
        track_suggestion(suggestion_id, feedback_text, sentence_context, 
                        document_type, "basic_fallback", response_time)
        
        return jsonify({
            "suggestion": suggestion, 
            "ai_answer": "AI enhancement unavailable. Using basic rule-based guidance.",
            "confidence": "low",
            "method": "basic_fallback",
            "suggestion_id": suggestion_id,
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

@main.route('/rag-status')
def rag_status():
    """Get Enhanced RAG system status for debugging and monitoring."""
    try:
        if RAG_AVAILABLE:
            status = get_rag_status()
            return jsonify({
                "success": True,
                "rag_system": status,
                "integration": "active"
            })
        else:
            return jsonify({
                "success": False,
                "error": "RAG system not available",
                "integration": "disabled"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "integration": "error"
        })

@main.route('/debug-ai')
def debug_ai():
    """Serve the AI debugging page"""
    debug_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_ai_frontend.html')
    with open(debug_file_path, 'r', encoding='utf-8') as f:
        return f.read()