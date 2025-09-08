#!/usr/bin/env python3
"""
Test script to verify the rewriter improvements calculation is working correctly.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rewriter.ollama_rewriter import get_rewriter

def test_improvements_calculation():
    """Test the improvements calculation with sample text."""
    
    # Sample complex text that should show improvements
    test_text = """
    The implementation of advanced methodologies in the optimization of operational 
    efficiency through the utilization of cutting-edge technologies necessitates 
    a comprehensive understanding of multifaceted organizational dynamics. 
    Furthermore, the integration of these sophisticated systems requires extensive 
    coordination between various departmental stakeholders to ensure seamless 
    functionality and maximum return on investment.
    """
    
    print("🧪 Testing Rewriter Improvements Calculation")
    print("=" * 50)
    
    # Get rewriter instance
    rewriter = get_rewriter()
    
    # Calculate original readability
    print("📊 Original text readability:")
    original_scores = rewriter.calculate_readability(test_text)
    print(f"   Flesch Reading Ease: {original_scores['flesch_reading_ease']}")
    print(f"   Grade Level: {original_scores['flesch_kincaid_grade']}")
    print(f"   Text Length: {len(test_text)} characters")
    
    # Perform rewriting
    print("\n🔄 Rewriting document...")
    result = rewriter.rewrite_document(test_text, mode="simplicity")
    
    if result.get("success"):
        print("✅ Rewriting successful!")
        
        print("\n📈 Improvements Summary:")
        improvements = result.get("improvements", {})
        
        for metric, data in improvements.items():
            if isinstance(data, dict) and 'before' in data and 'after' in data:
                improvement = data.get('improvement', 0)
                sign = '+' if improvement > 0 else ''
                print(f"   {metric.replace('_', ' ').title()}:")
                print(f"      Before: {data['before']}")
                print(f"      After: {data['after']}")
                print(f"      Change: {sign}{improvement:.2f}")
                print()
        
        print("📝 Rewritten text preview:")
        print(f"   Original length: {len(test_text)} chars")
        print(f"   New length: {len(result.get('rewritten_text', ''))} chars")
        print(f"   First 100 chars: {result.get('rewritten_text', '')[:100]}...")
        
    else:
        print(f"❌ Rewriting failed: {result.get('error', 'Unknown error')}")
        
if __name__ == "__main__":
    test_improvements_calculation()
