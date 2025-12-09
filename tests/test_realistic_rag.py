#!/usr/bin/env python3
"""
Test with more realistic queries and show actual guidance content
"""
from style_guide_rag import StyleGuideRAG

def test_with_realistic_queries():
    rag = StyleGuideRAG()
    
    # Test queries that match our style guide content better
    test_cases = [
        ("Click on the button", "UI interaction guidance"),
        ("Follow these steps", "Procedural writing guidance"), 
        ("Write clear headings", "Heading formatting guidance"),
        ("Use inclusive language", "Inclusive writing guidance"),
        ("Format web addresses", "URL formatting guidance"),
    ]
    
    print("🧪 Testing Style Guide RAG with Realistic Queries")
    print("=" * 60)
    
    for query, description in test_cases:
        print(f"\n📝 {description}")
        print(f"Query: '{query}'")
        print("-" * 40)
        
        # Test with lower similarity threshold
        guidance = rag.retrieve_guidance(query, k=2, min_similarity=0.25)
        
        if guidance:
            print(f"✅ Found {len(guidance)} relevant guidance items:")
            for i, item in enumerate(guidance, 1):
                source = item["source"].upper()
                title = item["title"]
                similarity = item["similarity"]
                topic = item["topic"]
                
                print(f"\n{i}. [{source}] {title}")
                print(f"   Topic: {topic} | Similarity: {similarity:.3f}")
                print(f"   Content: {item['text'][:200]}...")
                
                # Show if this would generate a prompt
                prompt = rag.build_guidance_prompt(query, max_guidance=1)
                if prompt:
                    print("   ✅ Would generate guided prompt")
                else:
                    print("   ❌ Below prompt threshold")
        else:
            print("❌ No guidance found")
    
    # Test the full prompt generation process
    print(f"\n{'='*60}")
    print("🎯 Full Prompt Generation Example")
    print("="*60)
    
    test_sentence = "Follow these steps to setup the system"
    prompt = rag.build_guidance_prompt(test_sentence, max_guidance=2)
    
    if prompt:
        print(f"Sentence: '{test_sentence}'")
        print("\nGenerated Prompt:")
        print("-" * 30)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    else:
        print("No prompt could be generated")

if __name__ == "__main__":
    test_with_realistic_queries()
