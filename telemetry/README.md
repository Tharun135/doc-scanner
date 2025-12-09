# Shadow Mode - Phase 2 Deployment

## Purpose

Observe rewrite system behavior in production without exposing rewrites to users.
This is **drift detection**, not feature rollout.

## What Shadow Mode Does

- ✅ Runs semantic analysis on all uploaded documents
- ✅ Evaluates rewrite eligibility (eligibility + justification gates)
- ✅ Logs all rewrite decisions to telemetry
- ❌ Does NOT apply rewrites to document output
- ❌ Does NOT display suggestions to users
- ❌ Does NOT expose UI controls

## Telemetry Data

**Location:** `telemetry/rewrite_shadow_log.jsonl`

**Format:** One JSON object per line (append-only)

**Example:**
```json
{"timestamp": "2025-12-09T10:30:45", "doc_id": "manual.pdf", "idx": 42, "rewrite_attempt": true, "rewrite_allowed": true, "rewrite_applied": true, "justification": "passive_referent_unclear"}
```

**Privacy:** No text content stored. Triggers only.

## Monitoring

### Daily Check
Run drift analysis daily:
```bash
python telemetry/analyze_shadow_drift.py
```

Or schedule with Windows Task Scheduler:
```bash
telemetry/daily_check.bat
```

### Output
```
SHADOW MODE DRIFT ANALYSIS
Total Evaluations: 500
Documents Processed: 12
Attempt Rate: 6.2% [NORMAL]
Applied Rate: 4.8% [NORMAL]
Justification Distribution:
  passive_referent_unclear: 18 (75%)
  vague_quantifier: 6 (25%)
Justification Skew: 75% [NORMAL]
✓ System stable - no drift detected
```

## Alarm Thresholds

| Metric | Normal | Warning | Alarm |
|--------|--------|---------|-------|
| Attempt Rate | <12% | 12-18% | >18% |
| Applied Rate | <8% | 8-12% | >12% |
| Justification Skew | <80% | 80-90% | >90% |
| New Justification | 0% | 0% | >0% |

## Interpretation

### Stable System
- Rewrite rate: 3-10%
- No single trigger > 80%
- Consistent across documents
- → Proceed to Phase 3

### Unstable System
- Rate > 15% on any doc
- Rate < 2% consistently
- Single trigger > 90%
- → Investigate, do not expand

### Domain Variance
- Different rates per product line
- Acceptable if consistent within domain
- May indicate author training need

## What to Do

### During Shadow Mode (2 Weeks Minimum)
1. Process documents normally
2. Run daily drift analysis
3. Observe metrics
4. Do NOT intervene unless critical alarm

### What NOT to Do
- ❌ Show rewrites to authors
- ❌ Add UI controls
- ❌ Tune gates based on early data
- ❌ Add new triggers
- ❌ Market as feature
- ❌ Create dashboards

## Phase Transition

**Current:** Phase 2 (Shadow Mode)

**Next:** Phase 3 (Visible UI, disabled controls) - Only after:
- 14+ days observation
- 500+ sentences evaluated
- <10% day-over-day variance
- <1% justification deviation

## Files

```
telemetry/
  shadow_logger.py           # Telemetry logging
  analyze_shadow_drift.py    # Drift analysis script
  daily_check.bat            # Scheduled monitoring
  rewrite_shadow_log.jsonl   # Telemetry data (append-only)
  daily_report.txt           # Latest analysis output
```

## Current Status

**Phase:** 2 (Shadow Mode - Observation Only)  
**User Exposure:** None  
**Rewrite Application:** Disabled  
**UI Visibility:** Hidden  
**Duration:** 2 weeks minimum  
**Goal:** Stability validation

---

**This is drift surveillance, not edit scoring.**
