"""
Knowledge Base Evaluation System

Tests retrieval quality and tracks metrics over time.
Minimal but effective CSV-based evaluation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationCase:
    """A single test case for evaluating retrieval."""
    query: str
    expected_rule: str
    should_rewrite: bool
    expected_severity: str = "medium"
    notes: str = ""


@dataclass
class EvaluationResult:
    """Result of evaluating one case."""
    query: str
    expected_rule: str
    actual_top_rules: List[str]
    hit_at_position: int  # 0 if not found in top-k
    should_rewrite: bool
    rewrite_correct: bool
    retrieval_score: float
    timestamp: str


class KBEvaluator:
    """Evaluates knowledge base retrieval quality."""
    
    def __init__(self, test_cases_file: str = "data/kb_test_cases.csv",
                 results_file: str = "data/kb_evaluation_results.csv"):
        self.test_cases_file = test_cases_file
        self.results_file = results_file
        self.test_cases: List[EvaluationCase] = []
        self.results: List[EvaluationResult] = []
    
    def load_test_cases(self) -> List[EvaluationCase]:
        """Load test cases from CSV."""
        test_cases = []
        
        try:
            with open(self.test_cases_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    test_cases.append(EvaluationCase(
                        query=row['query'],
                        expected_rule=row['expected_rule'],
                        should_rewrite=row['should_rewrite'].lower() == 'true',
                        expected_severity=row.get('expected_severity', 'medium'),
                        notes=row.get('notes', '')
                    ))
        except FileNotFoundError:
            logger.warning(f"Test cases file not found: {self.test_cases_file}")
            logger.info("Creating sample test cases file...")
            self.create_sample_test_cases()
            return self.load_test_cases()
        
        self.test_cases = test_cases
        logger.info(f"Loaded {len(test_cases)} test cases")
        return test_cases
    
    def create_sample_test_cases(self):
        """Create sample test cases CSV."""
        sample_cases = [
            {
                "query": "sentence with passive voice",
                "expected_rule": "PASSIVE_VOICE",
                "should_rewrite": "true",
                "expected_severity": "medium",
                "notes": "Test basic passive voice detection"
            },
            {
                "query": "very long sentence with many clauses",
                "expected_rule": "LONG_SENTENCES",
                "should_rewrite": "true",
                "expected_severity": "medium",
                "notes": "Test long sentence detection"
            },
            {
                "query": "text with very important adverb",
                "expected_rule": "ADVERBS",
                "should_rewrite": "true",
                "expected_severity": "low",
                "notes": "Test adverb detection"
            },
            {
                "query": "UI button label says Save",
                "expected_rule": "UI_LABEL",
                "should_rewrite": "false",
                "expected_severity": "critical",
                "notes": "Test negative knowledge - do not rewrite UI labels"
            },
            {
                "query": "error code ERROR_404 in documentation",
                "expected_rule": "ERROR_CODE",
                "should_rewrite": "false",
                "expected_severity": "critical",
                "notes": "Test negative knowledge - do not rewrite error codes"
            },
            {
                "query": "how to write a procedure",
                "expected_rule": "PATTERN_PROCEDURE",
                "should_rewrite": "false",
                "expected_severity": "medium",
                "notes": "Test pattern retrieval"
            },
            {
                "query": "when to use numbered lists",
                "expected_rule": "PATTERN_LISTS",
                "should_rewrite": "false",
                "expected_severity": "medium",
                "notes": "Test pattern retrieval"
            },
            {
                "query": "nominalization in sentence",
                "expected_rule": "NOMINALIZATIONS",
                "should_rewrite": "true",
                "expected_severity": "medium",
                "notes": "Test nominalization detection"
            },
            {
                "query": "vague terms like various and several",
                "expected_rule": "VAGUE_TERMS",
                "should_rewrite": "true",
                "expected_severity": "medium",
                "notes": "Test vague terms detection"
            },
            {
                "query": "inconsistent verb tense",
                "expected_rule": "VERB_TENSE",
                "should_rewrite": "true",
                "expected_severity": "medium",
                "notes": "Test verb tense consistency"
            }
        ]
        
        Path(self.test_cases_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.test_cases_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['query', 'expected_rule', 'should_rewrite', 'expected_severity', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_cases)
        
        logger.info(f"Created sample test cases at {self.test_cases_file}")
    
    def run_evaluation(self, top_k: int = 3) -> Dict[str, Any]:
        """
        Run evaluation against knowledge base.
        
        Note: This is a stub that needs integration with your actual
        RAG retrieval system. Replace the mock retrieval with real calls.
        """
        logger.info("\n" + "=" * 60)
        logger.info("RUNNING KNOWLEDGE BASE EVALUATION")
        logger.info("=" * 60)
        
        self.load_test_cases()
        
        if not self.test_cases:
            logger.error("No test cases to evaluate")
            return {}
        
        results = []
        hits = 0
        total = len(self.test_cases)
        
        for i, case in enumerate(self.test_cases, 1):
            logger.info(f"\nTest {i}/{total}: {case.query}")
            
            # TODO: Replace with actual RAG retrieval
            # For now, this is a mock that you'll integrate with your vector store
            retrieved_chunks = self.mock_retrieve(case.query, top_k=top_k)
            
            # Extract rule IDs from retrieved chunks
            retrieved_rules = [chunk.get('rule_id', '') for chunk in retrieved_chunks]
            retrieved_rules = [r for r in retrieved_rules if r]  # Filter empty
            
            # Check if expected rule is in top-k
            hit_position = 0
            if case.expected_rule in retrieved_rules:
                hit_position = retrieved_rules.index(case.expected_rule) + 1
                hits += 1
                logger.info(f"   ✅ Hit at position {hit_position}")
            else:
                logger.info(f"   ❌ Miss (expected {case.expected_rule}, got {retrieved_rules[:3]})")
            
            # Check rewrite flag
            rewrite_flags = [chunk.get('rewrite_allowed', True) for chunk in retrieved_chunks]
            actual_rewrite = rewrite_flags[0] if rewrite_flags else True
            rewrite_correct = actual_rewrite == case.should_rewrite
            
            # Calculate retrieval score (1.0 for position 1, 0.5 for position 2, etc.)
            score = 1.0 / hit_position if hit_position > 0 else 0.0
            
            result = EvaluationResult(
                query=case.query,
                expected_rule=case.expected_rule,
                actual_top_rules=retrieved_rules[:top_k],
                hit_at_position=hit_position,
                should_rewrite=case.should_rewrite,
                rewrite_correct=rewrite_correct,
                retrieval_score=score,
                timestamp=datetime.now().isoformat()
            )
            
            results.append(result)
        
        self.results = results
        
        # Compute metrics
        metrics = {
            "total_cases": total,
            "hits": hits,
            "misses": total - hits,
            "hit_rate": hits / total if total > 0 else 0,
            "average_retrieval_score": sum(r.retrieval_score for r in results) / total if total > 0 else 0,
            "rewrite_accuracy": sum(1 for r in results if r.rewrite_correct) / total if total > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Print metrics
        logger.info("\n" + "=" * 60)
        logger.info("EVALUATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"\n📊 Hit Rate: {metrics['hit_rate']:.1%}")
        logger.info(f"📊 Average Retrieval Score: {metrics['average_retrieval_score']:.2f}")
        logger.info(f"📊 Rewrite Decision Accuracy: {metrics['rewrite_accuracy']:.1%}")
        
        if metrics['hit_rate'] < 0.7:
            logger.warning("\n⚠️  Warning: Hit rate below 70%")
            logger.warning("   Your chunks may be poorly structured or too generic")
            logger.warning("   Consider: 1) More specific questions, 2) Better answers, 3) More examples")
        elif metrics['hit_rate'] >= 0.9:
            logger.info("\n✅ Excellent hit rate (>90%)")
        else:
            logger.info("\n✅ Good hit rate (70-90%)")
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def mock_retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Mock retrieval for testing.
        
        TODO: Replace this with actual calls to your vector store.
        
        Example integration:
            from app.services.vectorstore import search_chunks
            return search_chunks(query, top_k=top_k)
        """
        # This is a placeholder that returns mock results
        # You need to integrate this with your actual RAG system
        mock_results = [
            {
                "rule_id": "PASSIVE_VOICE",
                "title": "Passive Voice - Definition",
                "score": 0.85,
                "rewrite_allowed": True
            },
            {
                "rule_id": "LONG_SENTENCES",
                "title": "Long Sentences - Why",
                "score": 0.65,
                "rewrite_allowed": True
            },
            {
                "rule_id": "ADVERBS",
                "title": "Weak Adverbs - Example",
                "score": 0.55,
                "rewrite_allowed": True
            }
        ]
        
        return mock_results[:top_k]
    
    def save_results(self, metrics: Dict[str, Any]):
        """Save evaluation results to CSV."""
        # Save detailed results
        results_path = Path(self.results_file)
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_exists = results_path.exists()
        
        with open(results_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'query', 'expected_rule', 'actual_top_rules',
                'hit_at_position', 'should_rewrite', 'rewrite_correct', 'retrieval_score'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'timestamp': result.timestamp,
                    'query': result.query,
                    'expected_rule': result.expected_rule,
                    'actual_top_rules': '|'.join(result.actual_top_rules),
                    'hit_at_position': result.hit_at_position,
                    'should_rewrite': result.should_rewrite,
                    'rewrite_correct': result.rewrite_correct,
                    'retrieval_score': f"{result.retrieval_score:.2f}"
                })
        
        logger.info(f"\n💾 Saved detailed results to {results_path}")
        
        # Save metrics summary
        metrics_path = results_path.parent / "kb_evaluation_metrics.json"
        
        # Load existing metrics if file exists
        all_metrics = []
        if metrics_path.exists():
            with open(metrics_path, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
        
        all_metrics.append(metrics)
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(all_metrics, f, indent=2)
        
        logger.info(f"💾 Saved metrics summary to {metrics_path}")


def main():
    """Main entry point."""
    evaluator = KBEvaluator()
    metrics = evaluator.run_evaluation(top_k=3)
    
    if not metrics:
        logger.error("Evaluation failed")
        return 1
    
    logger.info("\n✅ Evaluation complete")
    
    # Suggest next steps
    if metrics['hit_rate'] < 0.7:
        logger.info("\n📋 Suggested Actions:")
        logger.info("   1. Review failed test cases in results file")
        logger.info("   2. Add more specific chunks for missed queries")
        logger.info("   3. Improve chunk questions to better match user queries")
        logger.info("   4. Add more rewrite examples for poorly-retrieved rules")
    
    return 0


if __name__ == "__main__":
    exit(main())
