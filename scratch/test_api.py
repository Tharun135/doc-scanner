import requests
import json

payload = {
    'text': "Rockwell's Studio 5000 or RSLogix 5000 software is installed and available on an Engineering PC.",
    'issue': {'issue_type': 'Passive voice detected', 'reviewer_rationale': 'Actor unclear'},
    'feedback': 'Passive voice detected'
}

resp = requests.post('http://127.0.0.1:5005/ai_suggestion', json=payload)
print(json.dumps(resp.json(), indent=2))
