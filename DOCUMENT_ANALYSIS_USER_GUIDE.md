# Document-Level Analysis: User Guide

## What's New

DocScanner now reads your entire document before analyzing individual sentences. This means it understands **context**, **structure**, and **intent** - not just grammar.

---

## The Three Analysis Tabs

### 1. Issues Tab (Sentence-Level)
**What it shows:** Grammar, style, and readability issues in individual sentences

**Example findings:**
- ❌ Passive voice detected in sentence 5
- ❌ Long sentence (42 words) in sentence 12
- ❌ Vague term "very" in sentence 8

**What you can do:** Click the AI button to get rewrite suggestions

---

### 2. AI Assistance Tab
**What it shows:** AI-powered rewrite suggestions for flagged sentences

**Example content:**
- 📋 Original: "The system will be installed automatically"
- ✍️ Suggestion: "The system installs automatically"
- 💡 Explanation: Active voice makes instructions clearer

---

### 3. Document Analysis Tab ⭐ NEW
**What it shows:** Document-level findings about structure, consistency, and completeness

**Example findings:**

#### Structure Issues
- ⚠️ **Missing Prerequisites Section**
  - Description: Procedure documents should include a prerequisites section
  - Guidance: Add a "Prerequisites" or "Before You Begin" section

#### Consistency Issues
- ⚠️ **Undefined Acronyms: API, SDK, JWT**
  - Description: Found 3 acronyms without definitions
  - Guidance: Define acronyms on first use: Full Term (ACRONYM)

- ℹ️ **Mixed Verb Tenses**
  - Description: Document uses mixed verb tenses across sections
  - Guidance: Use consistent tense (present for procedures, past for reports)

#### Completeness Issues
- ℹ️ **No Numbered Steps Found**
  - Description: Procedures are clearer with numbered steps
  - Guidance: Use numbered lists for step-by-step instructions

---

## How Document Context Affects Analysis

### Document Type Detection

DocScanner automatically detects:
- **Manual/Procedure** - Step-by-step instructions
- **API Reference** - Technical documentation
- **Safety Document** - Warnings and hazards
- **Concept** - Explanatory content

### Smart Governance

**Safety Documents:**
- 🔒 Rewrites **blocked** in safety sections
- ⚠️ Higher sensitivity for all changes
- ✅ Grammar checks still applied

**API Documentation:**
- 🔒 Code samples protected
- ✅ Parameter descriptions checked
- ℹ️ Consistency validation enabled

**Procedures:**
- ✅ Step numbering validated
- ✅ Prerequisites checked
- ✅ Active voice preferred

---

## Understanding Document Context

When you upload a document, DocScanner analyzes:

### Basic Properties
- **Document Type:** manual | api | safety | concept | reference
- **Primary Goal:** instruct | explain | reference | warn
- **Audience Level:** novice | intermediate | expert
- **Rewrite Sensitivity:** low | medium | high | critical

### Structure Analysis
- Heading hierarchy
- Section organization
- Table of contents presence
- Missing required sections

### Content Characteristics
- Dominant verb tense
- Average sentence length
- Terminology usage
- Acronym definitions

### Protected Zones
- Safety sections (no rewrites)
- Legal disclaimers (no rewrites)
- Warning blocks (no rewrites)

---

## Test Documents Included

Try these sample documents to see the system in action:

### `test_installation_procedure.md`
**Expected Document Analysis:**
- Type: manual
- Missing: Numbered steps
- Issues: Undefined acronyms (API, SDK, REST, GUI)
- Protected: Safety and Legal sections
- Passive voice in multiple sentences

### `test_api_reference.md`
**Expected Document Analysis:**
- Type: api
- Missing: API versioning info
- Issues: Undefined acronym (JWT)
- Mixed tenses detected
- High rewrite sensitivity

---

## Best Practices

### For Procedures
✅ Include Prerequisites section
✅ Use numbered steps (1., 2., 3.)
✅ Define all acronyms
✅ Use active voice
✅ Keep consistent tense (present)

### For API Documentation
✅ Define request/response formats
✅ Include all HTTP status codes
✅ Document all parameters
✅ Provide code examples
✅ Use consistent terminology

### For Safety Documents
✅ Use clear warning labels (WARNING, CAUTION)
✅ Place safety info at the beginning
✅ Use simple, direct language
✅ Avoid passive voice in warnings
✅ Keep safety sections unchanged (protected)

---

## FAQs

### Q: Will document analysis change my document?
**A:** No! Document-level findings are **guidance only**. Only sentence-level issues can trigger rewrites, and you always have final control.

### Q: What happens in protected sections?
**A:** Grammar and style issues are still flagged, but **no rewrite suggestions** are offered. Your safety warnings stay exactly as written.

### Q: How does it detect document type?
**A:** Using lightweight heuristics:
- Presence of keywords ("Procedure", "Prerequisites", "API", "Parameters")
- Heading patterns
- Content structure
- Section names

### Q: Can I customize the rules?
**A:** Not yet in the UI, but the system is extensible. Document rules can be added in `core/document_rule.py`.

### Q: Does this replace sentence analysis?
**A:** No! It **enhances** it. You get both:
- Precise sentence-level fixes
- Holistic document-level guidance

---

## Technical Details

### Architecture
```
PASS 0: Document Analysis (context extraction)
  ↓
PASS 1: Sentence Analysis (grammar, style)
  ↓
PASS 2: Governance (rewrite decisions)
```

### What's Lightweight
- Regex-based pattern matching
- Simple keyword detection
- Heuristic classification
- No ML models for document analysis
- Fast execution (< 100ms)

### What's Preserved
- All existing sentence rules
- RAG-enhanced AI suggestions
- Governance gates
- Explainable feedback

---

## Examples

### Before (Sentence-Only)
```
❌ Passive voice: "The system will be installed"
❌ Passive voice: "API will start automatically"
❌ Long sentence: "Navigate to settings and configure..."
```

### After (Two-Pass)
```
📋 Document Context:
  - Type: Procedure
  - Sensitivity: Medium
  - Protected: Safety, Legal sections

⚠️ Structure Issues:
  - Missing numbered steps
  - Undefined acronyms: API, SDK, REST

❌ Sentence Issues:
  - Passive voice: "The system will be installed"
  - Passive voice: "API will start automatically"
  - Long sentence: "Navigate to settings and configure..."
```

**The difference:** You now understand **why** the issues matter in the context of your document type.

---

## Summary

DocScanner's two-pass architecture gives you:

1. **Context-Aware Analysis** - Understands your document type and goal
2. **Structural Validation** - Checks for missing sections and consistency
3. **Smart Governance** - Protects safety/legal content automatically
4. **Precise Fixes** - Sentence-level rewrites with document context
5. **Clear Separation** - Guidance vs. rewrites clearly distinguished

**Result:** Safer, smarter, more explainable documentation assistance.
