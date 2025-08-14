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
import spacy
import textstat
import time
from dataclasses import asdict

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("python-dotenv not available - environment variables must be set manually")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to hide RAG debug messages
logger = logging.getLogger(__name__)

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    logger.info("spaCy model loaded successfully")
except Exception as e:
    logger.warning(f"spaCy model not available: {e}")
    nlp = None
    SPACY_AVAILABLE = False

############################
# PARSING HELPERS
############################

def parse_file(file):
    filename = file.filename.lower()
    extension = os.path.splitext(filename)[1]

    try:
        if extension == '.docx':
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
        plain_text = soup.get_text(separator="\n")
        
        # Store the document content for RAG context
        current_document_content = plain_text

        # Split on newlines and punctuation for better sentence segmentation
        lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
        sentences = []
        for line in lines:
            if SPACY_AVAILABLE and nlp:
                # Use spaCy to further split lines with multiple sentences
                doc = nlp(line)
                for sent in doc.sents:
                    sentences.append(sent)
            else:
                # Fallback: simple sentence splitting when spaCy is not available
                import re
                # Split by sentence-ending punctuation
                simple_sentences = re.split(r'[.!?]+\s+', line)
                for sent_text in simple_sentences:
                    if sent_text.strip():
                        # Create a simple sentence object
                        class SimpleSentence:
                            def __init__(self, text):
                                self.text = text.strip()
                                self.start_char = 0
                                self.end_char = len(text)
                        sentences.append(SimpleSentence(sent_text.strip()))

        sentence_data = []
        for index, sent in enumerate(sentences):
            feedback, readability_scores, quality_score = analyze_sentence(sent.text, rules)
            
            # Add sentence index to each feedback item for UI linking
            enhanced_feedback = []
            for item in feedback:
                if isinstance(item, dict):
                    item['sentence_index'] = index
                    enhanced_feedback.append(item)
                else:
                    enhanced_feedback.append({
                        "text": sent.text,
                        "start": 0,
                        "end": len(sent.text),
                        "message": str(item),
                        "sentence_index": index
                    })
            
            sentence_data.append({
                "sentence": sent.text,
                "sentence_index": index,
                "feedback": enhanced_feedback,
                "readability_scores": readability_scores,
                "quality_score": quality_score,
                "start": sent.start_char,
                "end": sent.end_char
            })

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
    """Get RAG-powered AI suggestions for writing improvements."""
    global current_document_content
    
    # Import RAG system
    try:
        from .rules.rag_main import get_rag_suggestion
    except ImportError:
        return jsonify({"error": "RAG system not available"}), 500
    
    data = request.get_json()
    feedback_text = data.get('feedback', '')
    sentence_context = data.get('sentence', '')
    document_type = data.get('document_type', 'general')
    writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
    
    if not feedback_text:
        return jsonify({"error": "No feedback text provided"}), 400
    
    try:
        # Use RAG system to get contextual suggestions
        rag_response = get_rag_suggestion(
            issue_text=feedback_text,
            sentence_context=sentence_context,
            category=document_type
        )
        
        # Format response for web interface
        response = {
            "suggestion": rag_response.get('suggestion', 'No specific suggestion available'),
            "original_text": sentence_context,
            "improved_text": rag_response.get('improved_text', sentence_context),
            "explanation": rag_response.get('explanation', 'RAG-powered improvement suggestion'),
            "source": rag_response.get('source', 'Knowledge Base'),
            "confidence": rag_response.get('confidence', 0.8),
            "category": rag_response.get('category', 'general'),
            "timestamp": time.time()
        }
        
        logger.info(f"RAG suggestion provided for: {feedback_text[:50]}...")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting RAG suggestion: {e}")
        return jsonify({"error": f"Failed to get suggestion: {str(e)}"}), 500

@main.route('/suggestion_feedback', methods=['POST'])
def suggestion_feedback():
    """Record user feedback on AI suggestions."""
    try:
        from .performance_monitor import record_user_feedback
    except ImportError:
        logger.warning("Performance monitor not available")
        return jsonify({"message": "Feedback noted (monitor unavailable)"})
    
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
    try:
        from .performance_monitor import get_performance_dashboard
        dashboard_data = get_performance_dashboard()
        return jsonify(dashboard_data)
    except ImportError:
        logger.warning("Performance monitor not available")
        return jsonify({
            "error": "Performance dashboard not available",
            "suggestions_count": 0,
            "avg_response_time": 0,
            "user_satisfaction": 0
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"error": "Failed to get dashboard data"}), 500

@main.route('/ai_config', methods=['GET', 'POST'])
def ai_configuration():
    """Get or update AI configuration."""
    try:
        from .ai_config import config_manager
    except ImportError:
        logger.warning("AI config manager not available")
        if request.method == 'GET':
            return jsonify({
                "available_models": ["RAG System"],
                "suggestion_config": {"enabled": True},
                "feature_flags": {"rag_enabled": True}
            })
        else:
            return jsonify({"message": "Configuration not available"})
    
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

@main.route('/api_quota_status', methods=['GET'])
def api_quota_status():
    """Get current API quota status."""
    try:
        from .rate_limiter import get_quota_status
        status = get_quota_status()
        return jsonify(status)
    except ImportError:
        return jsonify({
            "error": "Rate limiter not available",
            "used": 0,
            "limit": 50,
            "remaining": 50,
            "can_make_request": True
        })
    except Exception as e:
        logger.error(f"Error getting quota status: {str(e)}")
        return jsonify({"error": "Failed to get quota status"}), 500

@main.route('/reset_quota', methods=['POST'])
def reset_api_quota():
    """Manually reset API quota (admin function)."""
    try:
        from .rate_limiter import reset_quota
        reset_quota()
        return jsonify({"message": "Quota reset successfully"})
    except ImportError:
        return jsonify({"error": "Rate limiter not available"}), 400
    except Exception as e:
        logger.error(f"Error resetting quota: {str(e)}")
        return jsonify({"error": "Failed to reset quota"}), 500

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

if __name__ == '__main__':
    from . import create_app
    print("🚀 Starting Doc Scanner with RAG System...")
    print("🌐 Access at: http://localhost:5000")
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)