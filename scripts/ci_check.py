"""
CI/CD Integration Script
Run rule checks as part of continuous integration pipeline.
Exit with error code if critical violations found.
"""
import sys
import json
from app.rules.loader import load_rules
from app.rules.matcher import apply_rules

def check_files_for_ci(file_paths, fail_on_error=True, fail_on_warn=False):
    """
    Check files and return appropriate exit code for CI/CD.
    
    Args:
        file_paths (list): List of file paths to check
        fail_on_error (bool): Exit with code 1 if errors found
        fail_on_warn (bool): Exit with code 1 if warnings found
    
    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    rules = load_rules()
    
    total_errors = 0
    total_warnings = 0
    total_info = 0
    
    print("=" * 80)
    print("RULE COMPLIANCE CHECK (CI/CD)")
    print("=" * 80)
    
    for file_path in file_paths:
        print(f"\nChecking: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic sentence splitting
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            file_errors = 0
            file_warnings = 0
            file_info = 0
            
            for sentence in sentences:
                violations = apply_rules(sentence, rules)
                
                for v in violations:
                    if v["severity"] == "error":
                        file_errors += 1
                        total_errors += 1
                        print(f"  [ERROR] {v['rule_id']}: {v['message']}")
                    elif v["severity"] == "warn":
                        file_warnings += 1
                        total_warnings += 1
                        if fail_on_warn:
                            print(f"  [WARN] {v['rule_id']}: {v['message']}")
                    else:
                        file_info += 1
                        total_info += 1
            
            print(f"  Results: {file_errors} errors, {file_warnings} warnings, {file_info} info")
            
        except Exception as e:
            print(f"  [ERROR] Failed to process file: {e}")
            total_errors += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Total Info: {total_info}")
    
    # Determine exit code
    if fail_on_error and total_errors > 0:
        print("\n❌ FAILED: Critical errors found")
        return 1
    elif fail_on_warn and total_warnings > 0:
        print("\n❌ FAILED: Warnings found")
        return 1
    else:
        print("\n✅ PASSED: All checks completed")
        return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check files for rule compliance")
    parser.add_argument("files", nargs="+", help="Files to check")
    parser.add_argument("--fail-on-error", action="store_true", default=True,
                       help="Fail if errors found (default: True)")
    parser.add_argument("--fail-on-warn", action="store_true", default=False,
                       help="Fail if warnings found (default: False)")
    
    args = parser.parse_args()
    
    exit_code = check_files_for_ci(args.files, args.fail_on_error, args.fail_on_warn)
    sys.exit(exit_code)
