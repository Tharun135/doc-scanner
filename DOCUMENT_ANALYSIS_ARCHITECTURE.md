# Two-Pass Document Analysis Architecture

## Implementation Complete ✅

DocScanner now implements a **two-pass document analysis architecture** that combines:

1. **PASS 0: Document-level understanding** (whole-manual reading)
2. **PASS 1: Sentence-level rule enforcement** (precise rewrites)
3. **PASS 2: Governance + rewrite decisions** (safe, explainable)

---

## What Was Added

### Core Components

#### 1. `core/document_context.py`
- **DocumentContext** dataclass capturing document-wide signals:
  - Document type (manual, API, safety, procedure, concept, reference)
  - Primary goal (instruct, explain, reference, warn)
  - Audience level (novice, intermediate, expert)
  - Rewrite sensitivity (low, medium, high, critical)
  - Forbidden sections/spans (safety, legal zones)
  - Terminology map and acronyms
  - Structure metadata (headings, sections, TOC)

#### 2. `core/document_analyzer.py`
- **DocumentAnalyzer** class with lightweight heuristics:
  - Document type detection
  - Forbidden zone identification
  - Terminology extraction
  - Acronym detection
  - Tense detection
  - Audience level detection
  - Structure analysis

#### 3. `core/document_rule.py`
- **DocumentRule** base class for document-level checks
- **Built-in rules:**
  - `ProcedureStructureRule` - checks for prerequisites, steps
  - `AcronymConsistencyRule` - detects undefined acronyms
  - `TerminologyConsistencyRule` - finds inconsistent terms
  - `TenseConsistencyRule` - detects mixed tenses
  - `DocumentCompletenessRule` - checks for missing sections
  - `SectionOrderRule` - validates logical section order

### Integration

#### Backend (`app/app.py`)
- PASS 0 runs **before** sentence extraction
- Document context flows into sentence analysis
- Document findings separate from rewrite suggestions
- API returns both sentence issues and document findings

#### Frontend (`app/templates/index.html`)
- **New "Document Analysis" tab** (third tab)
- Displays document context summary
- Shows document-level findings grouped by severity
- Separate from sentence-level rewrite suggestions

---

## How It Works

### Upload Flow

```
1. User uploads document
   ↓
2. PASS 0: Document Analysis
   - Extract headings, sections
   - Detect document type, goal, audience
   - Identify forbidden zones (safety, legal)
   - Extract terminology and acronyms
   - Run document-level rules
   ↓
3. PASS 1: Sentence Analysis (existing)
   - Split into sentences
   - Apply grammar/style rules
   - Document context available to rules
   ↓
4. Display Results
   - Issues Tab: sentence-level issues
   - AI Assistance Tab: AI suggestions
   - Document Analysis Tab: document-level findings ← NEW
```

### Document Context Usage

Document context **guides** sentence analysis without replacing it:

```python
# Example: Safety documents disable style rewrites
if document_context.doc_type == "safety":
    disable_style_rewrites()

# Example: Block rewrites in forbidden sections
if document_context.is_rewrite_allowed_at_position(position):
    apply_rewrite()
```

### Document Findings vs Sentence Issues

**Document Findings (PASS 0):**
- Do NOT trigger rewrites
- Provide structural guidance
- Examples:
  - "Missing Prerequisites Section"
  - "Undefined Acronyms: API, SDK, REST"
  - "Mixed Verb Tenses Detected"
  - "Unusual Section Order"

**Sentence Issues (PASS 1):**
- Trigger rewrite suggestions
- Examples:
  - "Passive voice detected"
  - "Long sentence (45 words)"
  - "Vague term: 'very'"

---

## Key Architectural Principles

### ✅ What We DID

1. **Lightweight heuristics** - No over-engineering, simple patterns
2. **Clean separation** - Document findings ≠ Rewrite suggestions
3. **Context flows down** - Document context guides sentences
4. **Sentence analysis preserved** - Existing rules unchanged
5. **Separate UI** - Document tab independent from issues

### ❌ What We DID NOT Do

1. ❌ Embed entire manual as one chunk
2. ❌ Let LLM rewrite whole sections
3. ❌ Remove sentence-level justification
4. ❌ Mix document feedback with rewrites
5. ❌ Replace existing architecture

---

## Testing the System

### Test Document

Create `data/test_procedure.md`:

```markdown
# System Installation Guide

This document describes how to install the software.

## Steps

Click on the Install button.
The system will be installed.
API will start automatically.
SDK configuration happens next.
REST endpoints become available.

## Safety

**WARNING** Do not modify core files during installation.
```

### Expected Results

**Document Analysis Tab:**
- ✅ Document Type: manual
- ✅ Goal: instruct
- ✅ Sensitivity: medium
- ⚠️ Missing Prerequisites Section
- ⚠️ Undefined Acronyms: API, SDK, REST
- ℹ️ No numbered steps found

**Issues Tab:**
- Passive voice: "will be installed"
- Vague instruction: "Click on the Install button"

**Protected Sections:**
- Safety section marked as forbidden for rewrites

---

## Benefits

### Before (Sentence-Only)

- ❌ No awareness of document type
- ❌ Same rules for safety and marketing docs
- ❌ No acronym tracking
- ❌ No structural validation
- ❌ No context for rewrite decisions

### After (Two-Pass)

- ✅ Document-aware analysis
- ✅ Safety docs protected automatically
- ✅ Acronym consistency checked
- ✅ Structural issues caught
- ✅ Context-guided rewrites

---

## What This Means for DocScanner

> **Context-aware, explainable, governance-safe documentation intelligence**

This is something Grammarly, Copilot, and most RAG tools **cannot do**:

1. **Read the manual as a whole** (document context)
2. **Analyze at sentence level** (precision)
3. **Enforce governance** (safety zones)
4. **Provide explainable suggestions** (no hallucinations)
5. **Separate guidance from rewrites** (clear boundaries)

---

## Future Enhancements (Optional)

### Document-Level RAG

```python
# Ask questions about the document structure
"Is this document structured correctly for a procedure?"
"What sections are missing?"
"Is this suitable for novice users?"
```

This would use RAG for **document critique**, not sentence rewriting.

### Rule Customization

Allow users to configure:
- Which document types to detect
- Sensitivity thresholds
- Required sections by type
- Custom terminology maps

### Context-Aware Sentence Rules

Extend existing sentence rules to use context:

```python
def check_passive_voice(sentence, context=None):
    if context and context.doc_type == "procedure":
        # Procedures should use active voice
        severity = "high"
    else:
        severity = "medium"
```

---

## Code Statistics

- **3 new core modules**: ~800 lines
- **6 document rules**: built-in
- **Backend integration**: ~50 lines modified
- **Frontend UI**: ~150 lines added
- **Existing code**: unchanged ✅

---

## Conclusion

DocScanner now reads documents **as a whole** while preserving **sentence-level precision**.

The architecture is:
- ✅ Lightweight (heuristic-based)
- ✅ Explainable (clear findings)
- ✅ Safe (governance-aware)
- ✅ Extensible (easy to add rules)

**Next step:** Test with real documents and iterate on rules.
