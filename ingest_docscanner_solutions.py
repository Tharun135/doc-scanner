import json, chromadb, argparse
from chromadb.utils import embedding_functions

def main(path, collection_name="docscanner_solutions", reset=False):
    client = chromadb.PersistentClient(path="./chroma_db")
    if reset and collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(collection_name)
    try:
        col = client.get_collection(collection_name)
    except Exception:
        col = client.create_collection(collection_name)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ids = []
    docs = []
    metas = []
    for i, row in enumerate(data, start=1):
        ids.append(row.get("rule_id", f"rule-{i}"))
        docs.append(row["solution"] + "\n\nWhy:\n" + row["explanation"] + "\n\nReferences:\n" + row.get("reference",""))
        meta = row.copy()
        metas.append(meta)
    col.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Loaded {len(ids)} items into '{collection_name}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to docscanner_solutions_enriched.json")
    parser.add_argument("--collection", default="docscanner_solutions")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    main(args.data, args.collection, args.reset)
