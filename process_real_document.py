"""
Real Document Processor - End-to-End Example

Shows how ONE messy document becomes dozens of decision chunks.

This demonstrates the uncomfortable truth:
- Real sentences are messy
- Context matters
- Same rule, different decisions
- Rejections are as valuable as acceptances
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.decision_chunk import DecisionChunk
from app.rewrite_decision_logger import (
    get_history_logger,
    capture_rewrite_suggestion,
    capture_user_response,
    ConfidenceLevel
)
from mine_real_history import RealHistoryMiner
from typing import List, Dict, Any
import time


class RealDocumentProcessor:
    """
    Process a real document and show chunk generation.
    
    This is the PROOF that the system works with messy reality.
    """
    
    def __init__(self):
        self.history_logger = get_history_logger()
        self.generated_chunks = []
    
    def process_document(self, document: str, doc_type: str = "manual") -> Dict[str, Any]:
        """
        Process a real document end-to-end.
        
        Returns statistics about what was generated.
        """
        print("\n" + "="*60)
        print("PROCESSING REAL DOCUMENT")
        print("="*60)
        
        # Split into sentences (naive, but shows the pattern)
        sentences = self._split_sentences(document)
        print(f"\n📄 Document has {len(sentences)} sentences")
        
        stats = {
            "sentences_analyzed": len(sentences),
            "rules_triggered": 0,
            "rewrites_suggested": 0,
            "decisions_logged": 0
        }
        
        # Process each sentence
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            print(f"\n{'─'*60}")
            print(f"Sentence {i+1}: {sentence[:80]}...")
            
            # Get context
            context = {
                "doc_id": "real_doc_001",
                "doc_type": doc_type,
                "sentence_before": sentences[i-1] if i > 0 else "",
                "sentence_after": sentences[i+1] if i < len(sentences)-1 else "",
                "paragraph": self._get_paragraph(sentences, i),
                "severity": "medium"
            }
            
            # Analyze (with real rule logic)
            decisions = self._analyze_sentence_realistic(sentence, context)
            
            if decisions:
                stats["rules_triggered"] += len(decisions)
                print(f"  ⚠️  {len(decisions)} issues found")
                
                for decision in decisions:
                    # Log decision
                    self.history_logger.log_decision(decision)
                    stats["decisions_logged"] += 1
                    
                    print(f"     • {decision.rule_name}: {decision.justification[:60]}...")
                    
                    if decision.suggested_rewrite:
                        stats["rewrites_suggested"] += 1
        
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}\n")
        
        return stats
    
    def simulate_user_responses(self, accept_rate: float = 0.7):
        """
        Simulate user responses to logged decisions.
        
        In reality, this comes from actual user interaction.
        Here we simulate to show the full pipeline.
        """
        print("\n" + "="*60)
        print("SIMULATING USER RESPONSES")
        print("="*60)
        
        decisions = self.history_logger.load_history()
        print(f"\n📋 Processing {len(decisions)} logged decisions")
        
        import random
        
        for decision in decisions:
            # Simulate user decision (would be real in production)
            accepted = random.random() < accept_rate
            
            if accepted:
                # User accepts suggestion
                capture_user_response(
                    decision_id=decision.id,
                    accepted=True,
                    actual_rewrite=decision.suggested_rewrite,
                    time_to_decision_ms=random.randint(1000, 5000)
                )
                print(f"  ✅ Accepted: {decision.rule_name}")
            else:
                # User rejects with reason
                rejection_reasons = [
                    "Technical term that requires this structure",
                    "Context makes passive voice appropriate here",
                    "UI label must match interface exactly",
                    "This is a quoted passage",
                    "Industry standard terminology"
                ]
                reason = random.choice(rejection_reasons)
                
                capture_user_response(
                    decision_id=decision.id,
                    accepted=False,
                    rejection_reason=reason,
                    time_to_decision_ms=random.randint(500, 3000)
                )
                print(f"  ❌ Rejected: {decision.rule_name} - {reason[:40]}...")
    
    def mine_and_show_chunks(self) -> List[DecisionChunk]:
        """
        Mine the logged decisions into chunks and show results.
        """
        print("\n" + "="*60)
        print("MINING CHUNKS FROM LOGGED DECISIONS")
        print("="*60)
        
        miner = RealHistoryMiner()
        chunks = miner.mine_all()
        
        self.generated_chunks = chunks
        
        # Show some examples
        print("\n📚 Sample Generated Chunks:")
        print("─"*60)
        
        for chunk_type in ["example", "negative", "exception"]:
            matching = [c for c in chunks if c.knowledge_type == chunk_type]
            if matching:
                chunk = matching[0]
                print(f"\n🔹 {chunk_type.upper()} Chunk:")
                print(f"   Q: {chunk.question[:60]}...")
                print(f"   A: {chunk.answer[:100]}...")
                print(f"   Rule: {chunk.rule_id}")
                print(f"   Rewrite OK: {chunk.rewrite_allowed}")
        
        return chunks
    
    def _split_sentences(self, document: str) -> List[str]:
        """Naive sentence splitting."""
        import re
        # Simple sentence splitting (improve with spaCy in production)
        sentences = re.split(r'[.!?]+\s+', document)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_paragraph(self, sentences: List[str], index: int) -> str:
        """Get paragraph context."""
        # Simple: take sentence with before/after
        start = max(0, index - 1)
        end = min(len(sentences), index + 2)
        return ' '.join(sentences[start:end])
    
    def _analyze_sentence_realistic(self, sentence: str, context: Dict) -> List[Any]:
        """
        Realistic analysis with messy cases.
        
        This shows the REAL complexity:
        - Multiple rules can trigger
        - Confidence varies
        - Context affects decisions
        """
        decisions = []
        
        # Check passive voice
        if self._has_passive_voice(sentence):
            confidence = self._calculate_passive_confidence(sentence, context)
            suggested = self._generate_passive_rewrite(sentence) if confidence in ["high", "medium"] else None
            
            decision = capture_rewrite_suggestion(
                sentence=sentence,
                rule_id="PASSIVE_VOICE",
                rule_name="Passive Voice",
                suggested_rewrite=suggested or "",
                justification="Passive voice obscures the actor. Active voice is clearer.",
                confidence=confidence,
                document_context=context
            )
            decisions.append(decision)
        
        # Check sentence length
        word_count = len(sentence.split())
        if word_count > 25:
            confidence = "high" if word_count > 35 else "medium"
            
            decision = capture_rewrite_suggestion(
                sentence=sentence,
                rule_id="LONG_SENTENCES",
                rule_name="Long Sentences",
                suggested_rewrite="",  # Would need AI to split
                justification=f"This {word_count}-word sentence is difficult to read. Break into shorter sentences.",
                confidence=confidence,
                document_context=context
            )
            decisions.append(decision)
        
        # Check adverbs
        if self._has_weak_adverbs(sentence):
            decision = capture_rewrite_suggestion(
                sentence=sentence,
                rule_id="ADVERBS",
                rule_name="Weak Adverbs",
                suggested_rewrite="",
                justification="Adverbs often weaken writing. Consider stronger verbs instead.",
                confidence="low",
                document_context=context
            )
            decisions.append(decision)
        
        return decisions
    
    def _has_passive_voice(self, sentence: str) -> bool:
        """Detect passive voice (simplified)."""
        # Real implementation uses spaCy
        passive_patterns = [
            r'\bis\s+\w+ed\b',
            r'\bwas\s+\w+ed\b',
            r'\bare\s+\w+ed\b',
            r'\bwere\s+\w+ed\b',
            r'\bbeen\s+\w+ed\b',
            r'\bby\s+the\b'
        ]
        import re
        return any(re.search(pattern, sentence, re.IGNORECASE) for pattern in passive_patterns)
    
    def _calculate_passive_confidence(self, sentence: str, context: Dict) -> str:
        """Calculate confidence for passive voice detection."""
        # High confidence: clear passive with "by"
        if "by" in sentence.lower() and self._has_passive_voice(sentence):
            return "high"
        
        # Low confidence: UI or technical docs
        if context["doc_type"] in ["ui", "api"]:
            return "low"
        
        # Medium: everything else
        return "medium"
    
    def _generate_passive_rewrite(self, sentence: str) -> str:
        """Generate a suggested rewrite (simplified)."""
        # In production, use AI or more sophisticated logic
        # For now, return placeholder
        return f"[Suggested rewrite for: {sentence[:40]}...]"
    
    def _has_weak_adverbs(self, sentence: str) -> bool:
        """Detect weak adverbs."""
        weak_adverbs = ['very', 'really', 'quite', 'rather', 'somewhat']
        return any(adv in sentence.lower() for adv in weak_adverbs)


# Sample messy document
SAMPLE_MESSY_DOCUMENT = """
The system was designed to handle multiple concurrent users accessing shared resources. 
When a request is received by the server, it is first validated against the authentication 
service before being processed by the main application logic which consists of several 
interconnected components that work together to ensure data consistency and reliability 
across the entire platform.

Error handling is implemented through a very comprehensive exception management system 
that catches and logs all errors that are raised during normal operation. The monitoring 
dashboard displays real-time metrics that are updated every 30 seconds and can be accessed 
by administrators through the Settings menu under System > Monitoring > Live View.

In cases where the database connection is lost, the system automatically switches to a 
backup connection that was configured during the initial setup process. This failover 
mechanism has been tested extensively and is proven to work reliably under various 
failure scenarios.

The Save button must be clicked to persist changes. Configuration options are described 
in the Administrator's Guide. WARNING: Do not modify system files directly as this may 
cause unexpected behavior.
"""


def main():
    """Run the end-to-end demonstration."""
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║    Real Document → Decision Chunks                      ║
    ║    End-to-End Demonstration                             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    processor = RealDocumentProcessor()
    
    # Step 1: Process document
    print("\n📝 Step 1: Processing messy document...")
    stats = processor.process_document(SAMPLE_MESSY_DOCUMENT, doc_type="manual")
    
    print(f"\n📊 Processing Statistics:")
    print(f"   Sentences analyzed: {stats['sentences_analyzed']}")
    print(f"   Rules triggered: {stats['rules_triggered']}")
    print(f"   Rewrites suggested: {stats['rewrites_suggested']}")
    print(f"   Decisions logged: {stats['decisions_logged']}")
    
    # Step 2: Simulate user responses
    print("\n🎭 Step 2: Simulating user responses...")
    processor.simulate_user_responses(accept_rate=0.7)
    
    # Step 3: Mine chunks
    print("\n⛏️  Step 3: Mining chunks from decisions...")
    chunks = processor.mine_and_show_chunks()
    
    print(f"\n{'='*60}")
    print("✅ DEMONSTRATION COMPLETE")
    print(f"{'='*60}")
    print(f"\n🎉 Generated {len(chunks)} decision chunks from 1 document")
    print(f"\n💡 Key Insight:")
    print(f"   One messy document → {stats['decisions_logged']} decisions")
    print(f"   {stats['decisions_logged']} decisions → {len(chunks)} chunks")
    print(f"   Average: {len(chunks) / stats['decisions_logged']:.1f} chunks per decision")
    
    print(f"\n📁 Data logged to:")
    print(f"   - data/rewrite_history.jsonl")
    print(f"   - data/mined_chunks.json")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Integrate logging into your real app (see integration_template.py)")
    print(f"   2. Process 10-20 real documents")
    print(f"   3. Collect user accept/reject feedback")
    print(f"   4. Run: python mine_real_history.py")
    print(f"   5. Merge mined chunks with base KB")
    print(f"   6. You'll have 500+ chunks of REAL knowledge")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
