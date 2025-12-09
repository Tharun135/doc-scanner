#!/usr/bin/env python3
"""
Click On → Click Rule Implementation
Removes unnecessary "on" after "click" in UI instructions
"""
import re
from typing import Optional, Dict

class ClickOnRule:
    """Rule to change 'click on' to 'click' for concise UI instructions."""
    
    def __init__(self):
        self.name = "click_on_to_click"
        self.description = "Change 'click on' to 'click' for more concise UI instructions"
        self.pattern = re.compile(r'\bclick\s+on\b', re.IGNORECASE)
        
    def apply(self, text: str) -> Optional[Dict]:
        """
        Apply the click on → click rule.
        
        Args:
            text: Input text to process
            
        Returns:
            Dict with rewrite and metadata if rule applies, None otherwise
        """
        if not self.pattern.search(text):
            return None
            
        # Apply the replacement
        original = text
        rewritten = self.pattern.sub(lambda m: self._replace_click_on(m), text)
        
        if rewritten == original:
            return None
            
        return {
            "original": original,
            "rewrite": rewritten,
            "rule": self.name,
            "description": self.description,
            "confidence": 0.9,  # High confidence for this simple rule
            "changes": self._get_changes(original, rewritten)
        }
    
    def _replace_click_on(self, match):
        """Replace 'click on' with 'click', preserving case."""
        matched_text = match.group(0)
        if matched_text.startswith('C'):  # Capitalized
            return "Click"
        else:
            return "click"
    
    def _get_changes(self, original: str, rewritten: str) -> list:
        """Get list of specific changes made."""
        changes = []
        
        # Find all instances of the change
        for match in self.pattern.finditer(original):
            start, end = match.span()
            old_text = match.group(0)
            new_text = "Click" if old_text.startswith('C') else "click"
            
            changes.append({
                "position": start,
                "old": old_text,
                "new": new_text,
                "reason": "Removed unnecessary 'on' after 'click' for conciseness"
            })
            
        return changes


def test_click_on_rule():
    """Test the click on → click rule with various examples."""
    rule = ClickOnRule()
    
    test_cases = [
        "Click on the Submit button to continue.",
        "Users should click on Save to save their work.", 
        "Click on Settings to open the menu.",
        "To start, click on the Start button.",
        "CLICK ON the icon to proceed.",
        "Please click on 'Next' when ready.",
        "Click the button to continue.",  # No change needed
        "Select the option and then click on Apply.",
        "Double-click on the file to open it.",  # Should not change
        "Right-click on the item for options.",  # Should not change
    ]
    
    print("🧪 Testing Click On → Click Rule")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Original: '{test_text}'")
        
        result = rule.apply(test_text)
        
        if result:
            print(f"   ✅ Rewrite: '{result['rewrite']}'")
            print(f"   📝 Changes: {len(result['changes'])}")
            for change in result['changes']:
                print(f"      • {change['old']} → {change['new']} ({change['reason']})")
        else:
            print(f"   ❌ No changes needed")


def integrate_with_style_rag():
    """Demo integration with the style guide RAG system."""
    from style_guide_rag import StyleGuideRAG
    
    rule = ClickOnRule()
    style_rag = StyleGuideRAG()
    
    def enhanced_rewrite_with_click_rule(sentence: str) -> Dict:
        """Enhanced rewrite that applies click rule first."""
        
        # Step 1: Apply the click on → click rule first (high confidence)
        click_result = rule.apply(sentence)
        if click_result and click_result['confidence'] >= 0.8:
            return {
                "final_text": click_result['rewrite'],
                "strategy": "click_on_rule",
                "confidence": click_result['confidence'],
                "changes": click_result['changes']
            }
        
        # Step 2: Try style guide RAG for other improvements
        current_text = click_result['rewrite'] if click_result else sentence
        guidance_prompt = style_rag.build_guidance_prompt(current_text, max_guidance=2)
        
        if guidance_prompt:
            return {
                "final_text": current_text,  # Would send to LLM in real implementation
                "strategy": "style_guide_rag",
                "confidence": 0.75,
                "prompt_generated": True,
                "pre_processed": click_result is not None
            }
        
        # Step 3: Return original or click-fixed version
        return {
            "final_text": current_text,
            "strategy": "click_rule_only" if click_result else "no_changes",
            "confidence": click_result['confidence'] if click_result else 0.5,
            "changes": click_result['changes'] if click_result else []
        }
    
    # Test the integrated pipeline
    test_sentences = [
        "Click on the Submit button to continue.",
        "Follow these steps to click on Settings.",
        "Users should click on Save to save their work.",
    ]
    
    print("\n🔄 Testing Integrated Pipeline (Click Rule + Style RAG)")
    print("=" * 60)
    
    for sentence in test_sentences:
        print(f"\n📝 Input: '{sentence}'")
        result = enhanced_rewrite_with_click_rule(sentence)
        
        print(f"   ✅ Output: '{result['final_text']}'")
        print(f"   📊 Strategy: {result['strategy']}")
        print(f"   🎯 Confidence: {result['confidence']:.1%}")
        
        if result.get('changes'):
            print(f"   📝 Changes applied:")
            for change in result['changes']:
                print(f"      • {change['old']} → {change['new']}")


if __name__ == "__main__":
    test_click_on_rule()
    print("\n" + "="*60)
    integrate_with_style_rag()
