import json
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.services.rag_service import generate_suggestion

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def evaluate_system():
    # Evaluation Dataset
    dataset = [
        {
            "sentence": "The login button is clicked by the user.",
            "issue_type": "passive_voice",
            "expected": "Click the login button."
        },
        {
            "sentence": "It is recommended that the server should be restarted by the administrator.",
            "issue_type": "passive_voice",
            "expected": "The administrator should restart the server."
        },
        {
            "sentence": "In order to ensure that the system functions correctly, it is necessary to apply the latest patch.",
            "issue_type": "long_sentence",
            "expected": "Apply the latest patch to ensure correct system function."
        }
    ]

    model = SentenceTransformer('all-MiniLM-L6-v2')
    results = []
    
    print("Starting Evaluation...\n" + "-"*40)
    for data in dataset:
        print(f"Testing: '{data['sentence']}'")
        
        # Generate prediction
        response = generate_suggestion(data['sentence'], data['issue_type'])
        predicted = response.get('suggestion', '')
        
        # Calculate similarity
        expected_emb = model.encode(data['expected'])
        predicted_emb = model.encode(predicted)
        
        similarity = cosine_similarity(expected_emb, predicted_emb)
        
        print(f"Expected : {data['expected']}")
        print(f"Predicted: {predicted}")
        print(f"Score    : {similarity:.4f}\n")
        
        results.append({
            "sentence": data['sentence'],
            "score": similarity
        })
        
    avg_score = np.mean([r['score'] for r in results])
    print(f"Average System Score: {avg_score:.4f}")
    
if __name__ == '__main__':
    evaluate_system()
