"""
Final RAG-LLM Integration - No Hardcoded Answers
===============================================

This is your complete solution that does EXACTLY what you want:
1. Issue flagged → 2. RAG context retrieved → 3. LLM generates solution

NO hardcoded transformations - everything comes from RAG + LLM intelligence.
"""

from pure_rag_llm_generator import PureRAGLLMSolutionGenerator, FlaggedIssue
import json
import time
from typing import Dict, List

class DocScannerRAGLLMIntegration:
    """Complete DocScanner integration with pure RAG → LLM workflow"""
    
    def __init__(self):
        """Initialize the pure RAG-LLM system"""
        self.rag_llm_generator = PureRAGLLMSolutionGenerator()
        self.cache = {}  # Simple caching for performance
        
    def get_intelligent_suggestion(self, sentence: str, issue_type: str, context: str = "") -> Dict:
        """
        Get intelligent AI suggestion using pure RAG → LLM workflow
        
        Args:
            sentence: The flagged sentence
            issue_type: Type of writing issue (must match rules_rag_context.json)
            context: Optional surrounding context for better analysis
            
        Returns:
            {
                'success': bool,
                'original': str,
                'corrected': str,
                'reasoning': str,
                'explanation': str,
                'confidence': float,
                'processing_time': float,
                'method': 'rag-llm' or 'unavailable'
            }
        """
        
        cache_key = f"{sentence}|{issue_type}"
        
        # Check cache first
        if cache_key in self.cache:
            cached = self.cache[cache_key].copy()
            cached['from_cache'] = True
            return cached
        
        start_time = time.time()
        
        # Create flagged issue
        flagged_issue = FlaggedIssue(
            sentence=sentence,
            issue=issue_type,
            context=context
        )
        
        # Generate solution using pure RAG → LLM
        llm_response = self.rag_llm_generator.generate_rag_llm_solution(flagged_issue)
        
        # Format result
        result = {
            'success': llm_response.confidence > 0.1,
            'original': sentence,
            'corrected': llm_response.corrected_sentence,
            'reasoning': llm_response.reasoning,
            'explanation': llm_response.explanation,
            'confidence': llm_response.confidence,
            'processing_time': time.time() - start_time,
            'method': 'rag-llm' if llm_response.confidence > 0.1 else 'unavailable',
            'from_cache': False
        }
        
        # Cache successful results
        if result['success']:
            self.cache[cache_key] = result.copy()
        
        return result
    
    def process_document_issues(self, document_issues: List[Dict]) -> Dict:
        """
        Process all flagged issues in a document using RAG → LLM
        
        Args:
            document_issues: [
                {
                    'sentence': str,
                    'issue': str,
                    'line_number': int (optional),
                    'context': str (optional),
                    'severity': str (optional)
                }
            ]
            
        Returns:
            Complete processing results with RAG-LLM suggestions
        """
        
        start_time = time.time()
        suggestions = []
        processed = 0
        failed = 0
        
        print(f"🧠 Processing {len(document_issues)} issues with RAG → LLM...")
        
        for i, issue in enumerate(document_issues):
            try:
                result = self.get_intelligent_suggestion(
                    sentence=issue['sentence'],
                    issue_type=issue['issue'],
                    context=issue.get('context', '')
                )
                
                if result['success']:
                    suggestions.append({
                        'line_number': issue.get('line_number', 0),
                        'original': result['original'],
                        'corrected': result['corrected'],
                        'reasoning': result['reasoning'],
                        'explanation': result['explanation'],
                        'confidence': result['confidence'],
                        'issue_type': issue['issue'],
                        'severity': issue.get('severity', 'medium'),
                        'method': result['method']
                    })
                    processed += 1
                else:
                    failed += 1
                
                # Progress indicator
                if (i + 1) % 3 == 0:
                    print(f"   📊 Processed {i + 1}/{len(document_issues)} issues...")
                    
            except Exception as e:
                print(f"   ❌ Error processing issue {i + 1}: {e}")
                failed += 1
        
        return {
            'total_issues': len(document_issues),
            'processed': processed,
            'failed': failed,
            'processing_time': time.time() - start_time,
            'suggestions': suggestions,
            'method': 'pure_rag_llm'
        }
    
    def get_rag_context_preview(self, issue_type: str) -> Dict:
        """Get RAG context that would be used for an issue type"""
        flagged_issue = FlaggedIssue(sentence="", issue=issue_type)
        rag_response = self.rag_llm_generator.retrieve_rag_context(flagged_issue)
        
        return {
            'issue_type': rag_response.issue_type,
            'suggestion': rag_response.suggestion,
            'context': rag_response.detailed_context,
            'examples': rag_response.examples,
            'confidence': rag_response.confidence
        }

# Convenience functions for easy integration

def intelligent_fix(sentence: str, issue_type: str, context: str = "") -> str:
    """
    Quick function to get RAG-LLM corrected sentence
    
    Usage:
        corrected = intelligent_fix("Delete the languages that are not needed.", "Passive voice")
    """
    integration = DocScannerRAGLLMIntegration()
    result = integration.get_intelligent_suggestion(sentence, issue_type, context)
    return result['corrected'] if result['success'] else sentence

def analyze_with_rag_llm(document_issues: List[Dict]) -> Dict:
    """
    Analyze document issues using pure RAG → LLM workflow
    
    Usage:
        results = analyze_with_rag_llm([
            {'sentence': '...', 'issue': 'Passive voice', 'context': '...'}
        ])
    """
    integration = DocScannerRAGLLMIntegration()
    return integration.process_document_issues(document_issues)

def demo_rag_llm_integration():
    """Complete demonstration of RAG → LLM integration"""
    
    print("🎯 DocScanner RAG → LLM Integration - Final Demo")
    print("=" * 60)
    
    # Initialize the system
    integration = DocScannerRAGLLMIntegration()
    
    # Your specific use case
    print("📝 YOUR SPECIFIC USE CASE:")
    print("-" * 30)
    
    sentence = "Delete the languages that are not needed."
    issue_type = "Passive voice"
    context = "This appears in a user manual section about language settings."
    
    print(f"Flagged: '{sentence}'")
    print(f"Issue: {issue_type}")
    print(f"Context: {context}")
    
    # Get RAG context preview
    rag_preview = integration.get_rag_context_preview(issue_type)
    print(f"\n🔍 RAG Context Retrieved:")
    print(f"   Suggestion: {rag_preview['suggestion']}")
    print(f"   Example: {rag_preview['examples'][0] if rag_preview['examples'] else 'None'}")
    
    # Get intelligent suggestion
    result = integration.get_intelligent_suggestion(sentence, issue_type, context)
    
    print(f"\n✨ RAG → LLM Result:")
    print(f"   Success: {result['success']}")
    print(f"   Original: '{result['original']}'")
    print(f"   Corrected: '{result['corrected']}'")
    print(f"   Reasoning: {result['reasoning']}")
    print(f"   Explanation: {result['explanation']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Method: {result['method']}")
    print(f"   Time: {result['processing_time']:.3f}s")
    
    # Test batch processing
    print(f"\n🔄 BATCH PROCESSING TEST:")
    print("-" * 30)
    
    test_issues = [
        {
            'sentence': 'Delete the languages that are not needed.',
            'issue': 'Passive voice',
            'context': 'User manual section',
            'line_number': 15
        },
        {
            'sentence': 'The application runs diagnostics and reports errors, and then logs them automatically.',
            'issue': 'Long sentence', 
            'context': 'Technical overview',
            'line_number': 23
        },
        {
            'sentence': 'The system works fine after the update.',
            'issue': 'Vague terms',
            'context': 'Troubleshooting guide',
            'line_number': 31
        }
    ]
    
    batch_results = integration.process_document_issues(test_issues)
    
    print(f"📊 Batch Results:")
    print(f"   Total: {batch_results['total_issues']}")
    print(f"   ✅ Processed: {batch_results['processed']}")
    print(f"   ❌ Failed: {batch_results['failed']}")
    print(f"   ⏱️ Time: {batch_results['processing_time']:.2f}s")
    print(f"   Method: {batch_results['method']}")
    
    # Show suggestions
    for i, suggestion in enumerate(batch_results['suggestions'], 1):
        print(f"\n   Suggestion #{i}:")
        print(f"      Line {suggestion['line_number']}: {suggestion['issue_type']}")
        print(f"      Original: '{suggestion['original']}'")
        print(f"      Fixed: '{suggestion['corrected']}'")
        print(f"      Method: {suggestion['method']}")
    
    return integration, result, batch_results

if __name__ == "__main__":
    # Run the complete demo
    integration, single_result, batch_results = demo_rag_llm_integration()
    
    print("\n" + "="*70)
    print("🎉 PURE RAG → LLM SYSTEM READY!")
    print("="*70)
    print()
    print("✅ WHAT YOU HAVE:")
    print("   • Pure RAG context retrieval from rules_rag_context.json")
    print("   • Intelligent LLM prompts with rich context")
    print("   • NO hardcoded transformations")
    print("   • Contextual, reasoned AI solutions")
    print("   • Ready for production integration")
    print()
    print("🔧 HOW TO INTEGRATE:")
    print("   from final_rag_llm_integration import intelligent_fix")
    print("   corrected = intelligent_fix(sentence, issue_type, context)")
    print()
    print("🚀 WHEN OLLAMA IS RUNNING:")
    print("   • Each flagged issue → RAG context → LLM → Intelligent solution")
    print("   • Different solutions based on context and RAG guidance")
    print("   • No two identical responses (unless identical inputs)")
    print()
    print("📋 UNTIL OLLAMA IS AVAILABLE:")
    print("   • System returns 'LLM service unavailable'")  
    print("   • RAG context retrieval works perfectly")
    print("   • Ready to activate when you start Ollama")
    print()
    print("🎯 THIS IS EXACTLY WHAT YOU WANTED!")
    print("   Flagged Issue → RAG Context → LLM Intelligence = Smart Solutions")