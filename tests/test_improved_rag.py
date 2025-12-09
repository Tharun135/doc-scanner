"""
Test improved RAG system
"""
import sys
sys.path.append('scripts')
from scripts.docscanner_ollama_rag import DocScannerOllamaRAG

print('🔧 Testing improved RAG with passive voice example...')
rag = DocScannerOllamaRAG()

# Test with your exact example
result = rag.get_rag_suggestion(
    feedback_text='Avoid passive voice in sentence',
    sentence_context='The Time, Description, and Comments columns are fixed and cannot be removed.',
    document_type='technical'
)

if result:
    print(f'Method: {result.get("method", "unknown")}')
    print(f'Original: The Time, Description, and Comments columns are fixed and cannot be removed.')
    print(f'AI Suggestion: {result["suggestion"]}')
    
    # Check if it's an intelligent suggestion
    suggestion = result['suggestion']
    if ('Consider Revising' not in suggestion and 
        ('system fixes' in suggestion.lower() or 'prevents' in suggestion.lower())):
        print('✅ SUCCESS: Intelligent suggestion generated!')
    else:
        print('🔄 Still needs improvement')
        print(f'Suggestion type: Generic' if 'Consider' in suggestion else 'Improved')
else:
    print('❌ No result from RAG')
