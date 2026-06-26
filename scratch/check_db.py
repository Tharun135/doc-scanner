import chromadb
client = chromadb.PersistentClient('./chroma_db')
collection = client.get_collection('docscanner_knowledge')
res = collection.get()
print('Total:', len(res['ids']))
print('Sources:', set([m.get('source') for m in res['metadatas'] if m]))
print('Source Types:', set([m.get('source_type') for m in res['metadatas'] if m]))
print('Meta Source Types:', set([m.get('meta_source_type') for m in res['metadatas'] if m]))
