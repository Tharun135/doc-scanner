from app.advanced_retrieval import create_retriever, retrieve_for_writing_feedback
query = "Passive voice detected Rockwell's Studio 5000"
r = create_retriever()
res = retrieve_for_writing_feedback(query, r)
for x in res:
    print(x.content)
