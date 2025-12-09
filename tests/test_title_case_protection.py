#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import _fix_title_case_issues

def test_title_case_protection():
    """Test the title case protection function"""
    
    test_cases = [
        # Normal case (should not change)
        "The system demonstrates the installation steps in the following video:",
        
        # Title case issues (should be fixed)
        "The System Demonstrates The Installation Steps In The Following Video:",
        "When You Deploy A Project, The Metadata Is Also Published.",
        "The File Is Published By The Application System.",
        
        # Mixed case (should be fixed)
        "Installation Steps Are Demonstrated In The Following Video Guide.",
        
        # Technical terms (should preserve some capitalization)
        "The API Endpoint Configuration Is Managed By The System.",
        "Configure The SQL Database Connection Settings.",
        
        # Should not change (proper capitalization)
        "The system publishes the metadata automatically.",
        "When you deploy a project, the system handles the configuration."
    ]
    
    print("🛡️ Testing Title Case Protection")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nCase {i}:")
        print(f"Input:  {test_case}")
        
        result = _fix_title_case_issues(test_case)
        print(f"Output: {result}")
        
        if result != test_case:
            print("✅ FIXED: Title case corrected")
        else:
            print("→ No change needed")

if __name__ == "__main__":
    test_title_case_protection()
