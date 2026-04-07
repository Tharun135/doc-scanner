"""
seed_style_guide.py
Populates the ChromaDB knowledge base with Siemens-style technical writing rules.
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
        "metadata": {"category": "passive_voice", "severity": "high", "source": "Siemens Style Guide"}
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
        "metadata": {"category": "passive_voice", "severity": "high", "source": "Siemens Style Guide"}
    },

    # -----------------------------------------------------------------------
    # WORDINESS AND CONCISENESS (Golden Pairs)
    # -----------------------------------------------------------------------
    {
        "id": "sg-concise-001",
        "text": (
            "Rule: Replace wordy phrases with simple alternatives.\n"
            "Bad:  'at this point in time' -> 'now'\n"
            "Bad:  'due to the fact that' -> 'because'\n"
            "Bad:  'in order to' -> 'to'\n"
            "Bad:  'with the purpose of' -> 'to'\n"
            "Bad:  'in the event that' -> 'if'\n"
            "Bad:  'perform an analysis' -> 'analyze'\n"
            "Bad:  'make a decision' -> 'decide'"
        ),
        "metadata": {"category": "conciseness", "severity": "medium", "source": "Siemens Style Guide"}
    },

    # -----------------------------------------------------------------------
    # SIEMENS TERMINOLOGY AND BRANDING
    # -----------------------------------------------------------------------
    {
        "id": "sg-siemens-001",
        "text": (
            "Rule: Use correct Siemens product nomenclature.\n"
            "Standard: 'TIA Portal' (Not TIA-Portal or TIAporto)\n"
            "Standard: 'SIMATIC S7-300' (Include the series number)\n"
            "Standard: 'Industrial Edge' (Not Industry Edge)\n"
            "Standard: 'Common Connector' (Capitalized when referring to the product)"
        ),
        "metadata": {"category": "branding", "severity": "high", "source": "Siemens Branding"}
    },
    {
        "id": "sg-siemens-002",
        "text": (
            "Rule: Preserve software version numbers exactly.\n"
            "Example: 'TIA Portal v17', 'Industrial Edge v1.5'.\n"
            "Do not round 'v1.5' to 'v1' or 'v2'. Do not remove the 'v'."
        ),
        "metadata": {"category": "technical_accuracy", "severity": "critical", "source": "Siemens Style Guide"}
    },

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
        "metadata": {"category": "long_sentence", "severity": "high", "source": "Siemens Style Guide"}
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
        "metadata": {"category": "hallucination_prevention", "severity": "critical", "source": "Safety Policy"}
    }
]

def seed_chromadb():
    """Seed all style guide rules into ChromaDB."""
    try:
        from app.chromadb_fix import get_chromadb_client, get_or_create_collection

        client = get_chromadb_client()
        collection = get_or_create_collection(client, "docscanner_knowledge")

        existing_count = collection.count()
        print(f"Existing documents in collection: {existing_count}")

        # Upsert all rules
        ids = [r["id"] for r in STYLE_GUIDE_RULES]
        documents = [r["text"] for r in STYLE_GUIDE_RULES]
        metadatas = [r["metadata"] for r in STYLE_GUIDE_RULES]

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
    print("Seeding Siemens Style Guide rules into ChromaDB...")
    seed_chromadb()
