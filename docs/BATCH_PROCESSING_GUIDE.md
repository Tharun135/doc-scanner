# 📚 Batch Processing - Quick Start Guide

## What is Batch Processing?

Check **multiple documents at once** for technical writing rule violations. Perfect for:
- Auditing existing documentation
- Pre-commit checks
- CI/CD integration
- Documentation quality reports

---

## ✅ Installation Complete

The batch processor is ready to use:
- **Main script**: `batch_check.py`
- **Supporting files**: 
  - `app/rules/analytics.py` - Track violations
  - `app/rules/batch_processor.py` - Core processing
  - `app/rules/builder.py` - Custom rule creation

---

## 🚀 Quick Start

### 1. Check a Single File
```bash
python batch_check.py test_atomic_rules.md
```

### 2. Check All Files in a Directory
```bash
python batch_check.py docs/
```

### 3. Check Specific Pattern
```bash
python batch_check.py docs/*.md
python batch_check.py --pattern "*.txt" docs/
```

### 4. Generate HTML Report
```bash
python batch_check.py docs/ --html report.html
```

### 5. Generate JSON Report
```bash
python batch_check.py docs/ --json results.json
```

### 6. Show Only Errors
```bash
python batch_check.py docs/ --errors-only
```

### 7. Quiet Mode (Minimal Output)
```bash
python batch_check.py docs/ --quiet
```

---

## 📊 Example Output

```
================================================================================
BATCH DOCUMENT CHECKER
================================================================================

Loading rules...
[OK] Loaded 20 rules

Finding files matching pattern: *.md
[OK] Found 15 file(s)

[1/15] Checking: docs/api-guide.md
  Status: PASSED
  Sentences: 42
  Violations: 0 (Errors: 0, Warnings: 0, Info: 0)

[2/15] Checking: docs/user-manual.md
  Status: FAILED
  Sentences: 156
  Violations: 23 (Errors: 8, Warnings: 12, Info: 3)

...

================================================================================
BATCH PROCESSING SUMMARY
================================================================================
Total Files: 15
Total Sentences: 1,234
Total Violations: 87

Files Passed: 10
Files with Errors: 5

Errors: 34
Warnings: 42
Info: 11
================================================================================

[FAILED] Critical errors found - recommended exit code: 1
```

---

## 📋 Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `paths` | Files or directories to check | `docs/ file1.md` |
| `--pattern PATTERN` | File pattern to match | `--pattern "*.txt"` |
| `--errors-only` | Only show error-level violations | `--errors-only` |
| `--html PATH` | Generate HTML report | `--html report.html` |
| `--json PATH` | Generate JSON report | `--json results.json` |
| `--quiet` | Minimal console output | `--quiet` |
| `--fail-on-error` | Exit with code 1 if errors found | `--fail-on-error` |

---

## 📈 HTML Report Features

The HTML report includes:
- ✅ **Visual Summary Cards**: Total files, errors, warnings, info
- ✅ **Expandable File Sections**: Click to see violations
- ✅ **Color-Coded Violations**: Red (error), Yellow (warn), Blue (info)
- ✅ **Sentence Context**: See exactly where violations occur
- ✅ **Inline Suggestions**: Fix recommendations for each violation
- ✅ **Responsive Design**: Works on desktop and mobile

### Example HTML Report Structure:
```
📊 Summary Cards
├── Total Files: 15
├── Files Passed: 10
├── Files with Errors: 5
├── Total Violations: 87
└── Breakdown: 34 errors, 42 warnings, 11 info

📄 File Details (Expandable)
├── api-guide.md [PASSED]
├── user-manual.md [FAILED]
│   ├── Violation 1: TENSE_001 (ERROR)
│   │   ├── Message: Future tense not allowed
│   │   ├── Sentence: "The system will display..."
│   │   └── Suggestion: Use simple present
│   └── Violation 2: UI_001 (ERROR)
└── ...
```

---

## 🎯 Common Use Cases

### Use Case 1: Pre-Commit Check
```bash
# Check only staged files
python batch_check.py $(git diff --cached --name-only --diff-filter=ACM | grep "\.md$")
```

### Use Case 2: Daily Documentation Audit
```bash
# Check all docs and save report with timestamp
python batch_check.py docs/ \
  --html "reports/daily-$(date +%Y%m%d).html" \
  --json "reports/daily-$(date +%Y%m%d).json"
```

### Use Case 3: CI/CD Pipeline
```bash
# Exit with error code if violations found
python batch_check.py docs/ --errors-only --quiet
if [ $? -ne 0 ]; then
  echo "Documentation violations found!"
  exit 1
fi
```

### Use Case 4: Multiple Directories
```bash
# Check multiple documentation folders
python batch_check.py docs/ guides/ tutorials/ --html full-report.html
```

### Use Case 5: Specific File Types
```bash
# Check only .txt files
python batch_check.py docs/ --pattern "*.txt"

# Check multiple patterns (use multiple runs)
python batch_check.py docs/*.md docs/*.txt --html report.html
```

---

## 🔧 Advanced Usage

### Custom Exit Codes
The script exits with:
- `0` = Success (no errors)
- `1` = Failure (errors found)

Use in scripts:
```bash
python batch_check.py docs/ --quiet
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All checks passed"
  # Deploy documentation
else
  echo "❌ Violations found"
  # Block deployment
fi
```

### Combining with Other Tools
```bash
# Check files, then upload report
python batch_check.py docs/ --html report.html && \
  aws s3 cp report.html s3://my-bucket/reports/

# Check and send notification
python batch_check.py docs/ --json results.json && \
  curl -X POST https://api.slack.com/webhook \
    -d @results.json
```

---

## 📊 JSON Report Format

```json
{
  "timestamp": "2025-12-09T13:40:00",
  "files": [
    {
      "filename": "docs/api-guide.md",
      "sentence_count": 42,
      "violation_count": 8,
      "errors": 3,
      "warnings": 4,
      "info": 1,
      "status": "failed",
      "violations": [
        {
          "sentence_number": 5,
          "sentence": "You will click the Save button.",
          "rule_id": "TENSE_001",
          "category": "tense",
          "severity": "error",
          "message": "Future tense not allowed in procedures.",
          "suggestion": "Rewrite in simple present.",
          "matched_text": "will"
        }
      ]
    }
  ],
  "summary": {
    "total_files": 15,
    "total_sentences": 1234,
    "total_violations": 87,
    "errors": 34,
    "warnings": 42,
    "info": 11,
    "files_with_errors": 5,
    "files_passed": 10
  }
}
```

---

## 🐛 Troubleshooting

### Issue: No files found
```bash
# Check pattern matches files
ls docs/*.md

# Try absolute path
python batch_check.py /full/path/to/docs/
```

### Issue: Module import errors
```bash
# Ensure you're in the correct directory
cd /path/to/doc-scanner

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: Rules not loading
```bash
# Test rule loading
python -c "from app.rules.loader import load_rules; print(f'{len(load_rules())} rules loaded')"
```

---

## 🎓 Best Practices

1. **Start Small**: Test with one file first
   ```bash
   python batch_check.py README.md
   ```

2. **Use HTML Reports**: Visual reports are easier to review
   ```bash
   python batch_check.py docs/ --html report.html
   ```

3. **Focus on Errors First**: Use `--errors-only` to prioritize
   ```bash
   python batch_check.py docs/ --errors-only
   ```

4. **Automate**: Add to git hooks or CI/CD
   ```bash
   # .git/hooks/pre-commit
   python batch_check.py $(git diff --cached --name-only | grep "\.md$")
   ```

5. **Track Progress**: Generate daily reports
   ```bash
   # Daily cron job
   0 9 * * * cd /path/to/doc-scanner && python batch_check.py docs/ --html daily-report.html
   ```

---

## 🚀 Next Steps

1. **Test the batch checker**:
   ```bash
   python batch_check.py test_atomic_rules.md --html test-report.html
   ```

2. **Check your actual docs**:
   ```bash
   python batch_check.py docs/ --html docs-report.html
   ```

3. **Set up CI/CD** (see `scripts/ci_check.py`)

4. **Add analytics** (track violations over time)

---

## 📞 Getting Help

```bash
# Show help
python batch_check.py --help

# Show examples
python batch_check.py --help | grep "Examples:" -A 10
```

---

## ✅ Quick Test

Run this to verify everything works:

```bash
# Test with the atomic rules test file
python batch_check.py test_atomic_rules.md --html test-report.html

# Expected output:
# - File checked successfully
# - Violations found and categorized
# - HTML report generated
# - Exit code 1 (because test file has intentional errors)
```

Open `test-report.html` in your browser to see the interactive report!

---

**Status**: ✅ Batch Processing Fully Implemented  
**Last Updated**: December 9, 2025  
**Version**: 1.0.0
