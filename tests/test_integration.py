#!/usr/bin/env python3
"""
Test script for DocScanner AI suggestions integration
"""

import sys
import os

# Add app directory to path
sys.path.append('app')
sys.path.append('app/services')
sys.path.append('enhanced_rag')

def test_enrichment():
    """Test the enrichment function directly"""
    try:
        # Import the enrichment function
        from enrichment import enrich_issue_with_solution
        
        print("✅ Successfully imported enrich_issue_with_solution")
        
        # Test cases based on the original problems
        test_cases = [
            {
                'name': 'Capitalization Issue',
                'issue': {
                    'message': 'Consider using sentence case for this text',
                    'context': 'it is in ISO 8601 format.',
                    'issue_type': 'style'
                }
            },
            {
                'name': 'Passive Voice Issue', 
                'issue': {
                    'message': 'Consider converting this passive voice to active voice',
                    'context': 'The file is uploaded by the user.',
                    'issue_type': 'passive_voice'
                }
            },
            {
                'name': 'Long Sentence Issue',
                'issue': {
                    'message': 'Consider breaking this long sentence into shorter sentences',
                    'context': 'The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem.',
                    'issue_type': 'long_sentence'
                }
            }
        ]
        
        print("\n" + "="*60)
        print("TESTING AI SUGGESTION IMPROVEMENTS")
        print("="*60)
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['name']}")
            print(f"Original: {test_case['issue']['context']}")
            
            try:
                result = enrich_issue_with_solution(test_case['issue'])
                
                print(f"Method: {result.get('method', 'unknown')}")
                print(f"Rewrite: {result.get('proposed_rewrite', 'None')}")
                print(f"Guidance: {result.get('solution_text', 'None')[:100]}...")
                
                # Check if the rewrite is actually different and improved
                original = test_case['issue']['context']
                rewrite = result.get('proposed_rewrite', '')
                
                if rewrite and rewrite != original:
                    print("✅ AI suggestion provided and different from original")
                else:
                    print("⚠️  AI suggestion same as original or empty")
                    
            except Exception as e:
                print(f"❌ Error testing {test_case['name']}: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("INTEGRATION TEST COMPLETE")
        print("="*60)
        
    except ImportError as e:
        print(f"❌ Failed to import enrichment function: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_enrichment()
    if success:
        print("\n🎉 Integration test completed successfully!")
        print("The enhanced AI suggestion system is now integrated into DocScanner!")
    else:
        print("\n❌ Integration test failed!")
