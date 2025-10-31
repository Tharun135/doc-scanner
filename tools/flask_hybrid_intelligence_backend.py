"""
Flask Backend with Hybrid Intelligence RAG-LLM System
====================================================

This implements your Flask backend with hybrid model selection:
- phi3:mini for fast, lightweight tasks (90% of cases)  
- llama3:8b for deep reasoning and complex analysis
- RAG-enhanced context for intelligent responses
- RESTful API endpoints for DocScanner integration
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import time
import logging
from hybrid_intelligence_rag_system import HybridIntelligenceRAGSystem, FlaggedIssue, IntelligenceMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize the hybrid intelligence system
rag_llm_system = HybridIntelligenceRAGSystem()

@app.route('/')
def index():
    """Simple web interface for testing"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DocScanner AI - Hybrid Intelligence</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 10px 0; }
            input, textarea, select { width: 100%; padding: 10px; margin: 5px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; }
            .result { background: #e8f5e8; padding: 15px; border-radius: 5px; margin-top: 15px; }
            .error { background: #ffe6e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <h1>🧠 DocScanner AI - Hybrid Intelligence Test</h1>
        
        <div class="container">
            <h3>Test RAG → LLM System</h3>
            <textarea id="sentence" placeholder="Enter sentence to improve..." rows="3"></textarea>
            
            <select id="issueType">
                <option value="Passive voice">Passive voice</option>
                <option value="Long sentence">Long sentence</option>
                <option value="Vague terms">Vague terms</option>
                <option value="Complex sentence structure">Complex sentence structure</option>
                <option value="Title capitalization">Title capitalization</option>
            </select>
            
            <select id="complexity">
                <option value="default">Auto-select Model</option>
                <option value="fast">Fast (phi3:mini)</option>
                <option value="deep">Deep (llama3:8b)</option>
            </select>
            
            <input type="text" id="context" placeholder="Optional: surrounding context...">
            
            <button onclick="getAISuggestion()">Get AI Suggestion</button>
            
            <div id="result"></div>
        </div>

        <script>
        async function getAISuggestion() {
            const sentence = document.getElementById('sentence').value;
            const issueType = document.getElementById('issueType').value;
            const complexity = document.getElementById('complexity').value;
            const context = document.getElementById('context').value;
            
            if (!sentence) {
                alert('Please enter a sentence');
                return;
            }
            
            document.getElementById('result').innerHTML = '<p>🤖 Processing with hybrid intelligence...</p>';
            
            try {
                const response = await fetch('/api/ai-suggestion', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        sentence: sentence,
                        issue_type: issueType,
                        complexity: complexity,
                        context: context
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                            <h4>✨ AI Suggestion</h4>
                            <p><strong>Model Used:</strong> ${result.model_used} (${result.intelligence_mode} mode)</p>
                            <p><strong>Original:</strong> "${result.original}"</p>
                            <p><strong>Corrected:</strong> "${result.corrected}"</p>
                            <p><strong>Reasoning:</strong> ${result.reasoning}</p>
                            <p><strong>Explanation:</strong> ${result.explanation}</p>
                            ${result.analysis ? `<p><strong>Deep Analysis:</strong> ${result.analysis}</p>` : ''}
                            ${result.alternatives ? `<p><strong>Alternatives:</strong> ${result.alternatives}</p>` : ''}
                        </div>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <div class="error">
                            <h4>❌ Error</h4>
                            <p>${result.error}</p>
                            <p><strong>Attempted Model:</strong> ${result.model_used || 'Unknown'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <div class="error">
                        <h4>❌ Network Error</h4>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        </script>
    </body>
    </html>
    """)

@app.route('/api/ai-suggestion', methods=['POST'])
def get_ai_suggestion():
    """
    Get AI suggestion using hybrid intelligence model selection
    
    Your main API endpoint that implements:
    - RAG context retrieval
    - Intelligent model selection (phi3:mini vs llama3:8b)
    - Context-aware response generation
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'sentence' not in data or 'issue_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: sentence, issue_type'
            }), 400
        
        # Create flagged issue
        flagged_issue = FlaggedIssue(
            sentence=data['sentence'],
            issue=data['issue_type'],
            context=data.get('context', ''),
            complexity=data.get('complexity', 'default'),
            severity=data.get('severity', 'medium'),
            line_number=data.get('line_number')
        )
        
        logger.info(f"Processing AI suggestion for: {flagged_issue.issue}")
        
        # Generate hybrid intelligence solution
        start_time = time.time()
        result = rag_llm_system.generate_hybrid_solution(flagged_issue)
        processing_time = time.time() - start_time
        
        # Add metadata
        result['processing_time'] = round(processing_time, 3)
        result['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing AI suggestion: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch-suggestions', methods=['POST'])
def get_batch_suggestions():
    """
    Process multiple writing issues with hybrid intelligence
    
    Automatically selects appropriate model for each issue:
    - Simple issues → phi3:mini (fast)
    - Complex issues → llama3:8b (deep reasoning)
    """
    try:
        data = request.json
        
        if not data or 'issues' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: issues'
            }), 400
        
        issues = data['issues']
        results = []
        total_processing_time = 0
        model_usage = {'phi3:mini': 0, 'llama3:8b': 0, 'failed': 0}
        
        logger.info(f"Processing {len(issues)} issues with hybrid intelligence")
        
        for i, issue_data in enumerate(issues):
            try:
                # Create flagged issue
                flagged_issue = FlaggedIssue(
                    sentence=issue_data.get('sentence', ''),
                    issue=issue_data.get('issue_type', ''),
                    context=issue_data.get('context', ''),
                    complexity=issue_data.get('complexity', 'default'),
                    severity=issue_data.get('severity', 'medium'),
                    line_number=issue_data.get('line_number')
                )
                
                # Generate solution
                start_time = time.time()
                result = rag_llm_system.generate_hybrid_solution(flagged_issue)
                processing_time = time.time() - start_time
                
                # Track usage
                if result['success']:
                    model_used = result['model_used']
                    model_usage[model_used] = model_usage.get(model_used, 0) + 1
                else:
                    model_usage['failed'] += 1
                
                result['processing_time'] = round(processing_time, 3)
                result['issue_index'] = i
                results.append(result)
                
                total_processing_time += processing_time
                
            except Exception as e:
                logger.error(f"Error processing issue {i}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'issue_index': i
                })
                model_usage['failed'] += 1
        
        return jsonify({
            'success': True,
            'total_issues': len(issues),
            'successful': len([r for r in results if r.get('success')]),
            'failed': len([r for r in results if not r.get('success')]),
            'total_processing_time': round(total_processing_time, 3),
            'model_usage': model_usage,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing batch suggestions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models/status', methods=['GET'])
def get_models_status():
    """Check which models are available and their status"""
    try:
        import requests
        
        # Check Ollama connection
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models_info = response.json()
                available_models = [model['name'] for model in models_info.get('models', [])]
                
                status = {
                    'ollama_running': True,
                    'available_models': available_models,
                    'phi3_available': any('phi3' in model for model in available_models),
                    'llama3_available': any('llama3' in model for model in available_models),
                    'hybrid_ready': any('phi3' in model for model in available_models) and any('llama3' in model for model in available_models)
                }
            else:
                status = {'ollama_running': False, 'error': 'Ollama API error'}
                
        except requests.exceptions.ConnectionError:
            status = {'ollama_running': False, 'error': 'Cannot connect to Ollama'}
        except Exception as e:
            status = {'ollama_running': False, 'error': str(e)}
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag-contexts', methods=['GET'])
def get_rag_contexts():
    """Get available RAG contexts and their complexity assessments"""
    try:
        contexts = {}
        for issue_type, rag_data in rag_llm_system.rag_knowledge_base.items():
            contexts[issue_type] = {
                'suggestion': rag_data['suggestion'],
                'complexity': rag_data['complexity'],
                'examples_count': len(rag_data['examples']),
                'context_length': len(rag_data['context'])
            }
        
        return jsonify({
            'success': True,
            'total_contexts': len(contexts),
            'contexts': contexts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_model_response(query: str, context: str, mode: str = "default") -> str:
    """
    Your requested function for hybrid intelligence model selection
    
    Args:
        query: The question or task
        context: RAG context or surrounding information  
        mode: "default" for phi3:mini, "deep" for llama3:8b
        
    Returns:
        AI-generated response using appropriate model
    """
    
    # Determine model based on mode
    if mode == "deep":
        model = "llama3:8b"
        intelligence_mode = IntelligenceMode.DEEP
    else:
        model = "phi3:mini"
        intelligence_mode = IntelligenceMode.DEFAULT
    
    # Build the prompt
    prompt = f"Context:\\n{context}\\n\\nQuestion:\\n{query}"
    
    # Call the model
    try:
        response = rag_llm_system.call_ollama_chat(
            prompt=prompt, 
            model=model, 
            mode=intelligence_mode
        )
        return response if response else "Model unavailable"
    
    except Exception as e:
        logger.error(f"Error in get_model_response: {e}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    print("🚀 Starting DocScanner AI Flask Backend")
    print("=" * 50)
    print("🧠 Hybrid Intelligence Models:")
    print("   • phi3:mini - Fast responses for 90% of tasks")
    print("   • llama3:8b - Deep reasoning for complex analysis")
    print()
    print("📡 API Endpoints:")
    print("   • POST /api/ai-suggestion - Single suggestion")
    print("   • POST /api/batch-suggestions - Multiple suggestions") 
    print("   • GET /api/models/status - Check model availability")
    print("   • GET /api/rag-contexts - View RAG contexts")
    print()
    print("🌐 Web Interface: http://localhost:5000")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)