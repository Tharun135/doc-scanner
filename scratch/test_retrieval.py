from app.advanced_retrieval import AdvancedRetriever
r = AdvancedRetriever()
res = r.search_by_source_type("Passive voice detected Rockwell's Studio 5000 or RSLogix 5000 software is installed and available on an Engineering PC.", "style_guide", n_results=1)
for x in res:
    print(x.relevance_score, x.content[:50])
