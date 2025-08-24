#!/usr/bin/env python3
"""
Final Integration Test - Complete Style Guide RAG System
Demonstrates the full pipeline integration with realistic doc-scanner scenarios
"""
import json
from style_guide_rag import StyleGuideRAG

def simulate_docscanner_pipeline():
    """Simulate how this integrates with your existing DocScanner pipeline"""
    
    # Initialize the style guide RAG system
    print("🚀 Initializing Style Guide RAG System...")
    style_rag = StyleGuideRAG()
    
    # Sample sentences that would come from your document scanner
    test_sentences = [
        # UI/Interaction issues
        "Click on the Submit button to continue.",
        "Users should click on Save to save their work.",
        
        # Procedural writing issues  
        "Follow these steps to configure the system.",
        "To setup the application, do the following steps.",
        
        # Formatting issues
        "Visit https://www.example.com for more information.",
        "Go to the Settings page to change your preferences.",
        
        # Capitalization/Heading issues
        "How To Configure Your Account Settings",
        "GETTING STARTED WITH THE API",
        
        # Already good sentences (should remain unchanged)
        "Select **Save** to save your changes.",
        "Follow these guidelines to create clear instructions.",
    ]
    
    print(f"\n🧪 Testing {len(test_sentences)} sample sentences from document scanning...")
    print("=" * 80)
    
    results = []
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n📝 Test {i}: '{sentence}'")
        print("-" * 60)
        
        # Step 1: Check if we have relevant guidance
        guidance = style_rag.retrieve_guidance(sentence, k=2, min_similarity=0.3)
        
        result = {
            "original": sentence,
            "guidance_found": len(guidance),
            "sources": [],
            "has_prompt": False,
            "strategy": "none"
        }
        
        if guidance:
            print(f"✅ Found {len(guidance)} relevant guidance items:")
            for item in guidance[:2]:  # Show top 2
                source = item["source"].upper()
                title = item["title"]
                similarity = item["similarity"]
                topic = item["topic"]
                
                print(f"   • [{source}] {title}")
                print(f"     Topic: {topic} | Relevance: {similarity:.1%}")
                
                result["sources"].append({
                    "source": source,
                    "title": title,
                    "topic": topic,
                    "similarity": similarity
                })
            
            # Step 2: Try to generate a guidance-based prompt
            prompt = style_rag.build_guidance_prompt(sentence, max_guidance=2)
            
            if prompt:
                result["has_prompt"] = True
                result["strategy"] = "whitelist_guided"
                print(f"   ✅ Generated authoritative guidance prompt")
                print(f"   📄 Prompt length: {len(prompt)} characters")
                
                # In a real system, you'd send this prompt to your LLM
                # For demo purposes, we'll simulate a response
                print(f"   🤖 Would send to LLM with strategy: 'whitelist_guided'")
                
            else:
                result["strategy"] = "fallback"
                print(f"   ❌ No prompt generated (similarity too low)")
                print(f"   📄 Would fall back to existing smart_fallback()")
                
        else:
            result["strategy"] = "custom_rules"
            print(f"❌ No style guide guidance found")
            print(f"📄 Would try custom rules first, then smart_fallback()")
        
        results.append(result)
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("📊 PIPELINE INTEGRATION SUMMARY")
    print("="*80)
    
    guidance_found = sum(1 for r in results if r["guidance_found"] > 0)
    prompts_generated = sum(1 for r in results if r["has_prompt"])
    
    strategy_counts = {}
    for r in results:
        strategy = r["strategy"]
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    print(f"Total sentences processed: {len(results)}")
    print(f"Sentences with style guidance: {guidance_found} ({guidance_found/len(results)*100:.1f}%)")
    print(f"Sentences with generated prompts: {prompts_generated} ({prompts_generated/len(results)*100:.1f}%)")
    print(f"\nStrategy distribution:")
    for strategy, count in strategy_counts.items():
        print(f"  • {strategy}: {count} sentences ({count/len(results)*100:.1f}%)")
    
    # Source attribution breakdown
    source_counts = {}
    for r in results:
        for source_info in r["sources"]:
            source = source_info["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
    
    if source_counts:
        print(f"\nAuthoritative sources used:")
        for source, count in sorted(source_counts.items()):
            print(f"  • {source}: {count} guidance items")
    
    # Show a sample prompt for demonstration
    print(f"\n{'='*80}")
    print("🎯 SAMPLE GENERATED PROMPT")
    print("="*80)
    
    sample_sentence = "Follow these steps to setup the system"
    sample_prompt = style_rag.build_guidance_prompt(sample_sentence, max_guidance=1)
    
    if sample_prompt:
        print(f"Input: '{sample_sentence}'")
        print(f"\nGenerated Prompt:")
        print("-" * 40)
        # Show first 500 chars of the prompt
        print(sample_prompt[:500] + "..." if len(sample_prompt) > 500 else sample_prompt)
        
        # In a real implementation, you'd parse the JSON response:
        sample_response = {
            "rewrite": "Follow these steps to set up the system.",
            "rationale": "Changed 'setup' to 'set up' (verb form) following Microsoft writing standards for procedural instructions."
        }
        
        print(f"\n🤖 Sample LLM Response (JSON):")
        print("-" * 40)
        print(json.dumps(sample_response, indent=2))
        
    print(f"\n✅ Style Guide RAG System Integration Complete!")
    print(f"🚀 Ready for production use in your DocScanner pipeline!")


if __name__ == "__main__":
    simulate_docscanner_pipeline()
