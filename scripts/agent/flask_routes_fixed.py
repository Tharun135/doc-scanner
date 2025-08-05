from flask import Blueprint, request, jsonify
import os
import sys
from bs4 import BeautifulSoup
import logging

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the existing analysis function
from app.app import analyze_sentence, load_rules

# Create the agent blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

logger = logging.getLogger(__name__)

# Load rules once when blueprint is imported
rules = load_rules()

@agent_bp.route('/status', methods=['GET'])
def agent_status():
    """Get agent status"""
    return jsonify({
        "status": "running", 
        "message": "Document Review Agent is operational",
        "rules_loaded": len(rules),
        "version": "1.0.0"
    })

@agent_bp.route('/analyze', methods=['POST'])
def analyze_document():
    """Analyze document content sent as JSON"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        document_content = data.get('document_content', '')
        document_type = data.get('document_type', 'general')
        
        if not document_content:
            return jsonify({"error": "No document content provided"}), 400
        
        logger.info(f"Analyzing document content of length: {len(document_content)}")
        
        # Split content into sentences for analysis
        lines = [line.strip() for line in document_content.split('\n') if line.strip()]
        
        all_issues = []
        total_issues = 0
        
        for line_index, line in enumerate(lines):
            if line.strip():
                # Analyze each line
                feedback, readability_scores, quality_score = analyze_sentence(line, rules)
                
                for issue in feedback:
                    if isinstance(issue, dict):
                        issue['line_number'] = line_index + 1
                        issue['line_content'] = line
                        all_issues.append(issue)
                        total_issues += 1
        
        return jsonify({
            "status": "success",
            "total_issues": total_issues,
            "issues": all_issues,
            "document_type": document_type,
            "lines_analyzed": len(lines)
        })
        
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@agent_bp.route('/suggest', methods=['POST'])
def get_ai_suggestion():
    """Get AI suggestion for a specific issue"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        feedback_text = data.get('feedback_text', '')
        sentence_context = data.get('sentence_context', '')
        
        # For now, return a simple suggestion
        # This can be enhanced with actual AI integration later
        suggestion = f"Consider revising: {sentence_context}"
        
        return jsonify({
            "status": "success",
            "suggestion": suggestion,
            "feedback_text": feedback_text
        })
        
    except Exception as e:
        logger.error(f"Error getting AI suggestion: {e}")
        return jsonify({"error": f"Suggestion failed: {str(e)}"}), 500

@agent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "rules_loaded": len(rules),
        "endpoints": ["/status", "/analyze", "/suggest", "/health"]
    })
