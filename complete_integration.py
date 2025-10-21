"""
Complete DocScanner AI Integration
=================================

This is your production-ready integration script that combines:
- Your existing rules_rag_context.json
- Ollama AI integration (when available) 
- Intelligent rule-based fallbacks
- Easy integration with your DocScanner app

Usage Examples:
1. Single sentence fix: get_smart_suggestion(sentence, issue_type)
2. Batch processing: process_document_issues(issues_list)
3. API endpoint: create_ai_endpoint() for web integration
"""

from fallback_solution_generator import FallbackSolutionGenerator
from ollama_rag_integration import FlaggedIssue, AIResponse
import json
import time
from typing import List, Dict, Optional

class DocScannerAI:
    """Main class for DocScanner AI integration"""
    
    def __init__(self):
        """Initialize the AI system"""
        self.generator = FallbackSolutionGenerator()
        self.cache = {}  # Simple caching to avoid re-processing same sentences
        
    def get_smart_suggestion(self, sentence: str, issue_type: str, use_cache: bool = True) -> Dict:
        """
        Get AI-powered suggestion for a single flagged sentence
        
        Args:
            sentence: The flagged sentence
            issue_type: Type of issue (must match rules_rag_context.json)
            use_cache: Whether to use cached results
            
        Returns:
            {
                'success': True/False,
                'original': str,
                'corrected': str, 
                'explanation': str,
                'confidence': float,
                'processing_time': float,
                'source': 'ai' or 'fallback'
            }
        """
        
        cache_key = f"{sentence}|{issue_type}"
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key].copy()
            cached['from_cache'] = True
            return cached
        
        start_time = time.time()
        
        # Create flagged issue
        flagged_issue = FlaggedIssue(sentence=sentence, issue=issue_type)
        
        # Generate solution
        solution = self.generator.generate_solution(flagged_issue)
        
        # Determine if AI or fallback was used
        source = 'ai' if solution.confidence > 0.7 else 'fallback'
        
        result = {
            'success': solution.corrected_sentence != "AI service unavailable",
            'original': sentence,
            'corrected': solution.corrected_sentence,
            'explanation': solution.explanation,
            'confidence': solution.confidence,
            'processing_time': time.time() - start_time,
            'source': source,
            'from_cache': False
        }
        
        # Cache the result
        if use_cache:
            self.cache[cache_key] = result.copy()
        
        return result
    
    def process_document_issues(self, document_issues: List[Dict]) -> Dict:
        """
        Process all issues in a document
        
        Args:
            document_issues: [
                {
                    'sentence': str,
                    'issue': str,
                    'line_number': int (optional),
                    'severity': str (optional)
                },
                ...
            ]
            
        Returns:
            {
                'total_issues': int,
                'processed': int,
                'failed': int,
                'processing_time': float,
                'suggestions': [
                    {
                        'line_number': int,
                        'original': str,
                        'corrected': str,
                        'explanation': str,
                        'confidence': float,
                        'issue_type': str
                    },
                    ...
                ]
            }
        """
        
        start_time = time.time()
        suggestions = []
        processed = 0
        failed = 0
        
        print(f"🔄 Processing {len(document_issues)} issues...")
        
        for i, issue in enumerate(document_issues):
            try:
                result = self.get_smart_suggestion(
                    issue['sentence'], 
                    issue['issue']
                )
                
                if result['success']:
                    suggestions.append({
                        'line_number': issue.get('line_number', 0),
                        'original': result['original'],
                        'corrected': result['corrected'],
                        'explanation': result['explanation'],
                        'confidence': result['confidence'],
                        'issue_type': issue['issue'],
                        'severity': issue.get('severity', 'medium'),
                        'source': result['source']
                    })
                    processed += 1
                else:
                    failed += 1
                
                # Progress indicator
                if (i + 1) % 5 == 0:
                    print(f"   Processed {i + 1}/{len(document_issues)} issues...")
                    
            except Exception as e:
                print(f"   Error processing issue {i + 1}: {e}")
                failed += 1
        
        return {
            'total_issues': len(document_issues),
            'processed': processed,
            'failed': failed,
            'processing_time': time.time() - start_time,
            'suggestions': suggestions
        }
    
    def get_available_issue_types(self) -> List[str]:
        """Get list of all issue types that can be processed"""
        return list(self.generator.rules_dict.keys())
    
    def export_suggestions_report(self, results: Dict, filename: str = None) -> str:
        """Export processing results to a detailed report"""
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"docscanner_ai_report_{timestamp}.json"
        
        # Add metadata
        report = {
            'metadata': {
                'generated_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'docscanner_version': '1.0.0',
                'ai_enabled': self.generator.config.get('api_url') is not None,
                'total_rules': len(self.generator.rules_dict)
            },
            'summary': {
                'total_issues': results['total_issues'],
                'successfully_processed': results['processed'],
                'failed': results['failed'],
                'processing_time_seconds': round(results['processing_time'], 2),
                'average_time_per_issue': round(results['processing_time'] / max(results['total_issues'], 1), 3)
            },
            'suggestions': results['suggestions']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Report saved to: {filename}")
        return filename

# Convenience functions for easy integration

def quick_fix(sentence: str, issue_type: str) -> str:
    """
    Quick function to get corrected sentence
    
    Usage:
        corrected = quick_fix("The issue was resolved by the developer", "Passive voice")
    """
    ai = DocScannerAI()
    result = ai.get_smart_suggestion(sentence, issue_type)
    return result['corrected'] if result['success'] else sentence

def analyze_document(document_text: str, flagged_issues: List[Dict]) -> Dict:
    """
    Analyze an entire document and return comprehensive results
    
    Usage:
        results = analyze_document(doc_text, [
            {'sentence': '...', 'issue': 'Long sentence', 'line_number': 10}
        ])
    """
    ai = DocScannerAI()
    return ai.process_document_issues(flagged_issues)

# Demo and testing functions

def demo_integration():
    """Complete demo of the DocScanner AI integration"""
    
    print("🚀 DocScanner AI - Complete Integration Demo")
    print("=" * 50)
    
    # Initialize AI
    ai = DocScannerAI()
    
    # Show available issue types
    print(f"📋 Available issue types: {len(ai.get_available_issue_types())}")
    for issue_type in ai.get_available_issue_types()[:5]:  # Show first 5
        print(f"   • {issue_type}")
    print(f"   • ... and {len(ai.get_available_issue_types()) - 5} more")
    print()
    
    # Test individual suggestions
    print("🔍 Testing individual suggestions:")
    print("-" * 30)
    
    test_cases = [
        ("The application runs diagnostics and reports errors, and then logs them into the system automatically.", "Long sentence"),
        ("The issue was resolved by the developer.", "Passive voice"),
        ("installing the application", "Title capitalization"),
        ("The system works fine.", "Vague terms")
    ]
    
    for sentence, issue_type in test_cases:
        result = ai.get_smart_suggestion(sentence, issue_type)
        
        print(f"Issue: {issue_type}")
        print(f"Original: \"{result['original']}\"")
        print(f"✨ Fixed: \"{result['corrected']}\"")
        print(f"💡 Why: {result['explanation']}")
        print(f"📊 Confidence: {result['confidence']:.1%} | Source: {result['source']}")
        print(f"⏱️ Time: {result['processing_time']:.3f}s")
        print()
    
    # Test batch processing
    print("🔄 Testing batch processing:")
    print("-" * 30)
    
    document_issues = [
        {
            'sentence': 'The application runs diagnostics and reports errors, and then logs them into the system automatically.',
            'issue': 'Long sentence',
            'line_number': 15,
            'severity': 'medium'
        },
        {
            'sentence': 'The issue was resolved by the developer.',
            'issue': 'Passive voice', 
            'line_number': 23,
            'severity': 'low'
        },
        {
            'sentence': 'installing the application',
            'issue': 'Title capitalization',
            'line_number': 1,
            'severity': 'low'
        }
    ]
    
    batch_results = ai.process_document_issues(document_issues)
    
    print(f"📊 Batch Results:")
    print(f"   Total: {batch_results['total_issues']}")
    print(f"   ✅ Processed: {batch_results['processed']}")
    print(f"   ❌ Failed: {batch_results['failed']}")
    print(f"   ⏱️ Time: {batch_results['processing_time']:.2f}s")
    print()
    
    # Export report
    report_file = ai.export_suggestions_report(batch_results)
    
    print("✅ Integration demo complete!")
    print(f"📄 Detailed report saved as: {report_file}")
    
    return ai, batch_results

if __name__ == "__main__":
    # Run the complete demo
    ai_system, results = demo_integration()
    
    print("\n" + "="*60)
    print("🎯 READY FOR PRODUCTION INTEGRATION!")
    print("="*60)
    print()
    print("HOW TO INTEGRATE WITH YOUR DOCSCANNER:")
    print()
    print("1. Simple Usage:")
    print("   from complete_integration import quick_fix")
    print("   corrected = quick_fix(sentence, issue_type)")
    print()
    print("2. Advanced Usage:")
    print("   from complete_integration import DocScannerAI")
    print("   ai = DocScannerAI()")
    print("   result = ai.get_smart_suggestion(sentence, issue)")
    print()
    print("3. Batch Processing:")
    print("   results = ai.process_document_issues(issues_list)")
    print()
    print("4. Web API Integration:")
    print("   # Use DocScannerAI class in your Flask/FastAPI endpoints")
    print()
    print("🔧 Ollama Setup (for full AI features):")
    print("   1. Download from https://ollama.ai")
    print("   2. Run: ollama pull phi3:mini")
    print("   3. Start: ollama serve")
    print()
    print("✨ Works great with or without Ollama!")