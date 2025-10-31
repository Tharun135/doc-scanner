#!/usr/bin/env python3
"""
KB Coverage Analysis Tool
Tests various writing issues to identify gaps in knowledge base coverage
"""

import requests
import json
from typing import List, Dict

class KBGapAnalyzer:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.gaps = []
        self.low_quality = []
        self.errors = []
    
    def test_writing_issues(self):
        """Test comprehensive list of writing issues"""
        test_cases = [
            # Current Coverage (should work well)
            {"category": "Passive Voice", "feedback": "avoid passive voice", 
             "sentence": "The file was uploaded by the user"},
            {"category": "Adverbs", "feedback": "remove adverb", 
             "sentence": "You can easily configure the settings"},
            {"category": "Modal Verbs", "feedback": "avoid modal verbs", 
             "sentence": "You should click the button"},
            
            # Potential Gaps (might fail)
            {"category": "Double Negatives", "feedback": "avoid double negative", 
             "sentence": "You don't need no additional software"},
            {"category": "Comma Splices", "feedback": "fix comma splice", 
             "sentence": "The system is running, it's working fine"},
            {"category": "Dangling Modifiers", "feedback": "fix dangling modifier", 
             "sentence": "Walking to the store, the rain started falling"},
            {"category": "Split Infinitives", "feedback": "avoid split infinitive", 
             "sentence": "Make sure to carefully review the document"},
            {"category": "Wordiness", "feedback": "reduce wordiness", 
             "sentence": "Due to the fact that the system is not working, we need to fix it"},
            {"category": "Unclear Pronouns", "feedback": "clarify pronoun reference", 
             "sentence": "When you save the file, it will update it automatically"},
            {"category": "Mixed Metaphors", "feedback": "fix mixed metaphor", 
             "sentence": "Don't burn bridges until you come to them"},
            {"category": "Redundant Words", "feedback": "remove redundancy", 
             "sentence": "Please repeat again and do it over once more"},
            {"category": "Subject-Verb Disagreement", "feedback": "fix subject-verb agreement", 
             "sentence": "The list of items are incomplete"},
            {"category": "Apostrophe Errors", "feedback": "fix apostrophe usage", 
             "sentence": "The API's are working but the URL's need updates"},
            {"category": "Run-on Sentences", "feedback": "fix run-on sentence", 
             "sentence": "The application starts then it loads the configuration and after that it connects to the database and finally displays the interface"},
            {"category": "Misplaced Modifiers", "feedback": "fix misplaced modifier", 
             "sentence": "Only available in the premium version, users can access this feature"},
            {"category": "Parallelism Issues", "feedback": "fix parallel structure", 
             "sentence": "The system allows saving, editing, and to delete files"},
            {"category": "Tense Inconsistency", "feedback": "fix tense consistency", 
             "sentence": "First you click Save, then you had to wait for confirmation"},
            {"category": "Weak Transitions", "feedback": "improve transitions", 
             "sentence": "Configure the settings. The system will restart."},
            {"category": "Vague Language", "feedback": "be more specific", 
             "sentence": "The system has some issues with certain files"},
            {"category": "Technical Jargon", "feedback": "simplify technical language", 
             "sentence": "Initialize the TCP/IP stack configuration parameters"},
        ]
        
        print("🔍 TESTING KB COVERAGE FOR COMPREHENSIVE WRITING ISSUES")
        print("=" * 65)
        
        for test in test_cases:
            print(f"\n📝 {test['category']}")
            result = self._test_single_case(test)
            self._categorize_result(test, result)
        
        return self._generate_report()
    
    def _test_single_case(self, test_case: Dict) -> Dict:
        """Test a single writing issue case"""
        try:
            response = requests.post(
                f"{self.base_url}/ai_suggestion",
                json={
                    "feedback": test_case["feedback"],
                    "sentence": test_case["sentence"]
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze quality
                method = result.get('method', 'unknown')
                sources = result.get('sources', [])
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                
                print(f"   ✅ Method: {method}")
                print(f"   📚 Sources: {len(sources)} found")
                print(f"   💡 Quality: {self._assess_quality(result)}")
                
                return {
                    "success": True,
                    "method": method,
                    "sources_count": len(sources),
                    "quality": self._assess_quality(result),
                    "response": result
                }
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:50]}...")
            return {"success": False, "error": str(e)}
    
    def _assess_quality(self, result: Dict) -> str:
        """Assess the quality of AI suggestion result"""
        method = result.get('method', '')
        sources = result.get('sources', [])
        ai_answer = result.get('ai_answer', '')
        suggestion = result.get('suggestion', '')
        
        # High quality: RAG with sources and specific guidance
        if 'chromadb' in method and len(sources) > 0 and len(ai_answer) > 20:
            return "HIGH"
        
        # Medium quality: RAG but limited sources or guidance
        elif 'rag' in method or 'chromadb' in method:
            return "MEDIUM"
        
        # Low quality: Generic fallback
        elif 'fallback' in method:
            return "LOW"
        
        # Unknown quality
        else:
            return "UNKNOWN"
    
    def _categorize_result(self, test_case: Dict, result: Dict):
        """Categorize result for reporting"""
        if not result.get("success"):
            self.errors.append({
                "category": test_case["category"],
                "error": result.get("error"),
                "test": test_case
            })
        elif result.get("quality") == "LOW":
            self.low_quality.append({
                "category": test_case["category"],
                "method": result.get("method"),
                "test": test_case
            })
        elif result.get("sources_count", 0) == 0:
            self.gaps.append({
                "category": test_case["category"],
                "method": result.get("method"),
                "test": test_case
            })
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive gap analysis report"""
        print("\n" + "="*65)
        print("📊 KB GAP ANALYSIS REPORT")
        print("="*65)
        
        print(f"\n❌ ERRORS: {len(self.errors)}")
        for error in self.errors:
            print(f"   • {error['category']}: {error['error']}")
        
        print(f"\n🔍 KNOWLEDGE GAPS: {len(self.gaps)}")
        for gap in self.gaps:
            print(f"   • {gap['category']}: {gap['method']} (no sources)")
        
        print(f"\n⚠️  LOW QUALITY: {len(self.low_quality)}")
        for low in self.low_quality:
            print(f"   • {low['category']}: {low['method']}")
        
        return {
            "errors": self.errors,
            "gaps": self.gaps,
            "low_quality": self.low_quality,
            "total_issues": len(self.errors) + len(self.gaps) + len(self.low_quality)
        }

def main():
    analyzer = KBGapAnalyzer()
    try:
        results = analyzer.test_writing_issues()
        
        print(f"\n🎯 RECOMMENDATIONS TO IMPROVE KB:")
        print("="*65)
        
        if results["total_issues"] == 0:
            print("🟢 KB coverage is excellent! No gaps found.")
        else:
            print("📝 Add these missing rule types to KB:")
            
            # Extract missing categories
            missing_categories = set()
            for gap in results["gaps"]:
                missing_categories.add(gap["category"])
            for low in results["low_quality"]:
                missing_categories.add(low["category"])
                
            for i, category in enumerate(sorted(missing_categories), 1):
                print(f"   {i}. {category}")
    
    except requests.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server")
        print("   Make sure the server is running on http://localhost:5000")

if __name__ == "__main__":
    main()
