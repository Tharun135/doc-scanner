"""
Batch Processing Module
Process multiple documents and generate compliance reports.
"""
import os
import json
from pathlib import Path
from datetime import datetime

class BatchProcessor:
    """Process multiple documents for rule compliance."""
    
    def __init__(self, rules, output_dir="batch_reports"):
        self.rules = rules
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def process_directory(self, dir_path, file_pattern="*.md"):
        """
        Process all matching files in a directory.
        
        Args:
            dir_path (str): Directory to scan
            file_pattern (str): Glob pattern for files
        
        Returns:
            dict: Batch processing results
        """
        from app.rules.matcher import apply_rules
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "directory": dir_path,
            "pattern": file_pattern,
            "files": [],
            "summary": {
                "total_files": 0,
                "total_sentences": 0,
                "total_violations": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0
            }
        }
        
        # Find all matching files
        path = Path(dir_path)
        files = list(path.glob(file_pattern))
        
        results["summary"]["total_files"] = len(files)
        
        for file_path in files:
            file_result = self._process_file(file_path)
            results["files"].append(file_result)
            
            # Update summary
            results["summary"]["total_sentences"] += file_result["sentence_count"]
            results["summary"]["total_violations"] += file_result["violation_count"]
            results["summary"]["errors"] += file_result["errors"]
            results["summary"]["warnings"] += file_result["warnings"]
            results["summary"]["info"] += file_result["info"]
        
        # Save report
        report_path = self._save_report(results)
        results["report_path"] = report_path
        
        return results
    
    def _process_file(self, file_path):
        """Process a single file."""
        from app.rules.matcher import apply_rules
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into sentences (basic)
        sentences = content.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        file_result = {
            "filename": str(file_path),
            "sentence_count": len(sentences),
            "violation_count": 0,
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "violations": []
        }
        
        # Apply rules to each sentence
        for sentence in sentences:
            violations = apply_rules(sentence, self.rules)
            
            for v in violations:
                file_result["violation_count"] += 1
                if v["severity"] == "error":
                    file_result["errors"] += 1
                elif v["severity"] == "warn":
                    file_result["warnings"] += 1
                else:
                    file_result["info"] += 1
                
                file_result["violations"].append({
                    "sentence": sentence[:100],  # Truncate for report
                    "rule_id": v["rule_id"],
                    "severity": v["severity"],
                    "message": v["message"]
                })
        
        return file_result
    
    def _save_report(self, results):
        """Save batch report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"batch_report_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Also create HTML report
        html_path = report_path.replace('.json', '.html')
        self._create_html_report(results, html_path)
        
        return report_path
    
    def _create_html_report(self, results, output_path):
        """Create HTML version of batch report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Batch Processing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .error {{ color: #d9534f; }}
        .warn {{ color: #f0ad4e; }}
        .info {{ color: #5bc0de; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .file-section {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>Batch Processing Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Directory:</strong> {results['directory']}</p>
        <p><strong>Pattern:</strong> {results['pattern']}</p>
        <p><strong>Timestamp:</strong> {results['timestamp']}</p>
        <p><strong>Total Files:</strong> {results['summary']['total_files']}</p>
        <p><strong>Total Sentences:</strong> {results['summary']['total_sentences']}</p>
        <p><strong>Total Violations:</strong> {results['summary']['total_violations']}</p>
        <p class="error"><strong>Errors:</strong> {results['summary']['errors']}</p>
        <p class="warn"><strong>Warnings:</strong> {results['summary']['warnings']}</p>
        <p class="info"><strong>Info:</strong> {results['summary']['info']}</p>
    </div>
"""
        
        for file_result in results['files']:
            html += f"""
    <div class="file-section">
        <h3>{file_result['filename']}</h3>
        <p>Sentences: {file_result['sentence_count']} | Violations: {file_result['violation_count']}</p>
        <p class="error">Errors: {file_result['errors']}</p>
        <p class="warn">Warnings: {file_result['warnings']}</p>
        <p class="info">Info: {file_result['info']}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
