#!/usr/bin/env python3
"""
Direct Backend Test - No Flask
Test the backend rule processing directly to see what's really happening
"""

import sys
sys.path.append('app')

def test_backend_directly():
    """Test backend without Flask to isolate the issue"""
    
    print("🔍 TESTING BACKEND DIRECTLY (NO FLASK)")
    print("=" * 60)
    
    try:
        # Import backend functions
        from app.app import get_rules, review_document
        
        # Test content - same as what user would upload
        test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
        
        print(f"Test content length: {len(test_content)} characters")
        print(f"Content: {test_content[:150]}...")
        print("=" * 60)
        
        # Load rules
        print("📚 Loading rules...")
        rules = get_rules()
        print(f"✅ Loaded {len(rules)} rules")
        
        # Test document review
        print("\n🔧 Running review_document...")
        result = review_document(test_content, rules)
        
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'issues' in result:
            issues = result['issues']
            print(f"\n📊 ISSUES ANALYSIS:")
            print(f"Total issues found: {len(issues)}")
            
            if len(issues) == 0:
                print("❌ NO ISSUES DETECTED - This is the core problem!")
                print("   Backend is not detecting any issues at all")
                return
            
            # Categorize issues
            issue_breakdown = {}
            
            print(f"\nDetailed issues:")
            for i, issue in enumerate(issues):
                if isinstance(issue, dict):
                    message = issue.get('message', 'No message')
                    print(f"  {i+1}. {message}")
                    
                    # Categorize
                    message_lower = message.lower()
                    if 'passive voice' in message_lower:
                        issue_breakdown['Passive Voice'] = issue_breakdown.get('Passive Voice', 0) + 1
                    elif 'long sentence' in message_lower:
                        issue_breakdown['Long Sentence'] = issue_breakdown.get('Long Sentence', 0) + 1
                    elif 'modifier' in message_lower and ('very' in message_lower or 'unnecessary' in message_lower):
                        issue_breakdown['Unnecessary Modifiers'] = issue_breakdown.get('Unnecessary Modifiers', 0) + 1
                    elif 'verbose' in message_lower or 'utiliz' in message_lower or 'simplif' in message_lower:
                        issue_breakdown['Verbose Language'] = issue_breakdown.get('Verbose Language', 0) + 1
                    elif 'weak verb' in message_lower or 'nominalization' in message_lower:
                        issue_breakdown['Weak Verbs'] = issue_breakdown.get('Weak Verbs', 0) + 1
                    else:
                        issue_breakdown['Other'] = issue_breakdown.get('Other', 0) + 1
                else:
                    print(f"  {i+1}. {str(issue)}")
                    issue_breakdown['Unknown Format'] = issue_breakdown.get('Unknown Format', 0) + 1
            
            print(f"\n🎯 ISSUE BREAKDOWN:")
            for issue_type, count in issue_breakdown.items():
                print(f"  {issue_type}: {count}")
            
            if len(issue_breakdown) == 1 and 'Passive Voice' in issue_breakdown:
                print(f"\n⚠️  CONFIRMED: Only passive voice is being detected")
                print(f"   This means other rules are not triggering")
                print(f"   Need to investigate why other rules aren't working")
            elif len(issue_breakdown) > 1:
                print(f"\n✅ Multiple issue types detected in backend")
                print(f"   Backend is working - issue is in Flask distribution")
            else:
                print(f"\n❓ Unexpected issue pattern detected")
            
        else:
            print(f"❌ Unexpected result format: {result}")
            
    except Exception as e:
        print(f"❌ Error testing backend: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_directly()
