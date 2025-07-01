#!/usr/bin/env python3
"""
Comprehensive test script for the improved long sentence rule.
"""

import sys
import os
sys.path.append('app')

# Import the updated long sentences rule
from rules import long_sentences

def test_comprehensive_cases():
    """Test various types of long sentences to ensure the breaking works correctly."""
    
    test_cases = [
        {
            "name": "Parenthetical with abbreviation",
            "text": "The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem."
        },
        {
            "name": "Long list with conjunctions", 
            "text": "The comprehensive software development process includes detailed requirements analysis, thorough system design, careful implementation, extensive testing, strategic deployment, and ongoing maintenance activities that ensure quality delivery to customers."
        },
        {
            "name": "Complex technical sentence with multiple clauses",
            "text": "This advanced configuration file specifies the critical network parameters, security settings, authentication protocols, and comprehensive monitoring capabilities that the distributed system will use during runtime operations across multiple environments."
        },
        {
            "name": "Relative clause sentence",
            "text": "The high-performance application server, which handles all incoming user requests and processes complex business logic efficiently, must be configured with appropriate memory settings and optimized connection pools for maximum throughput."
        },
        {
            "name": "Long descriptive sentence with multiple actions",
            "text": "Authorized users can access the comprehensive dashboard through the secure web interface to view real-time analytics, generate detailed custom reports, manage granular user permissions, and configure advanced system settings according to organizational requirements."
        },
        {
            "name": "Sentence with 'and' conjunction",
            "text": "The system automatically processes incoming data streams from multiple sources and transforms them into standardized formats that can be easily analyzed by downstream applications and reporting tools."
        },
        {
            "name": "Sentence with relative clause 'which'",
            "text": "The new security protocol, which was developed specifically for handling sensitive customer data, implements advanced encryption methods and provides comprehensive audit trails for compliance monitoring purposes."
        }
    ]
    
    print("Testing improved long sentence rule with various sentence types...")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Input: \"{test_case['text']}\"")
        print()
        
        # Run the check
        suggestions = long_sentences.check(test_case['text'])
        
        if suggestions:
            for j, suggestion in enumerate(suggestions, 1):
                print(f"Suggestion {j}:")
                lines = suggestion.split('\n')
                for line in lines:
                    if line.strip().startswith('Issue:'):
                        print(f"  {line}")
                    elif line.strip().startswith('Original sentence:'):
                        print(f"  {line}")
                    elif line.strip().startswith('AI Solution:'):
                        print(f"  {line}")
                        # Extract and format the solution for better readability
                        solution = line.replace('AI Solution:', '').strip().strip('"')
                        print(f"  Improved: \"{solution}\"")
        else:
            print("  No suggestions found (sentence is under 25 words)")
        
        print()
    
    print("=" * 80)

if __name__ == "__main__":
    test_comprehensive_cases()
