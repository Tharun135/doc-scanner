"""
Batch Document Checker - CLI Tool
Process multiple documents and generate compliance reports.

Usage:
    python batch_check.py docs/                    # Check all files in directory
    python batch_check.py docs/*.md                # Check specific pattern
    python batch_check.py file1.md file2.md        # Check specific files
    python batch_check.py docs/ --profile api      # Use specific rule profile
    python batch_check.py docs/ --html report.html # Custom report location
    python batch_check.py docs/ --errors-only      # Show only errors
"""

import sys
import os
import argparse
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.loader import load_rules
from app.rules.matcher import apply_rules, get_severity_summary
from datetime import datetime


class BatchChecker:
    """Command-line batch document checker."""
    
    def __init__(self, rules, show_progress=True):
        self.rules = rules
        self.show_progress = show_progress
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "files": [],
            "summary": {
                "total_files": 0,
                "total_sentences": 0,
                "total_violations": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0,
                "files_with_errors": 0,
                "files_passed": 0
            }
        }
    
    def check_files(self, file_paths, errors_only=False):
        """
        Check multiple files for rule violations.
        
        Args:
            file_paths (list): List of file paths to check
            errors_only (bool): Only report error-level violations
        
        Returns:
            dict: Complete results with summary
        """
        self.results["summary"]["total_files"] = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            if self.show_progress:
                print(f"\n[{i}/{len(file_paths)}] Checking: {file_path}")
            
            file_result = self._check_file(file_path, errors_only)
            self.results["files"].append(file_result)
            
            # Update summary
            self.results["summary"]["total_sentences"] += file_result["sentence_count"]
            self.results["summary"]["total_violations"] += file_result["violation_count"]
            self.results["summary"]["errors"] += file_result["errors"]
            self.results["summary"]["warnings"] += file_result["warnings"]
            self.results["summary"]["info"] += file_result["info"]
            
            if file_result["errors"] > 0:
                self.results["summary"]["files_with_errors"] += 1
            else:
                self.results["summary"]["files_passed"] += 1
            
            if self.show_progress:
                self._print_file_summary(file_result)
        
        return self.results
    
    def _check_file(self, file_path, errors_only=False):
        """Check a single file."""
        file_result = {
            "filename": str(file_path),
            "sentence_count": 0,
            "violation_count": 0,
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "violations": []
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sentences (improved splitting)
            sentences = self._split_into_sentences(content)
            file_result["sentence_count"] = len(sentences)
            
            # Apply rules to each sentence
            for sentence_idx, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                violations = apply_rules(sentence, self.rules)
                
                for v in violations:
                    # Skip non-errors if errors_only mode
                    if errors_only and v["severity"] != "error":
                        continue
                    
                    file_result["violation_count"] += 1
                    
                    if v["severity"] == "error":
                        file_result["errors"] += 1
                    elif v["severity"] == "warn":
                        file_result["warnings"] += 1
                    else:
                        file_result["info"] += 1
                    
                    file_result["violations"].append({
                        "sentence_number": sentence_idx + 1,
                        "sentence": sentence[:150] + ("..." if len(sentence) > 150 else ""),
                        "rule_id": v["rule_id"],
                        "category": v["category"],
                        "severity": v["severity"],
                        "message": v["message"],
                        "suggestion": v.get("suggestion", ""),
                        "matched_text": v.get("matched_text", "")
                    })
            
            file_result["status"] = "passed" if file_result["errors"] == 0 else "failed"
            
        except Exception as e:
            file_result["status"] = "error"
            file_result["error_message"] = str(e)
            print(f"  [ERROR] Failed to process file: {e}")
        
        return file_result
    
    def _split_into_sentences(self, content):
        """Split content into sentences."""
        # Remove code blocks to avoid false positives
        import re
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]+`', '', content)
        
        # Basic sentence splitting
        sentences = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Split on sentence boundaries
            parts = re.split(r'[.!?]+\s+', line)
            sentences.extend([s.strip() for s in parts if s.strip()])
        
        return sentences
    
    def _print_file_summary(self, file_result):
        """Print summary for a single file."""
        if file_result.get("error_message"):
            print(f"  Status: ERROR - {file_result['error_message']}")
            return
        
        status_color = "PASSED" if file_result["status"] == "passed" else "FAILED"
        print(f"  Status: {status_color}")
        print(f"  Sentences: {file_result['sentence_count']}")
        print(f"  Violations: {file_result['violation_count']} "
              f"(Errors: {file_result['errors']}, "
              f"Warnings: {file_result['warnings']}, "
              f"Info: {file_result['info']})")
    
    def save_json_report(self, output_path):
        """Save results as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[OK] JSON report saved: {output_path}")
    
    def save_html_report(self, output_path):
        """Save results as HTML."""
        html = self._generate_html_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] HTML report saved: {output_path}")
    
    def _generate_html_report(self):
        """Generate HTML report."""
        summary = self.results["summary"]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Processing Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .timestamp {{ opacity: 0.9; font-size: 14px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary-card .label {{ color: #666; font-size: 14px; }}
        .error {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .info {{ color: #17a2b8; }}
        .success {{ color: #28a745; }}
        
        .file-section {{
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .file-header {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .file-header:hover {{ background: #e9ecef; }}
        .file-header .filename {{ font-weight: 600; }}
        .file-header .status {{
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status.passed {{ background: #d4edda; color: #155724; }}
        .status.failed {{ background: #f8d7da; color: #721c24; }}
        
        .violations {{
            padding: 20px;
            display: none;
        }}
        .file-section.expanded .violations {{ display: block; }}
        
        .violation {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #ddd;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .violation.error {{ border-left-color: #dc3545; }}
        .violation.warn {{ border-left-color: #ffc107; }}
        .violation.info {{ border-left-color: #17a2b8; }}
        
        .violation .severity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 8px;
        }}
        .violation.error .severity-badge {{ background: #dc3545; color: white; }}
        .violation.warn .severity-badge {{ background: #ffc107; color: #333; }}
        .violation.info .severity-badge {{ background: #17a2b8; color: white; }}
        
        .violation .rule-id {{ font-weight: 600; color: #495057; }}
        .violation .message {{ margin: 8px 0; color: #666; }}
        .violation .sentence {{
            background: white;
            padding: 10px;
            border-radius: 4px;
            margin: 8px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .violation .suggestion {{
            background: #e7f3ff;
            padding: 8px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 13px;
        }}
        
        .toggle-icon {{ transition: transform 0.3s; }}
        .file-section.expanded .toggle-icon {{ transform: rotate(90deg); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Batch Processing Report</h1>
            <div class="timestamp">Generated: {self.results['timestamp']}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Files</div>
                <div class="value">{summary['total_files']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Files Passed</div>
                <div class="value success">{summary['files_passed']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Files with Errors</div>
                <div class="value error">{summary['files_with_errors']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Sentences</div>
                <div class="value">{summary['total_sentences']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Errors</div>
                <div class="value error">{summary['errors']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Warnings</div>
                <div class="value warning">{summary['warnings']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Info</div>
                <div class="value info">{summary['info']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Violations</div>
                <div class="value">{summary['total_violations']}</div>
            </div>
        </div>
        
        <h2 style="margin: 30px 0 15px 0;">File Details</h2>
"""
        
        # Add file details
        for file_result in self.results["files"]:
            filename = Path(file_result["filename"]).name
            status = file_result.get("status", "unknown")
            
            html += f"""
        <div class="file-section" onclick="this.classList.toggle('expanded')">
            <div class="file-header">
                <div>
                    <span class="toggle-icon">▶</span>
                    <span class="filename">{filename}</span>
                    <small style="color: #666; margin-left: 10px;">
                        {file_result['violation_count']} violations
                        ({file_result['errors']} errors, {file_result['warnings']} warnings, {file_result['info']} info)
                    </small>
                </div>
                <span class="status {status}">{status.upper()}</span>
            </div>
            <div class="violations">
"""
            
            if file_result.get("violations"):
                for v in file_result["violations"]:
                    html += f"""
                <div class="violation {v['severity']}">
                    <div>
                        <span class="severity-badge">{v['severity']}</span>
                        <span class="rule-id">{v['rule_id']}</span>
                        <small style="color: #999;">Sentence {v['sentence_number']}</small>
                    </div>
                    <div class="message">{v['message']}</div>
                    <div class="sentence">"{v['sentence']}"</div>
                    {f'<div class="suggestion">💡 {v["suggestion"]}</div>' if v.get('suggestion') else ''}
                </div>
"""
            else:
                html += '<p style="padding: 20px; color: #28a745;">✅ No violations found!</p>'
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <script>
        // Expand first file with errors by default
        const filesWithErrors = document.querySelectorAll('.file-section .status.failed');
        if (filesWithErrors.length > 0) {
            filesWithErrors[0].closest('.file-section').classList.add('expanded');
        }
    </script>
</body>
</html>
"""
        return html
    
    def print_summary(self):
        """Print final summary to console."""
        summary = self.results["summary"]
        
        print("\n" + "=" * 80)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Total Files: {summary['total_files']}")
        print(f"Total Sentences: {summary['total_sentences']}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"\nFiles Passed: {summary['files_passed']}")
        print(f"Files with Errors: {summary['files_with_errors']}")
        print(f"\nErrors: {summary['errors']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Info: {summary['info']}")
        print("=" * 80)
        
        # Determine exit code recommendation
        if summary['errors'] > 0:
            print("\n[FAILED] Critical errors found - recommended exit code: 1")
            return 1
        else:
            print("\n[PASSED] All checks completed - recommended exit code: 0")
            return 0


def find_files(paths, pattern="*.md"):
    """Find files matching pattern from paths."""
    files = []
    
    for path in paths:
        path_obj = Path(path)
        
        if path_obj.is_file():
            files.append(path_obj)
        elif path_obj.is_dir():
            # Recursively find files in directory
            files.extend(path_obj.rglob(pattern))
        elif '*' in str(path):
            # Handle glob patterns
            parent = path_obj.parent
            files.extend(parent.glob(path_obj.name))
    
    return [str(f) for f in files]


def main():
    parser = argparse.ArgumentParser(
        description="Batch check documents for technical writing rule violations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/                          Check all files in docs/
  %(prog)s docs/*.md                      Check all markdown files
  %(prog)s file1.md file2.md              Check specific files
  %(prog)s docs/ --pattern "*.txt"        Check .txt files
  %(prog)s docs/ --errors-only            Show only errors
  %(prog)s docs/ --html report.html       Generate HTML report
  %(prog)s docs/ --json results.json      Generate JSON report
  %(prog)s docs/ --quiet                  Minimal output
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='+',
        help='Files or directories to check'
    )
    
    parser.add_argument(
        '--pattern',
        default='*.md',
        help='File pattern to match (default: *.md)'
    )
    
    parser.add_argument(
        '--errors-only',
        action='store_true',
        help='Only show error-level violations'
    )
    
    parser.add_argument(
        '--html',
        metavar='PATH',
        help='Generate HTML report at specified path'
    )
    
    parser.add_argument(
        '--json',
        metavar='PATH',
        help='Generate JSON report at specified path'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal console output'
    )
    
    parser.add_argument(
        '--fail-on-error',
        action='store_true',
        default=True,
        help='Exit with code 1 if errors found (default: True)'
    )
    
    args = parser.parse_args()
    
    # Banner
    if not args.quiet:
        print("=" * 80)
        print("BATCH DOCUMENT CHECKER")
        print("=" * 80)
        print()
    
    # Load rules
    if not args.quiet:
        print("Loading rules...")
    
    try:
        rules = load_rules()
        if not args.quiet:
            print(f"[OK] Loaded {len(rules)} rules")
    except Exception as e:
        print(f"[ERROR] Failed to load rules: {e}")
        return 1
    
    # Find files
    if not args.quiet:
        print(f"\nFinding files matching pattern: {args.pattern}")
    
    files = find_files(args.paths, args.pattern)
    
    if not files:
        print(f"[ERROR] No files found matching pattern: {args.pattern}")
        return 1
    
    if not args.quiet:
        print(f"[OK] Found {len(files)} file(s)")
    
    # Process files
    checker = BatchChecker(rules, show_progress=not args.quiet)
    results = checker.check_files(files, errors_only=args.errors_only)
    
    # Generate reports
    if args.json:
        checker.save_json_report(args.json)
    
    if args.html:
        checker.save_html_report(args.html)
    
    # Print summary
    exit_code = checker.print_summary()
    
    # Determine exit code
    if args.fail_on_error and results["summary"]["errors"] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
