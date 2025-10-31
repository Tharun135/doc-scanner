from production_passive_voice_ai import get_passive_voice_alternatives

sentence = "The following requirements must be met:"
feedback = "Avoid passive voice in sentence"

print("Testing:", sentence)
result = get_passive_voice_alternatives(sentence, feedback)

if result and result.get('suggestions'):
    print(f"SUCCESS: Generated {len(result['suggestions'])} alternatives:")
    for i, s in enumerate(result['suggestions'], 1):
        print(f"{i}. {s['text']}")
        print(f"   Source: {s.get('source', 'unknown')}")
        if s.get('synonym'):
            print(f"   Synonym: {s['synonym']}")
else:
    print("No alternatives generated")
    print("Result:", result)
