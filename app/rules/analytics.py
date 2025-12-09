"""
Rule Analytics Module
Track rule violations and provide insights.
"""
import json
import os
from datetime import datetime
from collections import defaultdict

class RuleAnalytics:
    def __init__(self, db_path="rule_analytics.json"):
        self.db_path = db_path
        self.data = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {
            "violations": {},  # rule_id -> count
            "documents": {},   # doc_name -> violations
            "history": []      # timestamped entries
        }
    
    def record_violation(self, rule_id, document_name):
        """Record a rule violation."""
        if rule_id not in self.data["violations"]:
            self.data["violations"][rule_id] = 0
        self.data["violations"][rule_id] += 1
        
        if document_name not in self.data["documents"]:
            self.data["documents"][document_name] = {}
        if rule_id not in self.data["documents"][document_name]:
            self.data["documents"][document_name][rule_id] = 0
        self.data["documents"][document_name][rule_id] += 1
        
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_id,
            "document": document_name
        })
        
        self._save_data()
    
    def _save_data(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_top_violations(self, limit=10):
        """Get most frequently violated rules."""
        sorted_violations = sorted(
            self.data["violations"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_violations[:limit]
    
    def get_document_stats(self, document_name):
        """Get violation stats for a specific document."""
        return self.data["documents"].get(document_name, {})
    
    def get_summary(self):
        """Get overall analytics summary."""
        total_violations = sum(self.data["violations"].values())
        total_docs = len(self.data["documents"])
        
        return {
            "total_violations": total_violations,
            "total_documents": total_docs,
            "unique_rules_violated": len(self.data["violations"]),
            "avg_violations_per_doc": total_violations / total_docs if total_docs > 0 else 0,
            "top_violations": self.get_top_violations(5)
        }
