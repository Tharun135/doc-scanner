"""
Shadow Mode Drift Analysis

Analyzes telemetry logs to detect system drift and instability.
Measures stability, not improvement.

Run daily to monitor:
- Rewrite rate drift
- Justification distribution skew
- New trigger appearance (governance breach)
"""

import json
from collections import Counter
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any


def analyze_shadow_logs(log_path: Path = None) -> Dict[str, Any]:
    """
    Analyze shadow mode telemetry logs.
    
    Returns:
        Dictionary with drift metrics
    """
    if log_path is None:
        log_path = Path(__file__).parent / "rewrite_shadow_log.jsonl"
    
    if not log_path.exists():
        return {
            "error": "No telemetry data found",
            "log_path": str(log_path)
        }
    
    total_evaluations = 0
    attempts = 0
    applied = 0
    allowed = 0
    justifications = Counter()
    docs_processed = set()
    
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                total_evaluations += 1
                docs_processed.add(record["doc_id"])
                
                if record["rewrite_attempt"]:
                    attempts += 1
                
                if record["rewrite_applied"]:
                    applied += 1
                    if record["justification"]:
                        justifications[record["justification"]] += 1
                
                if record["rewrite_allowed"]:
                    allowed += 1
            
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON line: {e}")
                continue
    
    # Calculate rates
    attempt_rate = (attempts / total_evaluations * 100) if total_evaluations > 0 else 0
    applied_rate = (applied / total_evaluations * 100) if total_evaluations > 0 else 0
    allowed_rate = (allowed / total_evaluations * 100) if total_evaluations > 0 else 0
    
    # Justification distribution
    justification_dist = dict(justifications.most_common())
    
    # Check for justification skew (single type dominance)
    max_justification_count = max(justifications.values()) if justifications else 0
    justification_skew = (max_justification_count / applied * 100) if applied > 0 else 0
    
    return {
        "total_evaluations": total_evaluations,
        "documents_processed": len(docs_processed),
        "attempt_rate_pct": round(attempt_rate, 2),
        "applied_rate_pct": round(applied_rate, 2),
        "allowed_rate_pct": round(allowed_rate, 2),
        "total_attempts": attempts,
        "total_applied": applied,
        "justification_distribution": justification_dist,
        "justification_skew_pct": round(justification_skew, 2),
        "max_justification": justifications.most_common(1)[0] if justifications else None,
    }


def check_drift_alarms(metrics: Dict[str, Any]) -> Dict[str, str]:
    """
    Check metrics against drift alarm thresholds.
    
    Thresholds:
    - Attempt rate: Normal <12%, Warning 12-18%, Alarm >18%
    - Applied rate: Normal <8%, Warning 8-12%, Alarm >12%
    - Justification skew: Normal <80%, Warning 80-90%, Alarm >90%
    
    Returns:
        Dictionary of alarm statuses
    """
    alarms = {}
    
    attempt_rate = metrics.get("attempt_rate_pct", 0)
    applied_rate = metrics.get("applied_rate_pct", 0)
    justification_skew = metrics.get("justification_skew_pct", 0)
    
    # Attempt rate alarm
    if attempt_rate > 18:
        alarms["attempt_rate"] = "ALARM"
    elif attempt_rate > 12:
        alarms["attempt_rate"] = "WARNING"
    else:
        alarms["attempt_rate"] = "NORMAL"
    
    # Applied rate alarm
    if applied_rate > 12:
        alarms["applied_rate"] = "ALARM"
    elif applied_rate > 8:
        alarms["applied_rate"] = "WARNING"
    else:
        alarms["applied_rate"] = "NORMAL"
    
    # Justification skew alarm
    if justification_skew > 90:
        alarms["justification_skew"] = "ALARM"
    elif justification_skew > 80:
        alarms["justification_skew"] = "WARNING"
    else:
        alarms["justification_skew"] = "NORMAL"
    
    return alarms


def print_report(metrics: Dict[str, Any], alarms: Dict[str, str]) -> None:
    """Print human-readable drift report."""
    print("=" * 60)
    print("SHADOW MODE DRIFT ANALYSIS")
    print(f"Generated: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    if "error" in metrics:
        print(f"ERROR: {metrics['error']}")
        return
    
    print(f"\nTotal Evaluations: {metrics['total_evaluations']}")
    print(f"Documents Processed: {metrics['documents_processed']}")
    
    print(f"\n--- REWRITE RATES ---")
    print(f"Attempt Rate: {metrics['attempt_rate_pct']}% [{alarms.get('attempt_rate', 'N/A')}]")
    print(f"Applied Rate: {metrics['applied_rate_pct']}% [{alarms.get('applied_rate', 'N/A')}]")
    print(f"Allowed Rate: {metrics['allowed_rate_pct']}%")
    
    print(f"\n--- JUSTIFICATION DISTRIBUTION ---")
    for justification, count in metrics['justification_distribution'].items():
        pct = (count / metrics['total_applied'] * 100) if metrics['total_applied'] > 0 else 0
        print(f"  {justification}: {count} ({pct:.1f}%)")
    
    print(f"\n--- DRIFT INDICATORS ---")
    print(f"Justification Skew: {metrics['justification_skew_pct']}% [{alarms.get('justification_skew', 'N/A')}]")
    if metrics.get('max_justification'):
        print(f"Dominant Trigger: {metrics['max_justification'][0]} ({metrics['max_justification'][1]} occurrences)")
    
    print("\n--- ALARM SUMMARY ---")
    has_alarms = any(status in ["WARNING", "ALARM"] for status in alarms.values())
    if has_alarms:
        print("⚠️  DRIFT DETECTED")
        for metric, status in alarms.items():
            if status != "NORMAL":
                print(f"  {metric}: {status}")
    else:
        print("✓ System stable - no drift detected")
    
    print("=" * 60)


def main():
    """Run drift analysis and print report."""
    metrics = analyze_shadow_logs()
    alarms = check_drift_alarms(metrics)
    print_report(metrics, alarms)


if __name__ == "__main__":
    main()
