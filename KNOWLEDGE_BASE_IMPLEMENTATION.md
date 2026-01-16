# Knowledge Base Building System

**From Theory to Execution** - A practical implementation of a decision-focused RAG system for DocScanner.

## What This Is

This system converts your writing rules, rewrite history, and writing patterns into a **properly structured knowledge base** for your RAG system. No more document-style chunking. Every chunk answers a specific question.

## Quick Start

### 1. Build the Knowledge Base

```powershell
python build_knowledge_base.py
```

This generates `data/knowledge_base.json` containing all your decision chunks.

**Expected output:**
- ✅ 60+ rule chunks (10 rules × 6 chunks each)
- ✅ 30+ example chunks (10 rewrites × 3 chunks each)
- ✅ 100+ negative knowledge chunks (what NOT to rewrite)
- ✅ 50+ pattern chunks (structural writing patterns)
- **Total: 240+ chunks** (baseline)

### 2. Evaluate Quality

```powershell
python evaluate_knowledge_base.py
```

This runs your test cases and reports:
- Hit rate (% of queries that retrieve correct rule)
- Retrieval score (quality of top-k results)
- Rewrite decision accuracy

**Target: 70%+ hit rate**

### 3. Index to Vector Store

Once you have validated chunks, index them:

```python
from app.services.vectorstore import index_chunks
import json

with open('data/knowledge_base.json', 'r') as f:
    kb = json.load(f)
    chunks = kb['chunks']
    index_chunks(chunks)
```

## System Architecture

```
chunk_factory/
├── rule_chunks.py        # Converts rules → 6 chunks each
├── example_chunks.py     # Mines rewrite history → examples
├── exception_chunks.py   # Negative knowledge (what NOT to do)
└── pattern_chunks.py     # Structural writing patterns

app/
└── decision_chunk.py     # Core DecisionChunk schema

build_knowledge_base.py   # Main orchestrator
evaluate_knowledge_base.py # Quality metrics
```

## The DecisionChunk Schema

Every chunk MUST have:

```python
DecisionChunk(
    id: str,              # Unique identifier
    title: str,           # Human-readable title
    question: str,        # THE question this chunk answers
    answer: str,          # Complete, self-contained answer (<200 words)
    knowledge_type: str,  # rule|example|exception|pattern|negative
    rule_id: str,         # Associated rule (if applicable)
    rewrite_allowed: bool,# Can this trigger a rewrite?
    severity: str,        # low|medium|high|critical
    doc_type: str,        # manual|api|safety|ui|legal|pattern
)
```

**Critical constraints:**
1. Answer must be < 200 words
2. Question + Answer must be self-contained
3. All metadata fields are mandatory

## How to Scale to 500+ Chunks

### Current Status (Baseline)

- ✅ 10 rules defined with 6 chunks each = 60 chunks
- ✅ 10 rewrite examples with 3 chunks each = 30 chunks  
- ✅ 20+ negative knowledge categories = 100+ chunks
- ✅ 8 pattern categories = 50+ chunks
- **Total: ~240 chunks**

### Path to 500 Chunks

1. **Add 17 more rules** (27 total)
   - Current: 10 rules
   - Target: 27 rules
   - Each rule generates 6 chunks
   - Adds: 17 × 6 = **+102 chunks**
   - **New total: 342 chunks**

2. **Mine 30 more rewrite examples** (40 total)
   - Current: 10 examples
   - Target: 40 examples
   - Each generates 3 chunks
   - Adds: 30 × 3 = **+90 chunks**
   - **New total: 432 chunks**

3. **Add 10 more negative knowledge items**
   - Adds: **+30-40 chunks**
   - **New total: 462-472 chunks**

4. **Add 2 more pattern categories**
   - Adds: **+20-30 chunks**
   - **New total: 482-502 chunks** ✅ **TARGET REACHED**

### Path to 1000 Chunks (Maximum Quality)

Continue scaling:
- 90+ rewrite examples = **+150 chunks** (total: 270)
- Full negative knowledge library = **+100 chunks** (total: 200)
- Complete pattern library = **+50 chunks** (total: 150)
- Rule expansion to 50 rules = **+138 chunks** (total: 300)

**Total: ~800-1000 chunks**

## Key Files to Modify

### Adding Rules

Edit `chunk_factory/rule_chunks.py`:

```python
RULE_DEFINITIONS = {
    "YOUR_NEW_RULE": {
        "name": "Rule Name",
        "definition": "What is this rule?",
        "why_matters": "Why should users care?",
        "severity": "medium",
        "detection": "How is it detected?",
        "exceptions": "When NOT to apply?",
        "rewrite_example": {
            "before": "...",
            "after": "...",
            "why": "..."
        }
    }
}
```

### Adding Rewrite Examples

Edit `chunk_factory/example_chunks.py`:

```python
REWRITE_EXAMPLES.append({
    "id": "rewrite_XXX",
    "rule_id": "RULE_NAME",
    "before": "Original text",
    "after": "Corrected text",
    "justification": "Why changed",
    "context": "Where used"
})
```

### Adding Negative Knowledge

Edit `chunk_factory/exception_chunks.py`:

```python
NEGATIVE_KNOWLEDGE.append({
    "context": "What NOT to rewrite",
    "forbidden_action": "Specific action to avoid",
    "reason": "Why forbidden",
    "doc_type": "ui|legal|safety",
    "severity": "critical",
    "examples": ["Example 1", "Example 2"]
})
```

### Adding Patterns

Edit `chunk_factory/pattern_chunks.py`:

```python
STRUCTURAL_PATTERNS.append({
    "pattern_name": "Pattern Name",
    "category": "category",
    "chunks": [
        {
            "question": "When to use X?",
            "answer": "Use X when..."
        }
    ]
})
```

## Health Monitoring

After running `build_knowledge_base.py`, check:

```
Health Status: UNDERFED | HEALTHY | NOISY

UNDERFED (< 500 chunks):
  ⚠️  Add more examples, rules, or patterns

HEALTHY (500-1200 chunks):
  ✅ Optimal size for retrieval

NOISY (> 1200 chunks):
  ⚠️  Consider pruning redundant chunks
```

## Evaluation Metrics

Target thresholds:

| Metric | Target | Meaning |
|--------|--------|---------|
| Hit Rate | ≥ 70% | Correct rule in top-3 retrievals |
| Avg Retrieval Score | ≥ 0.7 | Quality of ranking |
| Rewrite Accuracy | ≥ 90% | Correct rewrite_allowed flag |

**If hit rate < 70%:**
1. Chunks are too generic
2. Questions don't match user queries
3. Need more specific examples

**Fix:**
- Make questions more specific
- Add more rewrite examples
- Improve answer quality

## Integration with Existing RAG

To use these chunks in your current RAG system:

```python
# In your retrieval code
from app.decision_chunk import DecisionChunk
import json

# Load chunks
with open('data/knowledge_base.json', 'r') as f:
    kb = json.load(f)

# Index to ChromaDB (or your vector store)
for chunk_data in kb['chunks']:
    chunk = DecisionChunk(**chunk_data)
    
    # Embed the question + answer
    text = chunk.get_embedding_text()
    embedding = embed(text)
    
    # Index with metadata for filtering
    vectorstore.add(
        embedding=embedding,
        metadata=chunk.get_metadata_for_filtering(),
        document=text,
        id=chunk.id
    )
```

## Next Steps

1. **Run the baseline build**
   ```powershell
   python build_knowledge_base.py
   ```

2. **Check you have ~240 chunks**

3. **Add your missing rules** (you mentioned 27 total, we have 10)
   - Edit `chunk_factory/rule_chunks.py`
   - Add 17 more rule definitions

4. **Run build again**
   ```powershell
   python build_knowledge_base.py
   ```

5. **You should now have ~342 chunks**

6. **Mine your actual rewrite history**
   - Export rewrites to JSON
   - Load in `example_chunks.py`
   - Regenerate

7. **Run evaluation**
   ```powershell
   python evaluate_knowledge_base.py
   ```

8. **Integrate with vector store**

9. **Set up nightly builds** (optional)
   ```powershell
   # Add to cron/task scheduler
   python build_knowledge_base.py
   python evaluate_knowledge_base.py
   ```

## Hard Truths

1. **If chunks don't answer clear questions, retrieval will fail**
   - Bad: "Passive voice information"
   - Good: "When is a sentence considered passive voice?"

2. **If answers exceed 200 words, split the chunk**
   - One question = one chunk
   - Complex topics need multiple chunks

3. **If metadata is missing, filtering breaks**
   - Every chunk MUST have: knowledge_type, rewrite_allowed, severity, doc_type

4. **If you skip negative knowledge, you'll rewrite UI labels**
   - This is critical safety knowledge
   - 100+ chunks of "do NOT" is not overkill

5. **If hit rate stays below 70%, your chunks are wrong**
   - Not the model
   - Not the embeddings
   - The chunks are poorly designed

## Success Criteria

After implementing this system, you should see:

✅ **500+ properly structured chunks**
✅ **70%+ hit rate in evaluation**
✅ **Clear justifications for every rewrite suggestion**
✅ **No more rewriting UI labels or error codes**
✅ **Explainable RAG decisions** (you can see which chunk triggered what)

If you don't see these, **the chunks are wrong**, not the system.

---

## Questions?

The code is the documentation. Read:
1. `app/decision_chunk.py` - The schema
2. `chunk_factory/rule_chunks.py` - Example rule generation
3. `build_knowledge_base.py` - The orchestration

Everything else is details.

**Now execute.**
