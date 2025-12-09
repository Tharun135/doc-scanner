# scripts/test_retrieval.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.solutions_service import retrieve_solution, retrieve_top_solutions_robust

print("Testing retrieval...")
print(retrieve_solution("avoid passive voice"))
print(retrieve_top_solutions_robust("procedural steps"))
