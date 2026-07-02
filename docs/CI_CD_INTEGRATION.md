# 🔄 CI/CD Integration - Complete Guide

## Overview

Automatically check documentation quality in your development workflow:
- ✅ **GitHub Actions** - PR comments + artifacts
- ✅ **GitLab CI/CD** - Pipeline integration
- ✅ **Azure DevOps** - Pipeline tasks
- ✅ **Git Hooks** - Local pre-commit checks

---

## 🎯 Quick Start

### Install Git Hooks (Local)
```powershell
# Windows
.\setup-git-hooks.ps1

# Linux/Mac
chmod +x .git/hooks/pre-commit
```

Now every commit will be checked automatically!

---

## 📋 Components Installed

### 1. GitHub Actions Workflow
**File:** `.github/workflows/docs-check.yml`

**Features:**
- ✅ Runs on push and pull requests
- ✅ Only checks documentation files (*.md, docs/*, guides/*)
- ✅ Generates HTML + JSON reports
- ✅ Posts PR comment with results
- ✅ Uploads artifacts (30-day retention)
- ✅ Fails build if critical errors found

**Triggers:**
- Push to: `main`, `master`, `develop`, `branch-*`
- Pull requests to: `main`, `master`, `develop`
- Only when documentation files change

---

### 2. GitLab CI/CD Pipeline
**File:** `.gitlab-ci.yml`

**Features:**
- ✅ Two-stage pipeline (test + report)
- ✅ Caches dependencies
- ✅ Generates artifacts
- ✅ JUnit test reports
- ✅ 30-day artifact retention

**Stages:**
1. `test` - Run quality checks
2. `report` - Generate reports

---

### 3. Azure DevOps Pipeline
**File:** `azure-pipelines.yml`

**Features:**
- ✅ Ubuntu-based runner
- ✅ Python 3.11 environment
- ✅ Publishes test results
- ✅ Publishes pipeline artifacts
- ✅ Fails task on errors

**Triggers:**
- Push to: `main`, `develop`, `feature/*`
- Pull requests to: `main`, `develop`

---

### 4. Git Pre-Commit Hook
**Files:** 
- `.git/hooks/pre-commit` (bash/PowerShell launcher)
- `.git/hooks/pre-commit.ps1` (PowerShell implementation)

**Features:**
- ✅ Checks only staged .md files
- ✅ Runs before commit completes
- ✅ Blocks commit if errors found
- ✅ Provides helpful error messages
- ✅ Can be bypassed with `--no-verify`

---

## 🚀 Usage Examples

### GitHub Actions

#### Viewing Results
1. Go to **Actions** tab in your repo
2. Click on latest workflow run
3. Download artifacts:
   - `documentation-report` (HTML)
   - `documentation-results` (JSON)

#### PR Comments
Automatic comment on every PR:
```
🔴 Documentation Quality Check ❌ FAILED

Summary
- Total Files: 5
- Total Sentences: 234
- Total Violations: 12

Breakdown
- 🔴 Errors: 8 (must fix)
- 🟡 Warnings: 3 (suggestions)
- 🔵 Info: 1 (informational)

⚠️ Action Required
This PR contains critical documentation errors that must be fixed before merging.

📊 Detailed Report
Download the full HTML report from the workflow artifacts.
```

---

### Git Pre-Commit Hook

#### Normal Flow
```bash
$ git commit -m "Update documentation"

🔍 Running documentation quality checks...
Files to check:
  - README.md
  - docs/api-guide.md

✅ Documentation quality checks passed!

[main abc1234] Update documentation
 2 files changed, 45 insertions(+), 12 deletions(-)
```

#### When Errors Found
```bash
$ git commit -m "Update documentation"

🔍 Running documentation quality checks...
Files to check:
  - README.md

❌ Documentation quality checks failed!

Critical errors found in your documentation.
Please fix the errors before committing.

To see detailed report, run:
  python batch_check.py README.md --html report.html

To bypass this check (not recommended), use:
  git commit --no-verify
```

---

## 🛠️ Configuration

### Customize Severity Level

**Fail only on errors (recommended):**
```yaml
python batch_check.py docs/ --errors-only
```

**Fail on errors and warnings:**
```yaml
python batch_check.py docs/ --fail-on-warn
```

**Check but don't fail:**
```yaml
python batch_check.py docs/
continue-on-error: true
```

---

### Customize File Patterns

**GitHub Actions** (`.github/workflows/docs-check.yml`):
```yaml
on:
  push:
    paths:
      - '**.md'           # All markdown files
      - '**.txt'          # All text files
      - 'docs/**'         # Everything in docs/
      - 'guides/**'       # Everything in guides/
      - '!node_modules/**' # Exclude node_modules
```

**Git Hook** (`.git/hooks/pre-commit.ps1`):
```powershell
# Change this line to check different file types
$stagedFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { 
    $_ -match "\.(md|txt)$"  # Check .md and .txt files
}
```

---

### Customize Check Strictness

Edit `batch_check.py` command in your CI config:

**Strict Mode** (fail on any violation):
```bash
python batch_check.py docs/ --fail-on-warn
```

**Lenient Mode** (warnings don't fail):
```bash
python batch_check.py docs/ --errors-only
```

**Info Mode** (just report, don't fail):
```bash
python batch_check.py docs/ || true
```

---

## 📊 Example Workflow Run

### GitHub Actions Output
```
Run documentation quality checks...
================================================================================
BATCH DOCUMENT CHECKER
================================================================================

Loading rules...
[OK] Loaded 20 rules

Finding files matching pattern: *.md
[OK] Found 5 file(s)

[1/5] Checking: README.md
  Status: PASSED
  Sentences: 45
  Violations: 0 (Errors: 0, Warnings: 0, Info: 0)

[2/5] Checking: docs/api-guide.md
  Status: FAILED
  Sentences: 89
  Violations: 8 (Errors: 3, Warnings: 4, Info: 1)

...

================================================================================
BATCH PROCESSING SUMMARY
================================================================================
Total Files: 5
Total Sentences: 234
Total Violations: 12

Files Passed: 3
Files with Errors: 2

Errors: 8
Warnings: 3
Info: 1
================================================================================

[FAILED] Critical errors found - recommended exit code: 1

Error: Process completed with exit code 1.
```

---

## 🎯 Best Practices

### 1. Run Locally Before Pushing
```bash
# Check your changes before committing
python batch_check.py $(git diff --name-only | grep ".md$") --html report.html
```

### 2. Review Reports Regularly
- Download HTML reports from CI artifacts
- Track trends over time
- Focus on high-severity violations first

### 3. Educate Team
- Share rule documentation
- Review common violations
- Create style guide based on rules

### 4. Gradual Rollout
```yaml
# Start with warnings only
continue-on-error: true

# After team adapts, enforce errors
continue-on-error: false
```

### 5. Exclude Generated Files
```yaml
# Don't check auto-generated docs
python batch_check.py docs/ --exclude "node_modules/*" "build/*" "dist/*"
```

---

## 🐛 Troubleshooting

### Issue: Hook Not Running

**Check installation:**
```powershell
ls .git/hooks/pre-commit
```

**Re-install:**
```powershell
.\setup-git-hooks.ps1
```

---

### Issue: GitHub Actions Failing to Find Files

**Check paths:**
```yaml
paths:
  - '**.md'  # Use ** for recursive matching
```

**Debug:**
```yaml
- name: List files
  run: find . -name "*.md" -type f
```

---

### Issue: Dependencies Not Found

**GitHub Actions:**
```yaml
- name: Install dependencies
  run: |
    pip install flask textstat spacy beautifulsoup4
    python -m spacy download en_core_web_sm
```

**Add to requirements.txt:**
```
flask>=2.3.0
textstat>=0.7.3
spacy>=3.5.0
beautifulsoup4>=4.12.0
```

---

### Issue: Pre-Commit Hook Bypassed

**Enforce in CI:**
```yaml
# CI will catch it even if hook bypassed locally
- name: Run documentation checks
  run: python batch_check.py docs/ --errors-only
```

---

## 📈 Metrics & Reporting

### Track Quality Over Time

**Weekly Report (Cron Job):**
```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
```

**Save Results:**
```bash
python batch_check.py docs/ \
  --json "reports/weekly-$(date +%Y%m%d).json" \
  --html "reports/weekly-$(date +%Y%m%d).html"
```

**Track Metrics:**
- Total violations over time
- Error rate by file
- Most violated rules
- Quality score trends

---

## 🔐 Security Considerations

### 1. Secrets in CI
Never commit sensitive data to docs. Use environment variables:

```yaml
- name: Check docs
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: python batch_check.py docs/
```

### 2. Artifact Retention
Reports may contain sensitive info:

```yaml
artifacts:
  retention-days: 7  # Shorter retention for sensitive repos
```

### 3. Public vs Private Repos
For public repos, ensure reports don't leak sensitive information.

---

## 🎓 Advanced Features

### 1. Custom Rule Profiles
```yaml
- name: Check API docs
  run: python batch_check.py docs/api/ --profile api

- name: Check user docs
  run: python batch_check.py docs/user/ --profile user-manual
```

### 2. Conditional Checks
```yaml
- name: Check docs
  if: contains(github.event.head_commit.message, '[docs]')
  run: python batch_check.py docs/
```

### 3. Matrix Testing
```yaml
strategy:
  matrix:
    docs-folder: [docs/api, docs/guides, docs/tutorials]
steps:
  - name: Check ${{ matrix.docs-folder }}
    run: python batch_check.py ${{ matrix.docs-folder }}
```

---

## 📚 Related Documentation

- **Batch Processing Guide**: `BATCH_PROCESSING_GUIDE.md`
- **Rule System**: `ATOMIC_RULES_SYSTEM.md`
- **Roadmap**: `ROADMAP.md`

---

## ✅ Verification

Test your CI/CD setup:

### 1. Test Git Hook
```bash
# Make a change to a .md file
echo "# Test" >> test.md
git add test.md
git commit -m "Test hook"

# Should run checks automatically
```

### 2. Test GitHub Actions
```bash
# Create a branch and push
git checkout -b test-ci
git push origin test-ci

# Check Actions tab in GitHub
```

### 3. Test Full Workflow
```bash
# Create PR with documentation changes
git checkout -b docs-update
echo "# Updated Docs" >> README.md
git add README.md
git commit -m "Update docs"
git push origin docs-update

# Create PR on GitHub
# Check for automated comment
```

---

## 🎉 Summary

You now have **complete CI/CD integration**:

✅ **GitHub Actions** - Automated PR checks with comments  
✅ **GitLab CI/CD** - Pipeline integration  
✅ **Azure DevOps** - Full pipeline support  
✅ **Git Hooks** - Local pre-commit validation  
✅ **Artifacts** - HTML + JSON reports  
✅ **Flexibility** - Multiple configuration options  

**Next commit will be automatically checked!** 🚀

---

**Status**: ✅ CI/CD Integration Complete  
**Last Updated**: December 9, 2025  
**Version**: 1.0.0
