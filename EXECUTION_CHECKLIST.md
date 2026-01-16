# EXECUTION CHECKLIST - Path to 500+ Chunks

**Status: 223/500 chunks (44.6% complete)**  
**Health: UNDERFED → Need real history**

---

## ✅ Phase 1: Foundation (COMPLETE)

- [x] Decision-centric schema with validation
- [x] Programmatic chunk factories
- [x] 60 rule chunks (10 rules × 6)
- [x] 30 synthetic example chunks
- [x] 96 negative knowledge chunks
- [x] 37 pattern chunks
- [x] Rewrite decision logger
- [x] History mining system
- [x] End-to-end demonstration

**Result**: 223 baseline chunks

---

## 🔄 Phase 2: Real Data Integration (IN PROGRESS)

### Step 1: Integrate Decision Logging ⏳

**Files to edit**:
- [ ] `app/app.py` - Add import: `from app.rewrite_decision_logger import get_history_logger, capture_rewrite_suggestion`
- [ ] `app/app.py` - Find `analyze_sentence()` or equivalent
- [ ] `app/app.py` - Wrap with logging (see `integration_template.py` lines 15-88)
- [ ] Your UI code - Wire Accept button to `log_user_response(decision_id, accepted=True, ...)`
- [ ] Your UI code - Wire Reject button to `log_user_response(decision_id, accepted=False, reason=...)`

**Test**:
```powershell
# Process one test document
# Check that data/rewrite_history.jsonl is created
# Should contain one line per decision
Get-Content data/rewrite_history.jsonl | Measure-Object -Line
```

**Time**: 2-3 hours

---

### Step 2: Collect Real Decisions ⏳

**Goal**: 100+ real rewrite decisions

**Process**:
1. [ ] Use DocScanner normally on 10-20 real documents
2. [ ] For each suggestion, user clicks Accept or Reject
3. [ ] If rejecting, capture reason (optional dropdown + text field)
4. [ ] All decisions auto-logged to `data/rewrite_history.jsonl`

**Documents to process**:
- [ ] Technical documentation (API docs, user guides)
- [ ] Internal documentation (specs, designs)
- [ ] UI text (help text, labels - should be rejected)
- [ ] Mixed content (procedures with code examples)

**Target**: 
- ~10 sentences per document
- ~2 issues per sentence average
- ~20 decisions per document
- **10 documents = 200 decisions**

**Time**: 1 week of normal usage

---

### Step 3: Mine Real History ⏳

**Command**:
```powershell
python mine_real_history.py
```

**Expected output**:
- Accepted examples: 60-120 chunks (3 per accepted decision)
- Rejected examples: 40-80 chunks (2 per rejected decision)
- Contextual patterns: 10-20 chunks
- Borderline cases: 10-20 chunks
- **Total**: 120-240 new chunks

**Result**: 223 + 150 = **~373 chunks**

**Time**: 5 minutes

---

### Step 4: Add Missing Rules ⏳

**Current**: 10 rules  
**Target**: 20-25 rules (not all 27 yet)

**Files to edit**:
- [ ] `chunk_factory/rule_chunks.py` - Add to `RULE_DEFINITIONS`

**Rules to add** (examples from your codebase):
1. [ ] TITLE_FORMATTING - Title case, sentence case
2. [ ] ACRONYM_DEFINITION - Define acronyms on first use
3. [ ] NUMBER_FORMATTING - Consistent number formatting
4. [ ] LIST_PARALLELISM - Parallel structure in lists
5. [ ] TABLE_FORMATTING - Table structure and headers
6. [ ] CODE_FORMATTING - Code block formatting
7. [ ] LINK_TEXT - Descriptive link text
8. [ ] CROSS_REFERENCE - How to reference other sections
9. [ ] IMAGE_ALT_TEXT - Alt text for images
10. [ ] HEADING_HIERARCHY - H1, H2, H3 structure

**Each rule generates 6 chunks**:
- Definition
- Why it matters
- Detection logic
- Exceptions
- Rewrite example
- Non-rewrite example

**10 rules × 6 = 60 chunks**

**Result**: 373 + 60 = **~433 chunks**

**Time**: 3-4 hours

---

### Step 5: Expand Negative Knowledge ⏳

**Current**: 22 categories, 96 chunks  
**Target**: +30 more company/project-specific categories

**File to edit**:
- [ ] `chunk_factory/exception_chunks.py` - Add to `NEGATIVE_KNOWLEDGE`

**Add project-specific negative knowledge**:
1. [ ] Your product names (exact spelling)
2. [ ] Your API endpoints (exact paths)
3. [ ] Your error codes (exact identifiers)
4. [ ] Your UI component names
5. [ ] Your configuration file names
6. [ ] Your command-line flags
7. [ ] Your environment variables
8. [ ] Your database table names
9. [ ] Your metric names
10. [ ] Your log message formats

**10 categories × 3 chunks avg = 30 chunks**

**Result**: 433 + 30 = **~463 chunks**

**Time**: 2 hours

---

### Step 6: Rebuild Knowledge Base ⏳

**Command**:
```powershell
python build_knowledge_base.py
```

**Expected**:
- Rule chunks: 120 (20 rules × 6)
- Example chunks: 150-240 (from real history)
- Negative chunks: 126 (42 categories)
- Pattern chunks: 37
- **Total**: 433-523 chunks

**Health Status**: Should show **HEALTHY** (500-1200)

**Time**: 30 seconds

---

## 🎯 Phase 3: Quality Verification (NEXT)

### Step 7: Integrate Real Retrieval ⏱️

**File to edit**:
- [ ] `evaluate_knowledge_base.py` line 209

**Replace**:
```python
def mock_retrieve(self, query: str, top_k: int = 3):
    # TODO: Replace with actual RAG
    mock_results = [...]
    return mock_results[:top_k]
```

**With**:
```python
def mock_retrieve(self, query: str, top_k: int = 3):
    from app.services.vectorstore import search_chunks
    return search_chunks(query, top_k=top_k)
```

**Requires**:
- [ ] Implement `app/services/vectorstore.py::search_chunks()`
- [ ] Index chunks to ChromaDB/Pinecone/Weaviate
- [ ] Return results in expected format

**Time**: 2-3 hours

---

### Step 8: Index to Vector Store ⏱️

**Create/edit**:
- [ ] `app/services/vectorstore.py` or similar

**Implementation**:
```python
import chromadb
from app.decision_chunk import DecisionChunk
import json

def index_knowledge_base():
    with open('data/knowledge_base.json', 'r') as f:
        kb = json.load(f)
    
    client = chromadb.Client()
    collection = client.get_or_create_collection("decision_chunks")
    
    for chunk_data in kb['chunks']:
        chunk = DecisionChunk(**chunk_data)
        collection.add(
            documents=[chunk.get_embedding_text()],
            metadatas=[chunk.get_metadata_for_filtering()],
            ids=[chunk.id]
        )

def search_chunks(query, top_k=3):
    client = chromadb.Client()
    collection = client.get_collection("decision_chunks")
    results = collection.query(query_texts=[query], n_results=top_k)
    
    return [
        {
            "rule_id": meta.get("rule_id", ""),
            "title": doc[:50],
            "score": 1.0 - dist,
            "rewrite_allowed": meta.get("rewrite_allowed", True)
        }
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )
    ]
```

**Time**: 2 hours

---

### Step 9: Run Evaluation ⏱️

**Command**:
```powershell
python evaluate_knowledge_base.py
```

**Expected metrics** (with real retrieval):
- Hit rate: 70-85% (up from 30% with mock)
- Avg retrieval score: 0.7-0.8
- Rewrite accuracy: 85-95%

**If < 70% hit rate**:
- [ ] Review `data/kb_evaluation_results.csv`
- [ ] Identify missed queries
- [ ] Add specific chunks for failed cases
- [ ] Rebuild and re-evaluate

**Time**: 10 minutes per run

---

### Step 10: Add Evaluation Test Cases ⏱️

**File to edit**:
- [ ] `data/kb_test_cases.csv`

**Add real queries from your usage**:
- [ ] 10 common rewrite scenarios
- [ ] 5 rejection scenarios (UI, legal, etc.)
- [ ] 5 borderline cases
- [ ] 5 pattern queries

**Format**:
```csv
query,expected_rule,should_rewrite,expected_severity,notes
"Fix this passive voice sentence","PASSIVE_VOICE","true","medium","Common case"
"UI button says 'Save'","UI_LABEL","false","critical","Must not rewrite"
```

**Time**: 1 hour

---

## 🚀 Phase 4: Production Readiness (FUTURE)

### Step 11: Continuous Improvement ⏱️

- [ ] Set up daily KB rebuild: `python build_knowledge_base.py`
- [ ] Set up daily evaluation: `python evaluate_knowledge_base.py`
- [ ] Set up weekly history mining: `python mine_real_history.py`
- [ ] Monitor hit rate trends in `data/kb_evaluation_metrics.json`
- [ ] Add test cases for any hit rate drops

**Time**: 2 hours to set up automation

---

### Step 12: Dashboard Integration ⏱️

- [ ] Display chunk provenance in UI (which chunk → which suggestion)
- [ ] Show confidence levels to users
- [ ] Track user feedback (helpful/not helpful)
- [ ] Feed feedback back into rewrite history

**Time**: 1-2 days

---

## Success Criteria

### Minimum Viable (Phase 2 Complete):
- ✅ 500+ total chunks
- ✅ 100+ from real history
- ✅ All chunks validated
- ✅ Decisions being logged
- ✅ Health status: HEALTHY

### Production Ready (Phase 3 Complete):
- ✅ 500+ chunks
- ✅ Real vector store integrated
- ✅ 70%+ hit rate
- ✅ 20+ evaluation test cases
- ✅ Rejections preventing false positives

### Fully Operational (Phase 4 Complete):
- ✅ Continuous mining pipeline
- ✅ Automated quality monitoring
- ✅ User feedback loop closed
- ✅ Dashboard metrics meaningful

---

## Time Estimates

### Optimistic (dedicated focus):
- Phase 2: 1 week
- Phase 3: 2 days
- **Total to production: 9 days**

### Realistic (part-time):
- Phase 2: 2-3 weeks
- Phase 3: 1 week
- **Total to production: 4 weeks**

### Conservative (with interruptions):
- Phase 2: 1 month
- Phase 3: 2 weeks
- **Total to production: 6 weeks**

---

## Current Blockers

None. All infrastructure is ready.

**Next immediate action**:
```powershell
# 1. Open app/app.py in editor
# 2. Find the analyze_sentence function
# 3. Copy integration pattern from integration_template.py
# 4. Test with one document
# 5. Verify data/rewrite_history.jsonl created
```

**That's it. Start there.**

---

## How to Track Progress

### Daily:
```powershell
# Check decision count
Get-Content data/rewrite_history.jsonl | Measure-Object -Line

# Current count: X decisions
# Target: 100+ decisions
```

### Weekly:
```powershell
# Mine history
python mine_real_history.py

# Rebuild KB
python build_knowledge_base.py

# Check chunk count in output
# Target: 500+ chunks
```

### Monthly:
```powershell
# Run evaluation
python evaluate_knowledge_base.py

# Check hit rate in output
# Target: 70%+ hit rate
```

---

## Questions?

This checklist maps directly to code:
1. ✅ Everything in Phase 1 is built
2. ⏳ Phase 2 needs your integration
3. ⏱️ Phase 3 needs your vector store
4. 🔮 Phase 4 is optimization

The hard part (architecture, validation, mining) is done.  
The remaining part is integration and data collection.

**Execute the checklist. One item at a time.**
