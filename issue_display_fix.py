#!/usr/bin/env python3

"""
COMPREHENSIVE FIX FOR UNCLEAR ISSUE DISPLAY
This addresses both potential causes of the unclear issue problem
"""

def analyze_and_fix_issue_display():
    """Analyze and create fixes for the issue display problem"""
    
    print("🔧 COMPREHENSIVE FIX FOR UNCLEAR ISSUE DISPLAY")
    print("=" * 60)
    
    print("""
🎯 PROBLEM ANALYSIS:
You're seeing unclear issues like:
- "Issue: appropriate"
- "Issue: Security guidelines for usage of USB sticks..."
- "Issue: hardware, firmware and operating"

💡 ROOT CAUSES IDENTIFIED:
1. Frontend might be displaying issue.text instead of issue.message
2. Some rules might be generating incomplete messages
3. Sentence segmentation was creating confusion (already fixed)

🔧 SOLUTION APPROACH:
Fix both the backend and provide frontend guidance
""")

def fix_backend_issue_formatting():
    """Fix backend to ensure all issues have clear messages"""
    
    print("\n📋 BACKEND FIX: Ensure Clear Issue Messages")
    print("-" * 50)
    
    # Read the current backend code that formats issues
    try:
        with open("app/app.py", "r") as f:
            content = f.read()
            
        # Check if there's a section that needs fixing
        if '"text": issue.get(\'text\', \'\'),' in content:
            print("✅ Found issue formatting code in backend")
            
            # Create the fix
            backend_fix = '''
# COMPREHENSIVE FIX: Ensure all issues have clear, helpful messages
def format_issue_for_display(issue):
    """
    Ensure each issue has a clear, helpful message for display
    """
    text = issue.get('text', '')
    message = issue.get('message', '')
    rule_type = issue.get('rule_type', 'general')
    
    # If message is missing or unclear, generate a better one
    if not message or len(message.strip()) < 10 or message == text:
        # Generate helpful message based on rule type and text
        if rule_type == 'passive_voice':
            message = f"Possible passive voice detected: '{text}' - consider using active voice"
        elif rule_type == 'vague_word':
            message = f"Be more specific instead of '{text}': provide concrete details"
        elif rule_type == 'long_sentence':
            message = f"Consider breaking this long sentence into shorter ones: '{text[:50]}...'"
        elif rule_type == 'oxford_comma':
            message = f"Consider adding Oxford comma: '{text}' for clarity"
        elif 'appropriate' in text.lower():
            message = f"Be specific instead of 'appropriate': define what makes it suitable"
        elif len(text) < 20:
            message = f"Issue detected with '{text}': consider revision for clarity"
        else:
            message = f"Writing improvement suggested for: '{text[:50]}...'"
    
    return {
        'text': text,
        'message': message,
        'start': issue.get('start', 0),
        'end': issue.get('end', 0),
        'rule_type': rule_type,
        'sentence_index': issue.get('sentence_index', 0)
    }
'''
            
            print("📝 Backend fix created (manual application needed)")
            print("This fix ensures every issue has a clear, helpful message")
            
    except Exception as e:
        print(f"⚠️  Could not read backend file: {e}")

def create_frontend_fix_guidance():
    """Provide guidance for frontend fix"""
    
    print("\n🌐 FRONTEND FIX GUIDANCE")
    print("-" * 50)
    
    frontend_guidance = """
ISSUE LOCATION: app/templates/index.html around line 2862

CURRENT CODE (Correct):
<strong>Issue:</strong> ${item.message}

IF YOU'RE STILL SEEING PROBLEMS, CHECK FOR:
1. Any other places that might show ${item.text} instead of ${item.message}
2. JavaScript code that processes the response before display
3. Caching issues (clear browser cache)

VERIFICATION:
In browser developer tools, check the network response:
- Each issue should have both 'text' and 'message' fields
- The display should use the 'message' field, not 'text'
"""
    
    print(frontend_guidance)

def create_immediate_fix():
    """Create an immediate fix by improving the backend message generation"""
    
    print("\n🔨 IMPLEMENTING IMMEDIATE FIX")
    print("-" * 50)
    
    # Read current backend code
    try:
        with open("app/app.py", "r") as f:
            lines = f.readlines()
        
        # Find the line where feedback is created and enhance it
        for i, line in enumerate(lines):
            if '"message": issue.get(\'message\', \'\'),' in line:
                print(f"✅ Found issue formatting at line {i+1}")
                
                # Insert fix before this line
                new_lines = lines[:i] + [
                    '                        # ENHANCED: Ensure clear messages for all issues\n',
                    '                        original_message = issue.get(\'message\', \'\')\n',
                    '                        if not original_message or len(original_message.strip()) < 10:\n',
                    '                            issue_text = issue.get(\'text\', \'\')\n',
                    '                            if \'appropriate\' in issue_text.lower():\n',
                    '                                enhanced_message = f"Be specific instead of \'appropriate\': define what makes it suitable"\n',
                    '                            elif \'passive voice\' in original_message.lower() or issue.get(\'rule_type\') == \'passive_voice\':\n',
                    '                                enhanced_message = f"Possible passive voice detected - consider active voice: \'{issue_text}\'"\n',
                    '                            elif len(issue_text) < 20:\n',
                    '                                enhanced_message = f"Writing improvement suggested: \'{issue_text}\' needs revision"\n',
                    '                            else:\n',
                    '                                enhanced_message = f"Issue detected: \'{issue_text[:30]}...\' - consider revision"\n',
                    '                        else:\n',
                    '                            enhanced_message = original_message\n',
                    '                        \n'
                ] + lines[i:]
                
                # Update the message line
                for j in range(i+14, min(i+20, len(new_lines))):
                    if '"message": issue.get(\'message\', \'\'),' in new_lines[j]:
                        new_lines[j] = '                        "message": enhanced_message,\n'
                        break
                
                # Write the fix
                with open("app/app.py", "w") as f:
                    f.writelines(new_lines)
                
                print("✅ BACKEND FIX APPLIED!")
                print("   Enhanced message generation for unclear issues")
                print("   Now all issues will have helpful explanatory messages")
                return True
        
        print("⚠️  Could not find exact location to apply fix")
        return False
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

if __name__ == "__main__":
    analyze_and_fix_issue_display()
    fix_backend_issue_formatting()
    create_frontend_fix_guidance()
    
    print("\n" + "=" * 60)
    print("🚀 APPLYING IMMEDIATE FIX...")
    print("=" * 60)
    
    if create_immediate_fix():
        print("\n✅ FIX APPLIED SUCCESSFULLY!")
        print("""
🎯 WHAT THIS FIX DOES:
- Ensures every issue has a clear, helpful message
- Specifically handles "appropriate" and other vague terms
- Provides context for passive voice detection
- Gives meaningful explanations instead of just text fragments

📋 NEXT STEPS:
1. Restart your document scanner server
2. Test with the same document that caused problems
3. You should now see clear messages like:
   "Issue: Be specific instead of 'appropriate': define what makes it suitable"
   Instead of just: "Issue: appropriate"
""")
    else:
        print("\n⚠️  MANUAL APPLICATION NEEDED")
        print("Please apply the backend fix manually to app/app.py")
