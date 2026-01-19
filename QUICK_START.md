# Quick Start: Document-Level Analysis

## ✅ Implementation Complete

The two-pass document analysis system is now fully integrated into DocScanner.

---

## Quick Validation (2 minutes)

### Step 1: Test Core Functionality
```bash
python test_document_analysis.py
```

**Expected output:**
```
✅ Document Type: safety
✅ Forbidden Sections: Safety, Legal
⚠️ Undefined Acronyms: API, REST, SDK, WARNING
ℹ️ Missing Introduction section
🎉 Document-level analysis is working correctly!
```

### Step 2: Start the Server
```bash
python run.py
```

### Step 3: Test in Browser

1. Open http://localhost:5000
2. Upload `data/test_installation_procedure.md`
3. Check three tabs:
   - **Issues Tab** - Sentence-level problems
   - **AI Assistance Tab** - Rewrite suggestions
   - **Document Analysis Tab** ⭐ NEW - Document findings

---

## What You Should See

### Document Analysis Tab

**Document Context:**
```
Type: safety
Goal: warn
Audience: expert
Sensitivity: critical
Protected Sections: Safety, Legal
```

**Findings:**

⚠️ **WARNING: Undefined Acronyms**
- Found 4 acronyms without definitions: API, REST, SDK
- Guidance: Define acronyms on first use

ℹ️ **INFO: No Numbered Steps Found**
- Procedures are clearer with numbered steps
- Guidance: Use numbered lists (1., 2., 3.)

### Issues Tab

Should show sentence-level problems like:
- Passive voice in sentence 3
- "Click on" usage detected
- Long sentence detected

### Protected Behavior

**Important:** In the Safety section:
- ✅ Issues are flagged
- ❌ NO rewrite suggestions offered
- 🔒 Content protected automatically

---

## Files Created

### Core Implementation
- ✅ `core/document_context.py` - Data model
- ✅ `core/document_analyzer.py` - Analysis engine
- ✅ `core/document_rule.py` - Rule framework

### Integration
- ✅ `app/app.py` - Backend integration (PASS 0 added)
- ✅ `app/templates/index.html` - UI with new tab

### Testing & Documentation
- ✅ `test_document_analysis.py` - Validation script
- ✅ `data/test_installation_procedure.md` - Test doc 1
- ✅ `data/test_api_reference.md` - Test doc 2
- ✅ `DOCUMENT_ANALYSIS_ARCHITECTURE.md` - Technical docs
- ✅ `DOCUMENT_ANALYSIS_USER_GUIDE.md` - User guide
- ✅ `IMPLEMENTATION_SUMMARY.md` - Complete summary
- ✅ `QUICK_START.md` - This file

---

## Architecture Verification

### PASS 0: Document-Level (NEW)
```python
# In app.py, before sentence analysis:
analyzer = DocumentAnalyzer()
context = analyzer.analyze(plain_text, html_content)
findings = evaluate_document_rules(context, plain_text)
```

✅ Extracts document-wide signals
✅ Runs document-level rules
✅ Creates DocumentContext object

### PASS 1: Sentence-Level (ENHANCED)
```python
# Now receives document context:
feedback = analyze_sentence(
    sentence, 
    rules,
    document_context=current_document_context,
    sentence_position=index
)
```

✅ Existing sentence rules preserved
✅ Document context available to rules
✅ Can check forbidden zones

### PASS 2: Governance (EXISTING)
✅ Already implemented
✅ Now enhanced with document context
✅ Automatically protects forbidden zones

---

## Key Behaviors to Verify

### 1. Document Type Detection
Upload different documents and verify correct type:
- `test_installation_procedure.md` → **safety** or **manual**
- `test_api_reference.md` → **api**

### 2. Forbidden Zone Protection
In Safety/Legal sections:
- ✅ Grammar issues shown
- ❌ No rewrite buttons
- 🔒 Content protected

### 3. Acronym Detection
The system should flag:
- API, SDK, REST, JWT, GUI (if undefined)
- Suggest defining them on first use

### 4. Structure Validation
For procedure documents:
- Checks for Prerequisites section
- Validates numbered steps
- Ensures logical section order

### 5. Consistency Checks
Across the document:
- Mixed verb tenses
- Inconsistent terminology
- Undefined technical terms

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'core'"

**Fix:**
```bash
# Make sure you're in the doc-scanner directory
cd d:\doc-scanner
python test_document_analysis.py
```

### Document Analysis Tab is Empty

**Check:**
1. Is `DOCUMENT_ANALYSIS_AVAILABLE = True` in logs?
2. Did document analysis run in PASS 0?
3. Look for "PASS 0: Analyzing document structure" in console

**Fix:** Check Python logs when uploading

### No Findings Shown

**This is OK if:**
- Document is well-structured
- All acronyms defined
- No consistency issues

**To test:** Use the provided test documents which intentionally have issues

---

## Next Steps

### Immediate
1. ✅ Run validation script
2. ✅ Test in browser
3. ✅ Upload both test documents
4. ✅ Verify all three tabs work

### Short Term
1. Test with real-world documents
2. Adjust rule thresholds if needed
3. Add custom document types if required

### Future Enhancements
1. Context-aware sentence rules
2. Document-level RAG queries
3. Custom rule configuration UI
4. Additional document types

---

## Success Indicators

You know it's working when:

✅ **Three tabs visible** - Issues, AI Assistance, Document Analysis
✅ **Document context shown** - Type, goal, audience, sensitivity
✅ **Findings appear** - Structure, consistency, completeness issues
✅ **Separate from rewrites** - Document tab = guidance only
✅ **Protected zones** - No rewrites in Safety/Legal sections
✅ **Validation passes** - test_document_analysis.py succeeds

---

## Support

### Documentation
- Technical: `DOCUMENT_ANALYSIS_ARCHITECTURE.md`
- User Guide: `DOCUMENT_ANALYSIS_USER_GUIDE.md`
- Summary: `IMPLEMENTATION_SUMMARY.md`

### Code
- Core logic: `core/document_*.py`
- Integration: `app/app.py` (search for "PASS 0")
- UI: `app/templates/index.html` (search for "Document Analysis")

### Validation
- Test script: `test_document_analysis.py`
- Test docs: `data/test_*.md`

---

## Summary

The system is **complete and tested**. You can now:

1. ✅ Read documents as a whole (PASS 0)
2. ✅ Analyze at sentence level (PASS 1)
3. ✅ Apply governance safely (PASS 2)
4. ✅ See document findings separately from rewrites
5. ✅ Protect critical sections automatically

**This is context-aware, explainable, governance-safe documentation intelligence.**

Ready to use! 🚀
