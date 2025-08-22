"""
Test the fallback logic directly
"""
import sys
sys.path.append('scripts')
from scripts.docscanner_ollama_rag import DocScannerOllamaRAG

print('🔧 Testing fallback logic for passive voice...')

# Create RAG instance
rag = DocScannerOllamaRAG()

# Test the fallback method directly
feedback_text = 'Avoid passive voice in sentence'
sentence = 'The Time, Description, and Comments columns are fixed and cannot be removed.'

print(f'Original: {sentence}')

# Test the passive voice fallback
fallback_suggestion = rag._generate_passive_voice_fallback(sentence)
print(f'Fallback Suggestion: {fallback_suggestion}')

# Test similarity calculation
original_lower = sentence.lower()
similarity_same = rag._calculate_similarity(original_lower, original_lower)
similarity_different = rag._calculate_similarity(original_lower, "the system fixes the columns")

print(f'Similarity (same): {similarity_same}')
print(f'Similarity (different): {similarity_different}')

# Test cleaning with a bad AI response
bad_ai_response = f"Consider Revising For Better Clarity: {sentence}"
cleaned = rag._clean_suggestion(bad_ai_response, sentence, feedback_text)
print(f'Cleaned suggestion: {cleaned}')

if 'system fixes' in cleaned.lower():
    print('✅ SUCCESS: Fallback generated intelligent suggestion!')
else:
    print('🔄 Fallback needs adjustment')
