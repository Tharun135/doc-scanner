import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # or your preferred model

def generate_rewrite(
    sentence: str, 
    rule_id: str, 
    rule_description: str, 
    heading_context: str = "", 
    block_type: str = ""
) -> str:
    """
    Generate an AI rewrite for a flagged sentence using the Siemens IX Style Guide prompt structure.
    Returns ONLY the rewritten sentence without explanation.
    """
    prompt = f"""You are a technical writing assistant enforcing the Siemens IX Style Guide.

Section: {heading_context}
Block type: {block_type}
Rule violated: {rule_id} — {rule_description}

Original sentence:
"{sentence}"

Rewrite this sentence to fix the violation. Follow these constraints:
- Max 20 words
- Active voice with identified actor
- Present simple tense
- No banned words
- Match the block type context

Return ONLY the rewritten sentence. No explanation."""

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            rewritten = result.get("response", "").strip()
            # Clean up potential markdown formatting or quotes
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1]
            return rewritten
    except Exception as e:
        logger.error(f"Failed to generate rewrite from Ollama: {e}")
        
    return ""
