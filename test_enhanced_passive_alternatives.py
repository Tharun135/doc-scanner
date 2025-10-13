"""
Test script to demonstrate the enhanced passive voice resolution with AI-generated alternatives.
Shows how the system can generate multiple active voice suggestions using different words.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testing Enhanced Passive Voice Resolution with Multiple AI Alternatives...")

def test_enhanced_passive_voice():
    """Test the enhanced passive voice system"""
    
    try:
        from enhanced_passive_voice_alternatives import EnhancedPassiveVoiceResolver
        
        print("✅ Enhanced Passive Voice Resolver loaded successfully")
        resolver = EnhancedPassiveVoiceResolver()
        
        if not resolver.is_initialized:
            print("⚠️  RAG system not initialized - will use fallback patterns")
        else:
            print(f"✅ RAG system initialized with model: {resolver.model}")
        
        # Test cases from real usage
        test_cases = [
            {
                "sentence": "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.",
                "feedback": "Avoid passive voice in sentence"
            },
            {
                "sentence": "The Time, Description, and Comments columns are fixed and cannot be removed.",
                "feedback": "Convert to active voice"
            },
            {
                "sentence": "Docker logs are not generated when there are no active applications.",
                "feedback": "Convert to active voice: 'The Docker daemon does not generate logs when no applications are running.'"
            },
            {
                "sentence": "The configuration options are displayed in the Settings panel.",
                "feedback": "Passive voice detected - convert to active voice"
            },
            {
                "sentence": "Data is processed automatically by the system when files are uploaded.",
                "feedback": "Multiple passive voice instances - convert to active"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"📝 TEST CASE {i}")
            print(f"{'='*80}")
            print(f"Original Sentence:")
            print(f"   {test_case['sentence']}")
            print(f"\nFeedback:")
            print(f"   {test_case['feedback']}")
            print(f"\n{'🔄 GENERATING ALTERNATIVES...'}")
            
            # Generate alternatives
            result = resolver.generate_passive_voice_alternatives(
                test_case['sentence'], 
                test_case['feedback']
            )
            
            if result and result.get("suggestions"):
                print(f"\n✅ SUCCESS: Generated {len(result['suggestions'])} alternatives")
                print(f"Method: {result['method']}")
                print(f"Confidence: {result['confidence']}")
                
                print(f"\n🎯 ALTERNATIVES:")
                for j, suggestion in enumerate(result["suggestions"], 1):
                    print(f"\n   OPTION {j}: {suggestion['text']}")
                    print(f"   Source: {suggestion.get('source', 'unknown').upper()}")
                    if suggestion.get('strategy'):
                        print(f"   Strategy: {suggestion['strategy']}")
                    if suggestion.get('pattern'):
                        print(f"   Pattern: {suggestion['pattern']}")
                    if suggestion.get('synonym_verb'):
                        print(f"   Synonym: {suggestion['original_verb']} → {suggestion['synonym_verb']}")
                
                if result.get("explanation"):
                    print(f"\n💡 EXPLANATION:")
                    print(f"   {result['explanation']}")
                
                # Show analysis if available
                if result.get("analysis"):
                    analysis = result["analysis"]
                    print(f"\n🔍 ANALYSIS:")
                    print(f"   Detected patterns: {len(analysis.get('passive_patterns', []))}")
                    if analysis.get('passive_patterns'):
                        for pattern in analysis['passive_patterns']:
                            print(f"   - {pattern['type']}: '{pattern['full_match']}'")
                    print(f"   Complexity: {analysis.get('complexity', 'unknown')}")
                    print(f"   Word count: {analysis.get('length', 0)}")
            else:
                print("❌ No alternatives generated")
                if result:
                    print(f"Result: {result}")
        
        print(f"\n{'='*80}")
        print("🎉 ENHANCED PASSIVE VOICE TEST COMPLETE")
        print("💡 The system can generate multiple active voice alternatives using:")
        print("   • Different action verbs (synonyms)")
        print("   • Different sentence subjects") 
        print("   • Different sentence structures")
        print("   • RAG-enhanced word variety")
        print("   • Pattern-based transformations")
        print(f"{'='*80}")
        
    except ImportError as e:
        print(f"❌ Could not load enhanced passive voice resolver: {e}")
        print("   Make sure enhanced_passive_voice_alternatives.py is available")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_integration_with_ai_system():
    """Test integration with the main AI improvement system"""
    
    print(f"\n{'='*80}")
    print("🔗 TESTING INTEGRATION WITH MAIN AI SYSTEM")
    print(f"{'='*80}")
    
    try:
        from app.ai_improvement_clean import AISuggestionEngine
        
        print("✅ AI Suggestion Engine loaded successfully")
        ai_engine = AISuggestionEngine()
        
        # Test a passive voice case
        test_sentence = "The Time, Description, and Comments columns are fixed and cannot be removed."
        test_feedback = "Convert to active voice"
        
        print(f"\nTesting with main AI system:")
        print(f"Sentence: {test_sentence}")
        print(f"Feedback: {test_feedback}")
        
        # Test different options (simulating regenerate functionality)
        for option_num in [1, 2, 3]:
            print(f"\n🔄 Generating OPTION {option_num}...")
            
            result = ai_engine.generate_contextual_suggestion(
                feedback_text=test_feedback,
                sentence_context=test_sentence,
                option_number=option_num
            )
            
            if result:
                print(f"✅ Generated suggestion:")
                print(f"   Method: {result.get('method', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 'unknown')}")
                print(f"   Suggestion:")
                # Handle multi-line suggestions
                suggestion_lines = result.get('suggestion', '').split('\n')
                for line in suggestion_lines:
                    if line.strip():
                        print(f"     {line}")
            else:
                print(f"❌ No suggestion generated for option {option_num}")
        
        print(f"\n✅ Integration test complete!")
        
    except ImportError as e:
        print(f"❌ Could not load AI suggestion engine: {e}")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_passive_voice()
    test_integration_with_ai_system()
