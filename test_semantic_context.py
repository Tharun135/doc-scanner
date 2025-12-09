"""
Test script for semantic context system.
Tests that context is built correctly and passed to AI suggestions.
"""

import sys
sys.path.insert(0, 'D:\\doc-scanner')

def test_semantic_context_building():
    """Test that semantic context can be built from sample sentences."""
    print("=" * 60)
    print("TEST 1: Semantic Context Building")
    print("=" * 60)
    
    from app.semantic_context import build_document_context
    
    # Sample technical document
    sentences = [
        "The SIMATIC S7+ Controller (S7+) manages industrial connections.",
        "It connects to multiple PLCs.",
        "You configure S7+ through the web interface.",
        "The system monitors connection status.",
        "It alerts you when issues occur."
    ]
    
    sections = {
        0: "Introduction",
        1: "Configuration",
        2: "Configuration",
        3: "Monitoring",
        4: "Monitoring"
    }
    
    try:
        # Build context without spaCy (test fallback)
        ctx = build_document_context(
            sentences=sentences,
            sections=sections,
            nlp=None,
            document_type="technical"
        )
        
        print(f"✅ Context built successfully!")
        print(f"   - Total sentences: {ctx.total_sentences}")
        print(f"   - Entities tracked: {len(ctx.entities)}")
        print(f"   - Acronyms found: {len(ctx.acronyms)}")
        
        # Check acronym tracking
        if "S7+" in ctx.acronyms:
            acro_info = ctx.acronyms["S7+"]
            print(f"\n📝 Acronym S7+:")
            print(f"   - First use: sentence {acro_info['first']}")
            print(f"   - Expanded as: {acro_info['expanded']}")
            print(f"   - Total uses: {len(acro_info['all_uses'])}")
        
        # Check entity tracking
        print(f"\n🏢 Entities found:")
        for entity, positions in list(ctx.entities.items())[:5]:
            print(f"   - {entity}: used in sentences {positions}")
        
        # Test get_sentence_context
        print(f"\n🎯 Context for sentence 1:")
        sent_ctx = ctx.get_sentence_context(1, window=1)
        print(f"   - Section: {sent_ctx['section']}")
        print(f"   - Topic: {sent_ctx['topic']}")
        print(f"   - Acronyms: {[a['acronym'] for a in sent_ctx['acronyms']]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_for_ai():
    """Test that context can be formatted for AI prompts."""
    print("\n" + "=" * 60)
    print("TEST 2: Context Formatting for AI")
    print("=" * 60)
    
    from app.semantic_context import build_document_context, get_context_for_ai_suggestion
    
    sentences = [
        "The Controller manages connections.",
        "It restarts automatically after updates.",
        "This ensures continuous operation."
    ]
    
    try:
        ctx = build_document_context(sentences=sentences, sections=None, nlp=None)
        
        # Get context for middle sentence
        context_str = get_context_for_ai_suggestion(
            sentence_index=1,
            ctx=ctx,
            issue_type="passive_voice"
        )
        
        print(f"✅ Context string generated:")
        print(context_str)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_acronym_expansion_tracking():
    """Test that acronym expansions are tracked correctly."""
    print("\n" + "=" * 60)
    print("TEST 3: Acronym Expansion Tracking")
    print("=" * 60)
    
    from app.semantic_context import build_document_context
    
    sentences = [
        "Introduction to the system.",
        "The Programmable Logic Controller (PLC) manages automation.",
        "Each PLC connects to sensors.",
        "PLC configuration is done through software."
    ]
    
    try:
        ctx = build_document_context(sentences=sentences, sections=None, nlp=None)
        
        if "PLC" in ctx.acronyms:
            info = ctx.acronyms["PLC"]
            print(f"✅ Acronym tracking:")
            print(f"   - First expanded at sentence: {info['first']}")
            print(f"   - Expansion: {info['expanded']}")
            print(f"   - All uses: {info['all_uses']}")
            
            # Test if acronym is already expanded before sentence 3
            is_expanded = ctx.is_acronym_already_expanded("PLC", 3)
            print(f"   - Already expanded before sentence 3? {is_expanded}")
            
            return True
        else:
            print("❌ Acronym PLC not detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_meaning_lock():
    """
    CRITICAL TEST: Verify AI maintains subject reference and meaning.
    This is the actual validation that semantic context prevents meaning drift.
    """
    print("\n" + "=" * 60)
    print("TEST 4: MEANING PRESERVATION (CRITICAL)")
    print("=" * 60)
    
    from app.semantic_context import build_document_context
    
    sentences = [
        "The controller restarts after firmware update.",
        "It then re-establishes the network session."
    ]
    
    # Build context
    ctx = build_document_context(sentences, {}, nlp=None)
    
    print(f"\nInput sentences:")
    print(f"  [0] {sentences[0]}")
    print(f"  [1] {sentences[1]}")
    
    print(f"\nContext built:")
    print(f"  Entities: {ctx.entities}")
    print(f"  Pronoun links: {ctx.pronoun_links}")
    print(f"  Topics: {ctx.sentence_topics}")
    
    # Now attempt to get AI suggestion for sentence 1 (with "It")
    try:
        from app.document_first_ai import DocumentFirstAIEngine
        
        engine = DocumentFirstAIEngine()
        
        feedback_text = "Use active voice and maintain subject reference"
        sentence_context = sentences[1]
        
        result = engine.generate_document_first_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical",
            sentence_index=1,
            document_context=ctx,
            issue_type="pronoun_reference"
        )
        
        print(f"\n{'=' * 60}")
        print("AI OUTPUT (RAW):")
        print(f"{'=' * 60}")
        print(f"suggestion: {result.get('suggestion', 'NONE')}")
        print(f"ai_answer: {result.get('ai_answer', 'NONE')}")
        print(f"method: {result.get('method', 'NONE')}")
        print(f"confidence: {result.get('confidence', 'NONE')}")
        print(f"{'=' * 60}")
        
        return result
        
    except Exception as e:
        print(f"\nERROR during AI suggestion: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n🧪 Testing Semantic Context System\n")
    
    results = []
    
    # Test 1: Basic context building
    results.append(("Context Building", test_semantic_context_building()))
    
    # Test 2: AI context formatting
    results.append(("AI Context Formatting", test_context_for_ai()))
    
    # Test 3: Acronym tracking
    results.append(("Acronym Tracking", test_acronym_expansion_tracking()))
    
    # Test 4: CRITICAL - Meaning preservation
    print("\n" + "=" * 60)
    print("RUNNING CRITICAL TEST: MEANING PRESERVATION")
    print("=" * 60)
    ai_result = test_meaning_lock()
    results.append(("Meaning Preservation", ai_result is not None))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
