#!/usr/bin/env python3
"""
Enhanced Custom Rules System with Click On → Click Rule
Integrates the click rule with your existing custom rules and style guide RAG
"""
import re
from typing import List, Dict, Optional
from click_on_rule import ClickOnRule

class CustomRulesEngine:
    """Enhanced rules engine that includes the click on → click rule."""
    
    def __init__(self):
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """Load all custom rules."""
        # Add the click on → click rule
        self.rules.append(ClickOnRule())
        
        # You can add more rules here:
        # self.rules.append(PassiveVoiceRule())
        # self.rules.append(AbbreviationRule())
        # etc.
    
    def apply_rules(self, text: str) -> Dict:
        """
        Apply all custom rules in priority order.
        
        Args:
            text: Input text to process
            
        Returns:
            Dict with best rewrite result and metadata
        """
        results = []
        
        # Apply each rule and collect results
        for rule in self.rules:
            result = rule.apply(text)
            if result:
                results.append(result)
        
        if not results:
            return {
                "original": text,
                "rewrite": text,
                "rules_applied": [],
                "confidence": 0.0,
                "strategy": "no_custom_rules"
            }
        
        # For now, take the highest confidence rule
        # In a more complex system, you might combine multiple rules
        best_result = max(results, key=lambda x: x['confidence'])
        
        return {
            "original": text,
            "rewrite": best_result['rewrite'],
            "rules_applied": [best_result],
            "confidence": best_result['confidence'],
            "strategy": "custom_rules",
            "total_rules_checked": len(self.rules),
            "total_matches": len(results)
        }


def integrated_docscanner_pipeline(sentence: str) -> Dict:
    """
    Complete integrated pipeline: Custom Rules → Style Guide RAG → Fallback
    This is how it would integrate into your existing DocScanner system.
    """
    from style_guide_rag import StyleGuideRAG
    
    # Initialize components
    custom_rules = CustomRulesEngine()
    style_rag = StyleGuideRAG()
    
    # Step 1: Try custom rules first (highest confidence, fastest)
    print(f"   🔧 Step 1: Applying custom rules...")
    custom_result = custom_rules.apply_rules(sentence)
    
    if custom_result['confidence'] >= 0.8:  # High confidence threshold
        print(f"   ✅ Custom rule applied: {custom_result['rules_applied'][0]['rule']}")
        return {
            "final_text": custom_result['rewrite'],
            "strategy": custom_result['strategy'],
            "confidence": custom_result['confidence'],
            "method": "custom_rules",
            "details": custom_result
        }
    
    # Step 2: Try Style Guide RAG (authoritative guidance)
    print(f"   📚 Step 2: Checking style guide RAG...")
    current_text = custom_result['rewrite']  # Use any custom rule improvements
    guidance_prompt = style_rag.build_guidance_prompt(current_text, max_guidance=2)
    
    if guidance_prompt:
        print(f"   ✅ Style guide prompt generated ({len(guidance_prompt)} chars)")
        # In real implementation, you'd call your LLM here
        # llm_result = call_llm(guidance_prompt, strategy="whitelist_guided")
        
        return {
            "final_text": current_text,  # Would be LLM result in real implementation
            "strategy": "style_guide_rag", 
            "confidence": 0.75,
            "method": "authoritative_guidance",
            "prompt_length": len(guidance_prompt),
            "pre_processed": custom_result['confidence'] > 0
        }
    
    # Step 3: Fallback (your existing smart_fallback or no changes)
    print(f"   🔄 Step 3: Using fallback strategy...")
    
    # If custom rules made improvements, use them; otherwise return original
    if custom_result['confidence'] > 0:
        return {
            "final_text": custom_result['rewrite'],
            "strategy": "custom_rules_only",
            "confidence": custom_result['confidence'],
            "method": "fallback_with_custom_improvements",
            "details": custom_result
        }
    else:
        # In real implementation: return smart_fallback(sentence)
        return {
            "final_text": sentence,
            "strategy": "no_changes",
            "confidence": 0.5,
            "method": "fallback_original",
            "reason": "No applicable rules or guidance found"
        }


def demo_complete_pipeline():
    """Demonstrate the complete integrated pipeline."""
    
    test_sentences = [
        # Should trigger click rule
        "Click on the Submit button to continue.",
        "Users should click on Save to save their work.",
        
        # Should trigger style guide RAG  
        "Follow these steps to setup the system.",
        "How To Configure Your Account Settings",
        
        # Should have no changes
        "The system is working correctly.",
        "Click the button to proceed.",  # Already correct
    ]
    
    print("🚀 Complete DocScanner Pipeline Demo")
    print("=" * 60)
    print("Pipeline: Custom Rules → Style Guide RAG → Fallback")
    print("=" * 60)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n📝 Test {i}: '{sentence}'")
        print("-" * 50)
        
        result = integrated_docscanner_pipeline(sentence)
        
        print(f"   🎯 Final: '{result['final_text']}'")
        print(f"   📊 Method: {result['method']}")
        print(f"   🔥 Strategy: {result['strategy']}")
        print(f"   📈 Confidence: {result['confidence']:.1%}")
        
        if result.get('details', {}).get('rules_applied'):
            rule_info = result['details']['rules_applied'][0]
            print(f"   📝 Rule: {rule_info['rule']} ({rule_info['description']})")
        
        # Show improvement
        if result['final_text'] != sentence:
            print(f"   ✨ Improvement: YES")
        else:
            print(f"   ✨ Improvement: No changes needed")


if __name__ == "__main__":
    demo_complete_pipeline()
