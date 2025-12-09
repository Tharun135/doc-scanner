"""
Test the enhanced passive voice system with the specific "must be met" case.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testing Enhanced Passive Voice with 'must be met' Case...")

def test_must_be_met_case():
    """Test the specific 'must be met' passive voice case"""
    
    try:
        from production_passive_voice_ai import get_passive_voice_alternatives
        
        print("✅ Production Passive Voice AI loaded successfully")
        
        # Test the specific case from the user
        test_sentence = "The following requirements must be met:"
        test_feedback = "Avoid passive voice in sentence: 'The following requirements must be met:'"
        
        print(f"\n📝 TESTING SPECIFIC CASE:")
        print(f"Original: {test_sentence}")
        print(f"Feedback: {test_feedback}")
        print("-" * 60)
        
        result = get_passive_voice_alternatives(test_sentence, test_feedback)
        
        if result and result.get("suggestions"):
            print(f"✅ SUCCESS! Generated {len(result['suggestions'])} alternatives:")
            print(f"   Method: {result['method']}")
            print(f"   Confidence: {result['confidence']}")
            
            print(f"\n🎯 AI ALTERNATIVES:")
            for j, suggestion in enumerate(result["suggestions"], 1):
                print(f"\n   OPTION {j}: {suggestion['text']}")
                
                # Show the type of alternative
                source = suggestion.get('source', 'unknown')
                if source == 'template':
                    template = suggestion.get('template', '')
                    print(f"   📋 Template: {template}")
                elif source == 'synonym':
                    synonym = suggestion.get('synonym', 'alternative word')
                    print(f"   📝 Synonym: '{synonym}'")
                else:
                    print(f"   🔧 {source.title()} conversion")
            
            if result.get("explanation"):
                print(f"\n💡 EXPLANATION:")
                explanation_lines = result["explanation"].split('\n')
                for line in explanation_lines:
                    if line.strip():
                        print(f"   {line}")
            
            # Show detected patterns
            if result.get("detected_patterns"):
                print(f"\n🔍 DETECTED PATTERNS:")
                for pattern_info in result["detected_patterns"]:
                    print(f"   - Pattern: '{pattern_info['pattern']}'")
                    if pattern_info.get('context', {}).get('subject'):
                        print(f"     Subject: '{pattern_info['context']['subject']}'")
        else:
            print("❌ No alternatives generated")
            if result:
                print(f"Result: {result}")
        
        # Test additional modal passive voice cases
        additional_cases = [
            "These steps must be completed before proceeding.",
            "All fields must be filled out correctly.",
            "The criteria must be satisfied for approval.",
            "Safety protocols must be followed at all times."
        ]
        
        print(f"\n{'='*60}")
        print("🧪 TESTING ADDITIONAL MODAL PASSIVE CASES")
        print(f"{'='*60}")
        
        for i, case in enumerate(additional_cases, 1):
            print(f"\n📝 Additional Test {i}:")
            print(f"Original: {case}")
            
            result = get_passive_voice_alternatives(case, "Convert modal passive voice to active")
            
            if result and result.get("suggestions"):
                print(f"✅ Generated {len(result['suggestions'])} alternatives:")
                for j, suggestion in enumerate(result["suggestions"][:2], 1):  # Show top 2
                    print(f"   {j}. {suggestion['text']}")
            else:
                print("❌ No alternatives generated")
    
    except ImportError as e:
        print(f"❌ Could not load production passive voice AI: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_integration_with_main_system():
    """Test integration with the main AI system"""
    
    print(f"\n{'='*60}")
    print("🔗 TESTING INTEGRATION WITH MAIN AI SYSTEM")
    print(f"{'='*60}")
    
    try:
        from app.ai_improvement_clean import AISuggestionEngine
        
        ai_engine = AISuggestionEngine()
        print(f"✅ AI System loaded successfully")
        
        # Test the specific case through the main system
        test_sentence = "The following requirements must be met:"
        test_feedback = "Avoid passive voice in sentence: 'The following requirements must be met:'"
        
        print(f"\nTesting through main AI system:")
        print(f"Sentence: {test_sentence}")
        print(f"Feedback: {test_feedback}")
        
        result = ai_engine.generate_contextual_suggestion(
            feedback_text=test_feedback,
            sentence_context=test_sentence,
            document_type="technical",
            option_number=1
        )
        
        if result:
            print(f"\n✅ Main system generated suggestion:")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 'unknown')}")
            print(f"   Suggestion:")
            
            # Handle multi-line suggestions
            suggestion_lines = result.get('suggestion', '').split('\n')
            for line in suggestion_lines:
                if line.strip():
                    if line.strip().startswith('OPTION'):
                        print(f"     🎯 {line}")
                    elif line.strip().startswith('WHY:'):
                        print(f"     💡 {line}")
                    else:
                        print(f"       {line}")
        else:
            print("❌ No suggestion generated by main system")
    
    except ImportError as e:
        print(f"❌ Could not load AI system: {e}")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    test_must_be_met_case()
    test_integration_with_main_system()
