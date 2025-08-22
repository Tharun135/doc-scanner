import os
import json
import argparse
import chromadb

def main(path, collection_name="docscanner_solutions", reset=False):
    # Resolve Chroma path (env override supported)
    chroma_path = os.getenv("DOCSCANNER_CHROMA_PATH", "./chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)

    # Reset collection if requested
    try:
        if reset and collection_name in [c.name for c in client.list_collections()]:
            client.delete_collection(collection_name)
    except Exception:
        pass

    # Get or create collection
    try:
        col = client.get_collection(collection_name)
    except Exception:
        col = client.create_collection(collection_name)

    # Load data
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids, docs, metas = [], [], []

    for i, row in enumerate(data, start=1):
        rid = str(row.get("rule_id", f"rule-{i}"))  # Chroma IDs should be strings

        # Document body to embed/search (keep metadata smaller)
        doc = (
            (row.get("solution") or "")
            + "\n\nWhy:\n" + (row.get("explanation") or "")
            + "\n\nReferences:\n" + (row.get("reference") or "")
        )

        # FLAT metadata only: str/int/float/bool/None
        meta = {}
        for k, v in row.items():
            # These large fields are already included in `doc`
            if k in ("solution", "explanation", "reference"):
                continue
            if isinstance(v, (str, int, float, bool)) or v is None:
                meta[k] = v
            else:
                # Flatten dicts/lists (e.g., rewrite_policy, templates, few_shot)
                meta[k] = json.dumps(v, ensure_ascii=False)

        ids.append(rid)
        docs.append(doc)
        metas.append(meta)

    col.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Loaded {len(ids)} items into '{collection_name}' at {chroma_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        required=True,
        help="Path to docscanner_solutions_enriched_with_policy.json"
    )
    parser.add_argument("--collection", default="docscanner_solutions")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    main(args.data, args.collection, args.reset)
