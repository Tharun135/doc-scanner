"""
Test the full sentence review pipeline:
  classify → retrieve rules → (optional rerank) → Gemini LLM → structured output

Run from project root:
    python scratch/test_sentence_reviewer.py
"""
import sys
import os
sys.path.insert(0, 'd:/doc-scanner')

# Auto-load .env if present (this project uses GOOGLE_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.rag.sentence_reviewer import review_sentence, classify_sentence, retrieve_and_rerank

# -----------------------------------------------------------------------
# Test sentences — mix of violations and clean sentences
# -----------------------------------------------------------------------
TEST_SENTENCES = [
    # Should flag TENSE_001
    "The system shall start automatically.",
    # Should flag UI_001 / UI_002
    "Click on the Save button to continue.",
    # Should flag PERSON_001
    "I will configure the network settings.",
    # Should flag CONTRACTION_001
    "Do not close the window if you don't want to lose your work.",
    # Should flag ADV_001
    "Simply click Next to proceed.",
    # Should flag JARGON_001
    "Utilize the configuration utility to optimize performance.",
    # Clean sentence — should be compliant
    "Click Save.",
    # Should flag passive voice (TENSE_002 / grammar category)
    "The configuration should be updated by the user.",
]

print("=" * 70)
print("STEP 1: Classifier test (no LLM, no ChromaDB)")
print("=" * 70)
for sent in TEST_SENTENCES[:4]:
    hits = classify_sentence(sent)
    print(f"\n  Sentence: {sent}")
    print(f"  Classified: {[h['hint'] for h in hits]}")

print("\n" + "=" * 70)
print("STEP 2: Retrieval test (ChromaDB only, no LLM)")
print("=" * 70)
for sent in TEST_SENTENCES[:4]:
    rules = retrieve_and_rerank(sent, categories=[], top_k_retrieve=5, top_k_final=2)
    print(f"\n  Sentence: {sent}")
    for r in rules:
        print(f"    -> {r['rule_id']} [{r['category']}] score={r['score']}")

print("\n" + "=" * 70)
print("STEP 3: Full pipeline test (Privacy Mode: Ollama Local)")
print("=" * 70)

allow_cloud = os.environ.get("ALLOW_CLOUD_LLM", "true").lower() != "false"
ollama_model = os.environ.get("OLLAMA_MODEL", "phi3:mini")

if not allow_cloud:
    print(f"\n  [SECURE] Privacy Mode Enabled: Cloud LLMs (Gemini) are DISABLED.")
    print(f"  [STATUS] Attempting to use Local Ollama ({ollama_model})...\n")
    use_llm = True
else:
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n  [INFO] Cloud LLM allowed but no key found. Using Ollama fallback...")
        use_llm = True
    else:
        print(f"\n  [OK] GOOGLE_API_KEY found (****{api_key[-4:]}) - Gemini allowed as fallback\n")
        use_llm = True

for sent in TEST_SENTENCES:
    result = review_sentence(sent, top_k_final=3, use_llm=use_llm)
    status = "COMPLIANT" if result.get("compliant") else f"VIOLATION: {result.get('violation', '?')}"
    rule = result.get("rule_id", "—")
    suggestion = result.get("suggestion", "")[:80]
    method = result.get("method", "?")
    print(f"\n  [{status}] [{rule}] ({method})")
    print(f"    Sentence:   {sent}")
    if not result.get("compliant"):
        print(f"    Explanation: {result.get('explanation', '')[:120]}")
        print(f"    Suggestion:  {suggestion}")
