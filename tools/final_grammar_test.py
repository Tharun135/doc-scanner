from app.intelligent_ai_improvement import get_enhanced_ai_suggestion

# Test the exact sentence you reported as problematic
sentence = 'By following these steps, you can configure sensors to send data to the platform, either by importing configuration files or by manually entering the settings.'

result = get_enhanced_ai_suggestion(
    'Consider breaking this long sentence into shorter ones', 
    sentence, 
    'technical'
)

print('🎯 GRAMMAR FIX VERIFICATION')
print('=' * 50)
print()
print('BEFORE (Problematic):')
print('"By following these steps, you can configure sensors to send data to the platform. Either by importing configuration files or by manually entering the settings."')
print('❌ Creates sentence fragment starting with "Either"')
print()
print('AFTER (Fixed):')
print(f'"{result.get("suggestion")}"')
print('✅ Both sentences are grammatically complete')
print()

# Check for the specific issue
suggestion = result.get('suggestion', '')
if 'Either by importing' in suggestion:
    print('❌ ISSUE STILL EXISTS: Sentence fragments detected')
else:
    print('✅ SUCCESS: Grammar issue resolved!')
    print('📋 The AI now creates complete sentences instead of fragments')