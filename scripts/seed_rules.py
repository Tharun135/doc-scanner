# scripts/seed_rules.py
import sys, os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vectorstore import upsert_rules, get_store

rules = [
    {
        "id": "rule-001",
        "text": "Avoid passive voice. Prefer active constructions in all sentences.",
        "metadata": {"category": "style", "severity": "high"},
    },
    {
        "id": "rule-002",
        "text": "Use imperative verbs for procedural steps. Example: 'Click Save'.",
        "metadata": {"category": "style", "severity": "medium"},
    },
    {
        "id": "rule-003",
        "text": "Do not use future tense when describing user actions. Use simple present.",
        "metadata": {"category": "style"},
    },
]

print("Seeding rules into Chroma...")
upsert_rules(rules)

store = get_store()
print(f"Collection count: {store.count()}")
print("Done ✅")
