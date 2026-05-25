import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.services.style_guide_service import retrieve_relevant_style_rules, retrieve_relevant_manual_chunks, mask_sensitive

sentence = "You cannot delete data sources while \"start project\", \"stop project\", or \"deploy project\" operation is running."
issue_type = "sentence_length"
feedback_text = "Long sentence detected (26 words)"

masked_sentence, replacements = mask_sensitive(sentence)
retrieved_context = retrieve_relevant_manual_chunks(masked_sentence, n_results=3)
retrieved_rules = retrieve_relevant_style_rules(issue_type, feedback_text, n_results=2)

print("=== MASKED SENTENCE ===")
print(masked_sentence)
print("\n=== RETRIEVED RULES ===")
print(retrieved_rules)
print("\n=== RETRIEVED CONTEXT ===")
print(retrieved_context)
