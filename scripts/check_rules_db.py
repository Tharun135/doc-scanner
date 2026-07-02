import chromadb
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check_rules")

def check_rules():
    # Path relative to app/
    persist_path = os.path.join(os.getcwd(), 'docscanner_rules_db')
    print(f"Checking rules in: {persist_path}")
    
    if not os.path.exists(persist_path):
        print("❌ Rules database directory does not exist.")
        return

    client = chromadb.PersistentClient(path=persist_path)
    
    try:
        collection = client.get_collection(name="rule_remediations")
        count = collection.count()
        print(f"✅ Found rule_remediations collection with {count} rules.")
        
        if count > 0:
            results = collection.get(limit=5)
            print("\nPreview of first 5 rules:")
            for i, rule_id in enumerate(results['ids']):
                print(f"{i+1}. {rule_id}")
    except Exception as e:
        print(f"❌ Error accessing collection: {e}")

if __name__ == "__main__":
    check_rules()
