# DocScanner AI - Comprehensive Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [What the App Does](#what-the-app-does)
3. [Key Features](#key-features)
4. [Technical Architecture](#technical-architecture)
5. [Document Analysis Rules](#document-analysis-rules)
6. [User Interface Features](#user-interface-features)
7. [AI Enhancement System](#ai-enhancement-system)
8. [How to Use](#how-to-use)
9. [File Support](#file-support)
10. [Technical Stack](#technical-stack)

---

## Overview

**DocScanner AI** is a reviewer-grade technical documentation analysis system. It evaluates documents against company style guides, structural rules, and editorial judgment, and uses AI selectively to explain, justify, or safely rewrite content when appropriate.

The system makes explicit editorial decisions instead of blindly rewriting content. It combines **rule-based detection** with **reviewer-style decision-making**, using AI only when changes are provably safe and meaning-preserving. The result is feedback that maintains technical accuracy, respects document context, and explains restraint when automation would be harmful.

---

## What the App Does

DocScanner AI performs reviewer-grade document analysis through explicit editorial decisions:

### 1. **Document-Level Review**
- Detects document intent (procedural, conceptual, reference)
- Identifies structural and clarity blockers
- Makes strategic decisions about analysis scope
- Stops early when fundamental issues exist

### 2. **Sentence-Level Review (Selective)**
- Only analyzes sentences where review adds value
- Excludes titles, headings, code blocks, and markdown syntax
- Skips metadiscourse and document fragments
- Focuses analysis on content that requires judgment

### 3. **Editorial Decision Outcomes**

Every flagged issue results in one of four outcomes:

- **AI-Enhanced Rewrite** - Safe, meaning-preserving changes (rare, high-confidence)
- **Semantic Explanation** - AI explains the issue without changing the text
- **Reviewer Guidance** - Actionable advice for the author to implement
- **Reviewer Rationale** - Explains why no change is suggested (e.g., historical context, compliance language)

This mirrors how human technical reviewers work.

### 4. **Quality Assessment**
- Calculates document quality index based on issue density
- Provides sentence-by-sentence feedback with rationale
- Generates visual analytics for quality trends
- Tracks issues by category and editorial decision type

### 5. **Document Processing**
- Accepts multiple file formats (PDF, DOCX, DOC, Markdown, AsciiDoc, TXT, ZIP)
- Processes single files or batch uploads
- Provides real-time progress tracking
- Interactive results dashboard with visual analytics

---

## Editorial Decision Model

DocScanner does not force AI rewrites. Every issue is evaluated through an explicit decision framework:

### Decision Framework

```
Issue Detected
    ↓
┌───────────────────────────────────────────────┐
│ Is the change safe and meaning-preserving?    │
└───────────────┬───────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
    YES (rare)        NO (common)
        │                │
        ↓                ↓
┌────────────────┐  ┌──────────────────────────┐
│ AI-Enhanced    │  │ Can we explain the issue │
│ Rewrite        │  │ without changing it?     │
└────────────────┘  └──────────┬───────────────┘
                               │
                       ┌───────┴────────┐
                       │                │
                     YES              NO
                       │                │
                       ↓                ↓
              ┌─────────────────┐  ┌────────────────┐
              │ Semantic        │  │ Should author  │
              │ Explanation     │  │ make changes?  │
              └─────────────────┘  └────────┬───────┘
                                            │
                                    ┌───────┴────────┐
                                    │                │
                                  YES              NO
                                    │                │
                                    ↓                ↓
                          ┌──────────────────┐  ┌─────────────────┐
                          │ Reviewer         │  │ Reviewer        │
                          │ Guidance         │  │ Rationale       │
                          └──────────────────┘  └─────────────────┘
```

### The Four Outcomes

**1. AI-Enhanced Rewrite** (10-20% of issues)
- Change is provably safe
- Meaning, obligation, and time are preserved
- Technical accuracy verified
- Example: Converting unnecessary passive voice to active

**2. Semantic Explanation** (20-30% of issues)
- Issue exists but rewrite risks changing meaning
- AI explains *why* it's problematic
- Author decides how to address
- Example: Compliance language with conditionals

**3. Reviewer Guidance** (30-40% of issues)
- Clear path to improvement
- Author has context to make the change
- No AI rewrite needed
- Example: "Break this 40-word sentence at the conjunction"

**4. Reviewer Rationale** (20-30% of issues)
- Issue detected but change would be harmful
- System explains why no action is suggested
- Prevents false corrections
- Example: Historical context preserved in past tense

### Why This Matters

Most AI writing tools attempt to rewrite everything. DocScanner explicitly decides when *not* to change text. This restraint mirrors how human technical reviewers work and prevents the three common AI failures:

- **Meaning drift** - Subtle changes that alter technical accuracy
- **Context ignorance** - Rewriting text that should be preserved
- **False confidence** - Suggesting changes that make things worse

---

## Key Features

### 🔍 **Reviewer-Grade Analysis**
- **Editorial Decision Framework**: Four explicit outcomes for every issue (rewrite, explain, guide, rationale)
- **Context Preservation**: Excludes titles, headings, code blocks, markdown syntax, and metadiscourse
- **Structural Intelligence**: Detects document intent and adjusts review strategy
- **Eligibility Checking**: Determines when changes are safe before attempting them

### 🤖 **AI Assistance (Not Automation)**
- **Selective Use**: AI used only when change is provably safe and meaning-preserving
- **RAG-Grounded**: 130+ style guide documents provide context, not just generic rewrites
- **Validation Required**: All AI outputs validated for safety before display
- **Explicit Restraint**: System explains when and why it chooses not to rewrite

### 📊 **Visual Analytics**
- **Quality Index**: Overall document health score
- **Issue Breakdown**: Charts showing issue distribution by type
- **Sentence Metrics**: Total sentences, error count, quality percentage
- **Progress Tracking**: Real-time upload and analysis progress

### 💡 **User Experience**
- **Drag & Drop**: Easy file upload via drag-and-drop or file browser
- **Batch Processing**: Upload and analyze multiple files at once
- **Interactive UI**: Click on sentences to see detailed feedback
- **Copy to Clipboard**: One-click copying of improved text
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 **Developer Features**
- **Extensible Rule System**: Easy to add new writing rules
- **Debug Tools**: Comprehensive debugging utilities
- **Test Suite**: Extensive unit and integration tests
- **Documentation**: In-code documentation and external guides

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (HTML/JS)                 │
│  • File Upload  • Progress Tracking  • Results Dashboard    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Flask Backend (Python)                    │
│  • Route Handlers  • File Parsing  • Session Management    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼────────┐ ┌───▼──────────────┐
│  Rule Engine    │ │ AI System  │ │ Progress Tracker │
│  • Grammar      │ │ • RAG      │ │ • WebSocket      │
│  • Style        │ │ • Ollama   │ │ • Real-time      │
│  • Passive      │ │ • Prompts  │ │   Updates        │
│  • etc.         │ │            │ │                  │
└─────────────────┘ └────────────┘ └──────────────────┘
         │               │
         └───────┬───────┘
                 │
       ┌─────────▼──────────┐
       │   Data Storage     │
       │ • ChromaDB (RAG)   │
       │ • Session Data     │
       │ • Config Files     │
       └────────────────────┘
```

### Core Modules

**`app/app.py`** - Main Flask application
- Route handlers for upload, analysis, results
- File parsing (PDF, DOCX, Markdown, etc.)
- Session and progress management
- Document review orchestration

**`app/rules/`** - Writing rule modules
- Each rule is a separate Python module with a `check()` function
- Rules analyze text and return issue lists
- Support for RAG enhancement via `rag_rule_helper.py`

**`app/services/`** - Service layer
- Enrichment service for AI suggestions
- Progress tracking service
- Event handling

**`core/`** - Core processing logic
- Document review orchestration
- Event system
- Storage abstraction

**`static/` & `app/templates/`** - Frontend
- HTML templates with embedded JavaScript
- Bootstrap-based responsive design
- Real-time UI updates via WebSocket

---

## Document Analysis Rules

Rules are organized by editorial intent, not implementation:

### Language Correctness

**Grammar** (`grammar_rules.py`)
**Checks:**
- Subject-verb agreement
- Tense consistency
- Pronoun usage
- Basic grammatical errors

**Example Issues:**
- ❌ "The files is corrupted"
- ✅ "The files are corrupted"

**Verb Tense** (`verb_tense.py`)
**Checks:**
- Future tense in procedural documentation
- Modal verb overuse (may, might, should)
- Tense consistency across document

**Decision Logic:**
- Normalizes tense only when meaning, obligation, and time remain unchanged
- Preserves past tense for historical context
- Respects compliance language ("must", "shall")
- Explains why no change is suggested when unsafe

**Example Issues:**
- ❌ "The system will validate the input" (procedural)
- ✅ "The system validates the input"
- ✅ "In version 3.0, the system was redesigned" (historical - preserved)

---

### Clarity & Readability

**Style** (`style_rules.py`)
**Checks:**
- Adverb overuse (previously, currently, actually, etc.)
- Exclamation mark abuse (with NOTE/WARNING filtering)
- Writing tone and formality
- Redundant phrases

**Example Issues:**
- ❌ "Click on the button to start"
- ✅ "Click the button to start"

**Vague Terms** (`vague_terms.py`)
**Checks:**
- Imprecise language (several, various, etc.)
- Generic references (things, stuff)
- Unclear quantities

**Example Issues:**
- ❌ "Several files are affected"
- ✅ "Three files are affected"

**Long Sentences** (`long_sentence.py`)
**Checks:**
- Sentences over 25 words
- Excludes markdown tables
- Excludes titles/headings

**Example Issues:**
- ❌ 40-word sentence with multiple clauses
- ✅ Split into 2-3 sentences at natural boundaries

---

### Structure & Voice

**Passive Voice** (`passive_voice.py`)
**Checks:**
- Passive voice constructions
- Uses spaCy dependency parsing
- Detects "auxpass" dependencies
- Supports RAG-enhanced suggestions

**Example Issues:**
- ❌ "The file was created by the system"
- ✅ "The system created the file"

**Eligibility Checks:**
- Excludes markdown admonitions
- Skips titles and headings  
- Preserves compliance language
- Detects historical context

---

### Consistency

**Terminology** (`terminology_rules.py`)
**Checks:**
- Consistent term usage
- Technical terminology accuracy
- Industry-standard naming

**Example Issues:**
- ❌ "login page" vs "sign-in page" (inconsistent)
- ✅ Use one term consistently throughout

**General Consistency** (`consistency_rules.py`)
**Checks:**
- Capitalization patterns
- Punctuation usage
- Formatting conventions

---

### Developer Reference

Detailed implementation notes for each rule are in `app/rules/`. Each module contains:
- `check(content)` function returning issue list
- Eligibility logic for safe analysis
- Integration with RAG system for AI-assisted feedback
- Title/heading exclusion logic

---

## User Interface Features

### Upload Section
- **Drag & Drop Zone**: Drop files directly onto the interface
- **File Browser**: Click to browse and select files
- **Multi-File Support**: Select multiple files at once
- **Batch ZIP Upload**: Upload ZIP archives containing multiple documents
- **File List Display**: Shows selected files with sizes and icons
- **Add/Remove Files**: Add more files or remove individual selections
- **Clear All**: Reset selection and start over

### Progress Tracking
- **Real-time Updates**: WebSocket-powered live progress
- **Stage Indicators**: 5 stages (Upload → Parse → Extract → Analyze → Report)
- **Percentage Display**: Visual progress bar with percentage
- **ETA Calculation**: Estimated time remaining
- **Fallback Mode**: Progress simulation when WebSocket unavailable

### Results Dashboard
- **Quality Score**: Overall document quality index (0-100%)
- **Issue Summary**: Total sentences analyzed, issues detected, quality percentage
- **Analytics Chart**: Issue distribution by type and decision outcome
- **Sentence List**: All sentences with color-coded indicators showing decision type
- **Issue Details**: Expandable cards showing:
  - Rule type and decision outcome (badge)
  - Issue description with rationale
  - Feedback (rewrite, explanation, guidance, or rationale as appropriate)

### Batch Processing
- **Batch Progress**: Individual progress for each file
- **Batch Results**: Summary view of all files
- **File Selection**: Click on any file to view its results
- **Quality Comparison**: See quality scores across files
- **Active File Indicator**: Shows which file you're viewing

### Interactive Features
- **Sentence Highlighting**: Click sentences to see detailed feedback
- **Visual Indicators**: Color-coded badges show decision type (rewrite, explain, guide, rationale)
- **Scroll to Results**: Auto-scroll to dashboard after analysis
- **Feedback Details**: Expandable cards showing rationale and suggestions when available
- **Collapsible Sections**: Expand/collapse feedback for focused review

---

## AI Assistance System (When and Why)

### Core Principle: AI Executes, Reviewer Decides

DocScanner does not automatically rewrite content. AI is used only after eligibility and safety checks pass.

### When AI Is Used

**AI-Enhanced Rewrite** (10-20% of issues):
- Eligibility check confirms change is safe
- Meaning, time, and obligation preserved
- Technical accuracy verifiable
- Example: Simple passive-to-active conversion

**Semantic Explanation** (20-30% of issues):
- Issue exists but rewrite is risky
- AI explains *why* it's problematic
- No text change suggested
- Example: Compliance language analysis

### When AI Is NOT Used

**Reviewer Guidance** (30-40% of issues):
- Clear instructions sufficient
- AI rewrite would add no value
- Example: "Split at conjunction"

**Reviewer Rationale** (20-30% of issues):
- System explains why no change suggested
- Prevents false corrections
- Example: Historical context in past tense

### RAG (Retrieval Augmented Generation)

**Purpose:**
Provide style guide context to AI so suggestions align with company standards, not generic rewrites.

**How it works:**
1. **Issue Detected**: Rule identifies problem
2. **Eligibility Check**: Determine if AI rewrite is safe
3. **Context Retrieval**: Search 130+ style guides for relevant examples
4. **Decision**: Choose outcome (rewrite, explain, guide, rationale)
5. **AI Invocation**: If outcome requires AI, generate with context
6. **Validation**: Verify output meets safety standards

**Knowledge Base:**
- 130+ style guide documents in `data/rag_knowledge/`
- Before/after examples grounded in company practice
- Rule-specific documentation and patterns
- Explicit "avoid" guidance to prevent common AI mistakes

### Safety Mechanisms

**Pre-AI Validation:**
- Eligibility checks before AI invocation
- Historical context detection
- Compliance language detection
- Conditional structure analysis

**Post-AI Validation:**
- Passive voice artifact detection
- Grammar correctness verification
- Meaning preservation check
- Length and clarity assessment

**Fallback Strategy:**
- System works entirely without AI
- Rule-based guidance always available
- Explicit indication of decision type in UI

---

## How to Use

### Basic Usage

1. **Start the Application**
   ```bash
   python run.py
   ```
   Server starts on http://localhost:5000

2. **Upload a Document**
   - Drag & drop a file onto the upload zone, OR
   - Click "Browse Files" to select a file

3. **Wait for Analysis**
   - Watch real-time progress (5 stages)
   - Progress bar shows percentage complete
   - Typical analysis takes 5-30 seconds

4. **Review Results**
   - Dashboard displays quality score and metrics
   - Scroll through sentences
   - Click on sentences with issues to see details

5. **Apply Improvements**
   - Read AI-generated suggestions
   - Copy improved text with one click
   - Review multiple alternatives when available

### Batch Processing

1. **Select Multiple Files**
   - Click "Browse Files" and select multiple documents, OR
   - Upload a ZIP file containing multiple documents

2. **Upload & Analyze**
   - Click "Upload & Analyze"
   - Watch individual progress for each file

3. **Review Results**
   - See summary of all files
   - Click on any file to view its detailed results
   - Compare quality scores across files

### Advanced Features

**Add Files to Existing Selection:**
- After selecting files, click "Add More" to add additional files
- Existing selection is preserved
- Duplicates are automatically filtered

**Clear and Start Over:**
- Click "Clear All" to remove all selected files
- Reset selection and choose new files

**Intelligent Analysis Mode:**
- Click "Intelligent AI Analysis" for enhanced processing
- Uses advanced AI for deeper document insights

---

## File Support

### Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **PDF** | `.pdf` | Portable Document Format |
| **Word** | `.docx`, `.doc` | Microsoft Word documents |
| **Markdown** | `.md` | Plain text with markdown syntax |
| **AsciiDoc** | `.adoc` | AsciiDoc markup |
| **Plain Text** | `.txt` | Simple text files |
| **ZIP** | `.zip` | Archive containing multiple files |

### File Processing

**PDF Files:**
- Text extraction via PyMuPDF (fitz)
- Preserves paragraph structure
- Handles multi-page documents

**Word Documents:**
- .docx via python-docx library
- .doc via textract
- Preserves formatting context

**Markdown:**
- Converts to HTML
- Understands markdown syntax
- Excludes code blocks from analysis

**Batch ZIP:**
- Extracts all files
- Processes individually
- Provides combined results view

---

## Technical Stack

### Backend
- **Python 3.8+** - Core language
- **Flask** - Web framework
- **spaCy** - NLP and parsing
- **BeautifulSoup** - HTML processing
- **ChromaDB** - Vector database for RAG
- **Ollama** - Local AI inference

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript (ES6+)** - Client-side logic
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **Socket.IO** - Real-time communication

### NLP & AI
- **spaCy en_core_web_sm** - English language model
- **Ollama** - Local AI model hosting
- **ChromaDB** - Semantic search for RAG
- **Custom RAG System** - Context-aware suggestions

### File Processing
- **python-docx** - Word document parsing
- **PyMuPDF (fitz)** - PDF text extraction
- **markdown** - Markdown to HTML conversion
- **textract** - Legacy document support

### Development Tools
- **pytest** - Testing framework
- **watchdog** - File monitoring for auto-reload
- **logging** - Comprehensive logging system

---

## Configuration

### Environment Variables
Create `.env` file with:
```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
OLLAMA_API_URL=http://localhost:11434
```

### Rule Configuration
Rules are automatically loaded from `app/rules/` directory. Each rule must have a `check(content)` function that returns a list of issues.

### RAG Configuration
- Knowledge base: `data/rag_knowledge/`
- ChromaDB storage: `chroma_db/`
- Ollama models: Configure in `config/ollama_config.json`

---

## Performance Characteristics

### Analysis Speed
- **Simple documents** (< 100 sentences): 5-10 seconds
- **Medium documents** (100-500 sentences): 10-20 seconds
- **Large documents** (500+ sentences): 20-60 seconds

### Batch Processing
- **Multiple files**: Processed sequentially
- **ZIP archives**: Extracted then processed individually
- **Progress tracking**: Real-time updates for each file

### AI Enhancement
- **With RAG**: Additional 2-5 seconds per sentence with issues
- **Without RAG**: Instant rule-based suggestions
- **Lazy loading**: RAG initialized only when needed

---

## Architecture Decisions

### Why Reviewer-Centric Design?
- **Trust**: Explicit decisions prevent false corrections and meaning drift
- **Restraint**: System explains when not to change text, like human reviewers
- **Judgment**: Eligibility checks before automation, not blind rewrites
- **Transparency**: Four clear outcomes instead of opaque "suggestions"

### Why Rule Detection + Editorial Decision?
- **Separation of Concerns**: Detection identifies issues, decisions determine response
- **Safety**: Eligibility checks prevent harmful automation
- **Flexibility**: Same issue can have different outcomes based on context
- **Auditability**: Clear decision path for every issue

### Why RAG (When Used)?
- **Grounding**: Company style guides, not generic AI knowledge
- **Consistency**: Suggestions align with established practice
- **Context**: Relevant examples from documentation corpus
- **Maintainability**: Update knowledge without code changes

### Why Selective AI Use?
- **Restraint**: AI used only when provably safe (10-20% of issues)
- **Explanation**: AI explains issues even when not rewriting (20-30% of issues)
- **Human Judgment**: Reviewer guidance for complex cases (30-40% of issues)
- **Transparency**: Rationale provided when no change suggested (20-30% of issues)

### Why Local AI (Ollama)?
- **Privacy**: Documents never leave your infrastructure
- **Control**: Full control over model behavior and parameters
- **Cost**: No per-request API fees
- **Reliability**: Works offline without external dependencies

---

## Known Limitations

1. **AI Enhancement Speed**: RAG-enhanced suggestions take 2-5 seconds per issue
2. **Large Documents**: Very large documents (1000+ sentences) may take a while
3. **PDF Formatting**: Complex PDF layouts may not extract perfectly
4. **Batch Size**: Large batch uploads process sequentially (not parallel)
5. **Browser Support**: Requires modern browser with WebSocket support

---

## Future Enhancements

Potential improvements documented in the codebase:
- Parallel batch processing
- Advanced tense detection and normalization
- User preference overrides for aggressive splitting
- Learning from manual edits
- Domain-specific rule customization
- Confidence scoring for borderline cases

---

## Support & Resources

### Documentation Files
- `README.md` - Project structure overview
- `ARCHITECTURE_GUARDRAILS.md` - System design principles
- `docs/` - Detailed documentation and guides
- `data/rag_knowledge/` - Style guide knowledge base

### Debug Tools
- `tools/debug/` - Debugging utilities
- `scripts/` - Utility scripts
- Test files in `tests/` directory

### Logs
- Application logs via Python logging
- Browser console (F12) for client-side debugging
- Terminal output for server-side issues

---

## Quick Reference

### Starting the App
```bash
python run.py
```

### Running Tests
```bash
python -m pytest tests/
```

### Adding a New Rule
1. Create `app/rules/new_rule.py`
2. Implement `check(content)` function
3. Return list of issue strings
4. Rule is automatically loaded

### Updating RAG Knowledge
1. Add markdown files to `data/rag_knowledge/`
2. Documents are automatically indexed
3. Restart app to refresh knowledge base

---

**Last Updated:** January 30, 2026  
**Version:** Production-ready with RAG enhancement  
**Status:** ✅ Fully Operational
