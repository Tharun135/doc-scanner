import requests
import json
import time

prompt = """You are a technical documentation style guide assistant.
The rule checker flagged a potential issue in the following sentence/heading.

Sentence/Heading:
"You cannot delete data sources while "start project", "stop project", or "deploy project" operation is running."

Flagged Issue Category/Type: sentence_length
Rule Warning Message: Long sentence detected (26 words)

Relevant Siemens Style Guide Rules:
Rule: sentence_length
Description: Use as few words as possible (less than 20 words per sentence). Break longer descriptions into smaller chunks.
Good Example: When importing an app from an external source, ensure all dependencies are correctly configured. Check that the app is compatible with the existing system architecture.
Bad Example: When importing an app from an external source, it is crucial to ensure that all dependencies are correctly configured and that the app is compatible with the existing system architecture to avoid potential integration issues.

Your task:
Analyze the sentence and the rule warning message in light of the style guide rules.
1. Determine if the warning message is a FALSE POSITIVE (i.e. the flagged sentence is correct under the style rules, or represents an allowed exception).
   * Note: A sentence length warning is NOT a false positive if the sentence has 20 or more words. You must rewrite it to be shorter or split it.
2. If it is a false positive, the SOLUTION is to keep the original sentence.
3. If it is a genuine style issue, the SOLUTION is to provide the corrected sentence conforming to the style rules (e.g. converting non-product names to lowercase, changing to active voice, splitting long sentences, etc.).

Output the analysis in this exact format:
1. Issue detected: [State the issue, or write "None" if it is a false positive]
2. Explanation: [Provide a brief explanation of the style evaluation or what was changed]
3. Suggested rewrite: [Write ONLY the final corrected sentence or the original sentence if it was correct. Do not wrap in quotes or add extra introductory words.]"""

start = time.time()
print("Sending request to Ollama...")
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False
    },
    timeout=120
)
duration = time.time() - start
print(f"Completed in {duration:.2f} seconds.")
print("=== Response ===")
print(response.json().get("response"))
