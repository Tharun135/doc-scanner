import json
import chromadb
from chromadb.utils import embedding_functions

# 1) Configure Chroma (persistent storage)
client = chromadb.PersistentClient(path="./chroma")

# 2) Choose an embedding function (local SentenceTransformer example)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3) Create or get the collection
collection = client.get_or_create_collection(
    name="docscanner_rules",
    embedding_function=embed_fn,
    metadata={"hnsw:space": "cosine"}
)

# 4) Read JSONL and upsert
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

docs, ids, metadatas = [], [], []


def ingest_jsonl_file(jsonl_path):
    for entry in load_jsonl(jsonl_path):
        doc = "\n".join([
            f"Rule: {entry['rule_name']}",
            f"Intent: {entry.get('intent','')}",
            f"Guidance: {entry.get('guidance','')}",
            f"Steps: {', '.join(entry.get('transformation_steps', []))}",
            f"Signals: {', '.join(entry.get('detection_signals', [])) if 'detection_signals' in entry else ''}",
            f"Bad: {entry.get('bad_example','')}",
            f"Good: {' | '.join(entry.get('good_examples', []))}",
            f"Tags: {', '.join(entry.get('tags', []))}"
        ])
        docs.append(doc)
        ids.append(entry["id"])
        import json
        def serialize_list(val):
            if all(isinstance(item, str) for item in val):
                return "; ".join(val)
            else:
                return json.dumps(val, ensure_ascii=False)
        meta = {k: (serialize_list(v) if isinstance(v, list) else v) for k, v in entry.items()}
        metadatas.append(meta)

# Ingest both files (or just one if you want)
for jsonl_file in ["rules_split_sentences.jsonl", "rules_passive_voice.jsonl", "rules_adverbs.jsonl"]:
    ingest_jsonl_file(jsonl_file)

# Upsert (add or update)
collection.upsert(documents=docs, ids=ids, metadatas=metadatas)

print(f"Upserted {len(ids)} rules into collection 'docscanner_rules'.")
