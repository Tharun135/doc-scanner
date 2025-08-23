from app.services.enrichment import enrich_issue_with_solution
print(enrich_issue_with_solution(
    feedback="Avoid passive voice in procedural steps.",
    context="Once the status mapping is created and images uploaded...",
    top_k=3
))
