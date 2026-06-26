import re
import os

with open('d:/doc-scanner/app/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove endpoints
endpoints_to_remove = [
    (r"@main\.route\('/analyze_intelligent', methods=\['POST'\]\).*?(?=@main\.route\('/)", ""),
    (r"@main\.route\('/intelligent_results'\).*?(?=@main\.route\('/)", ""),
    (r"@main\.route\('/api/knowledge/learn', methods=\['POST'\]\).*?(?=@main\.route\('/)", ""),
    (r"@main\.route\('/api/enrich_issue', methods=\['POST'\]\).*?(?=@main\.route\('/)", ""),
]

for pattern, replacement in endpoints_to_remove:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 2. Rewrite /ai_suggestion endpoint
ai_suggestion_new = """@main.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():
    \"\"\"
    Community Edition: No AI rewriting. 
    Returns document references from RAG instead.
    \"\"\"
    global current_document_content, current_sentences_list
    import uuid
    import time
    from .advanced_retrieval import create_retriever, retrieve_for_writing_feedback
    import logging

    logger = logging.getLogger(__name__)

    data = request.get_json() or {}
    feedback_text   = data.get('feedback')
    multiple_feedback = data.get('multiple_feedback', [])
    sentence_context = data.get('sentence', '') or ''
    document_type   = data.get('document_type', 'general')
    document_title  = data.get('document_title', 'Unknown Document')
    writing_goals   = data.get('writing_goals', ['clarity', 'conciseness'])
    option_number   = data.get('option_number', 1)
    sentence_index  = data.get('sentence_index', -1)
    
    if not feedback_text and multiple_feedback:
        feedback_text = multiple_feedback[0]

    logger.info(f"RAG suggestion request: feedback='{feedback_text[:50] if feedback_text else ''}...', sentence='{sentence_context[:50]}...'")

    suggestion_id = str(uuid.uuid4())
    start_time = time.time()

    # Query RAG for references
    sources = []
    try:
        retriever = create_retriever()
        query = f"{feedback_text} {sentence_context}"
        rag_results = retrieve_for_writing_feedback(query, retriever, current_document_content)
        
        for res in rag_results:
            sources.append({
                "content": res.content,
                "source": res.metadata.get('source_doc_id', 'Knowledge Base'),
                "score": res.relevance_score
            })
    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")

    # Ensure we use rule feedback as Suggested Action
    ai_answer = data.get('ai_answer', '')
    if not ai_answer:
        ui_issue = data.get('issue')
        if ui_issue and isinstance(ui_issue, dict) and 'reviewer_rationale' in ui_issue:
            ai_answer = ui_issue['reviewer_rationale']
        else:
            ai_answer = f"Review needed based on rule: {feedback_text}"

    return jsonify({
        "suggestion": "", # No AI generation
        "ai_answer": ai_answer,
        "confidence": "high",
        "method": "community_edition_rag",
        "suggestion_id": suggestion_id,
        "sources": sources,
        "context_used": {
            "document_type": document_type,
            "writing_goals": writing_goals
        },
        "note": "Generated using Rule-Based Engine + RAG (Community Edition)",
        "is_semantic_explanation": False,
        "is_guidance_only": True,
        "is_reviewer_rationale": False,
        "guidance_category": "readability",
        "semantic_explanation": "",
        "decision_type": ""
    })
"""

content = re.sub(r"@main\.route\('/ai_suggestion', methods=\['POST'\]\).*?(?=@main\.route|$)", ai_suggestion_new, content, flags=re.DOTALL)

with open('d:/doc-scanner/app/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
