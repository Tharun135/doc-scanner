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
import spacy
import textstat
import ollama
import time
import uuid
from dataclasses import asdict

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)  # Or logging.INFO for production
logger = logging.getLogger(__name__)

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

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
            rule_path = os.path.join(rules_folder, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], rule_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "check"):
                rules.append(module.check)
                logger.info(f"Loaded rule: {filename} (Function: {module.check.__name__})")
            else:
                logger.warning(f"Warning: {filename} does not have a `check` function")

    logger.info(f"Total rules loaded: {len(rules)}")
    return rules

rules = load_rules()

def review_document(content, rules):
    suggestions = []
    for rule in rules:
        feedback = rule(content)
        if feedback:
            for item in feedback:
                suggestions.append({
                    "text": item["text"],
                    "start": item["start"],
                    "end": item["end"],
                    "message": item["message"]
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
                    # Convert string to expected object format
                    feedback.append({
                        "text": sentence,
                        "start": 0,
                        "end": len(sentence),
                        "message": item
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

        # Split on newlines and punctuation for better sentence segmentation
        lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
        sentences = []
        for line in lines:
            # Use spaCy to further split lines with multiple sentences
            doc = nlp(line)
            for sent in doc.sents:
                sentences.append(sent)

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
    from .ai_improvement import get_enhanced_ai_suggestion
    from .performance_monitor import track_suggestion, learning_system
    import uuid
    
    data = request.get_json()
    feedback_text = data.get('feedback')
    sentence_context = data.get('sentence', '')
    document_type = data.get('document_type', 'general')
    writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
    
    if not feedback_text:
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
            
            return jsonify({
                "suggestion": learned_suggestion,
                "confidence": "high",
                "method": "learned_pattern",
                "suggestion_id": suggestion_id,
                "note": "Generated using learned patterns from user feedback"
            })
        
        # Use enhanced AI suggestion system
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals
        )
        
        response_time = time.time() - start_time
        track_suggestion(suggestion_id, feedback_text, sentence_context, 
                        document_type, result["method"], response_time)
        
        return jsonify({
            "suggestion": result["suggestion"],
            "confidence": result["confidence"],
            "method": result["method"],
            "suggestion_id": suggestion_id,
            "context_used": result.get("context_used", {}),
            "note": f"Generated using {result['method']} approach"
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