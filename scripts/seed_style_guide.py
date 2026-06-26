"""
seed_style_guide.py
Populates the ChromaDB knowledge base with Technical-style technical writing rules.
Run this once (or whenever you update the rules) from the project root:
    python scripts/seed_style_guide.py
"""

import sys
import os
import json

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

STYLE_GUIDE_RULES = [
    # -----------------------------------------------------------------------
    # LONG SENTENCES
    # -----------------------------------------------------------------------
    {
        "id": "sg-length-001",
        "text": (
            "Rule: Keep sentences under 25 words. Split long sentences at conjunctions (and, then, or).\n"
            "Bad:  'You can select a file with the datapoints from the TIA Portal and export it from the TIA Portal.'\n"
            "Good: 'Select a file with the data points from the TIA Portal. Export the file from the TIA Portal.'"
        ),
        "metadata": {"category": "long_sentence", "severity": "high", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },
    
    # -----------------------------------------------------------------------
    # PASSIVE VOICE
    # -----------------------------------------------------------------------
    {
        "id": "sg-passive-001",
        "text": (
            "Rule: Avoid passive voice. Use active voice with simple present tense.\n"
            "Bad:  'The tags are imported by the application.'\n"
            "Good: 'The application imports the tags.'\n"
            "Bad:  'The dialog box is displayed.'\n"
            "Good: 'The dialog box appears.' or 'The application displays the dialog box.'"
        ),
        "metadata": {"category": "passive_voice", "severity": "high", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },
    {
        "id": "sg-passive-002",
        "text": (
            "Rule: Use 'you' as the subject of active voice sentences in user instructions.\n"
            "Bad:  'The settings are configured by the user.'\n"
            "Good: 'You configure the settings.'\n"
            "Bad:  'The device is connected to the network by the technician.'\n"
            "Good: 'You connect the device to the network.'"
        ),
        "metadata": {"category": "passive_voice", "severity": "high", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },

    # -----------------------------------------------------------------------
    # TECHNICAL TERMINOLOGY AND BRANDING
    # -----------------------------------------------------------------------
    {
        "id": "sg-technical-001",
        "text": (
            "Rule: Use correct Technical product nomenclature.\n"
            "Standard: 'TIA Portal' (Not TIA-Portal or TIAporto)\n"
            "Standard: 'SIMATIC S7-300' (Include the series number)\n"
            "Standard: 'Industrial Edge' (Not Industry Edge)\n"
            "Standard: 'Common Connector' (Capitalized when referring to the product)"
        ),
        "metadata": {"category": "branding", "severity": "high", "source": "Technical Branding", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },
    {
        "id": "sg-technical-002",
        "text": (
            "Rule: Preserve software version numbers exactly.\n"
            "Example: 'TIA Portal v17', 'Industrial Edge v1.5'.\n"
            "Do not round 'v1.5' to 'v1' or 'v2'. Do not remove the 'v'."
        ),
        "metadata": {"category": "technical_accuracy", "severity": "critical", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },

    # -----------------------------------------------------------------------
    # SAFETY AND HALLUCINATION PREVENTION
    # -----------------------------------------------------------------------
    {
        "id": "sg-safety-001",
        "text": (
                "Rule: Never add new procedural steps that were not in the original text.\n"
                "Original: 'Open the menu and select Export.'\n"
                "Allowed Rewrite: 'Open the menu. Select Export.'\n"
                "Forbidden Rewrite: 'Open the menu. Click the blue button then select Export.'"
        ),
        "metadata": {"category": "hallucination_prevention", "severity": "critical", "source": "Safety Policy", "source_type": "style_guide", "meta_source_type": "style_guide"}
    }
]

def load_json_rules():
    """Dynamically loads rules from app/rules/rules.json to ensure 100% RAG alignment."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "rules", "rules.json")
    if not os.path.exists(json_path):
        return []
        
    with open(json_path, 'r', encoding='utf-8') as f:
        json_rules = json.load(f)
        
    dynamic_rules = []
    for r in json_rules:
        text = f"Rule: {r['message']}\n"
        if r.get('suggestion'):
            text += f"Guidance: {r['suggestion']}\n"
        if r.get('example_violation') and r.get('example_correction'):
            text += f"Bad: '{r['example_violation']}'\n"
            text += f"Good: '{r['example_correction']}'"
            
        dynamic_rules.append({
            "id": f"sg-json-{r['rule_id']}",
            "text": text.strip(),
            "metadata": {
                "category": r['category'],
                "severity": r['severity'],
                "source": "Technical Style Guide",
                "source_type": "style_guide",
                "meta_source_type": "style_guide"
            }
        })
    return dynamic_rules

def seed_chromadb():
    """Seed all style guide rules into ChromaDB."""
    try:
        from app.chromadb_fix import get_chromadb_client, get_or_create_collection

        client = get_chromadb_client()
        collection = get_or_create_collection(client, "docscanner_knowledge")

        existing_count = collection.count()
        print(f"Existing documents in collection: {existing_count}")

        # Combine hardcoded rules with dynamically loaded JSON rules
        all_rules = STYLE_GUIDE_RULES + load_json_rules()

        # Upsert all rules
        ids = [r["id"] for r in all_rules]
        documents = [r["text"] for r in all_rules]
        metadatas = [r["metadata"] for r in all_rules]

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        new_count = collection.count()
        print(f"Seeding complete! Total in DB: {new_count}")

    except Exception as e:
        print(f"Error seeding ChromaDB: {e}")
        raise

if __name__ == "__main__":
    print("Seeding Technical Style Guide rules into ChromaDB...")
    seed_chromadb()
