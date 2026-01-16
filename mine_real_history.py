"""
Real History Miner - Converts logged decisions into decision chunks.

This is where synthetic chunks become REAL chunks.

Takes rewrite_history.jsonl and generates:
- Bad example chunks (what triggered the rule)
- Corrected example chunks (what the rewrite was)
- Justification chunks (why it mattered)
- Rejection chunks (when NOT to rewrite - critical negative knowledge)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk
from app.rewrite_decision_logger import RewriteHistoryLogger, RewriteDecision
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealHistoryMiner:
    """
    Mines real rewrite history into decision chunks.
    
    This is the PRIMARY source of training data.
    """
    
    def __init__(self, history_file: str = "data/rewrite_history.jsonl"):
        self.history_logger = RewriteHistoryLogger(log_file=history_file)
        self.mined_chunks: List[DecisionChunk] = []
    
    def mine_accepted_rewrites(self) -> List[DecisionChunk]:
        """
        Mine chunks from accepted rewrites.
        
        These are HIGH CONFIDENCE examples of correct rewrites.
        """
        decisions = self.history_logger.load_history()
        chunks = []
        
        for decision in decisions:
            # Only process accepted rewrites
            if decision.user_accepted is not True:
                continue
            
            if not decision.actual_rewrite:
                continue
            
            # 1. Bad example chunk
            chunks.append(DecisionChunk.create(
                title=f"Real Example: {decision.rule_name} (Bad)",
                question=f"What's wrong with this sentence: '{decision.sentence}'?",
                answer=f"This sentence violates the {decision.rule_name} rule. {decision.justification}",
                knowledge_type="example",
                rule_id=decision.rule_id,
                rewrite_allowed=True,
                severity=decision.severity,
                doc_type=decision.document_type,
                metadata={
                    "source": "accepted_rewrite",
                    "decision_id": decision.id,
                    "confidence": decision.confidence,
                    "context_before": decision.sentence_before,
                    "context_after": decision.sentence_after
                }
            ))
            
            # 2. Corrected example chunk
            chunks.append(DecisionChunk.create(
                title=f"Real Example: {decision.rule_name} (Corrected)",
                question=f"How should this be rewritten: '{decision.sentence}'?",
                answer=f"Correct version: '{decision.actual_rewrite}'. This fixes the {decision.rule_name} issue because {decision.justification}",
                knowledge_type="example",
                rule_id=decision.rule_id,
                rewrite_allowed=True,
                severity=decision.severity,
                doc_type=decision.document_type,
                metadata={
                    "source": "accepted_rewrite",
                    "decision_id": decision.id,
                    "confidence": decision.confidence,
                    "original": decision.sentence,
                    "rewritten": decision.actual_rewrite
                }
            ))
            
            # 3. Justification chunk (with REAL context)
            chunks.append(DecisionChunk.create(
                title=f"Real Example: {decision.rule_name} (Justification)",
                question=f"In the context '{decision.paragraph}', why was '{decision.sentence}' rewritten?",
                answer=f"The sentence was rewritten because {decision.justification}. The corrected version '{decision.actual_rewrite}' is clearer and follows the {decision.rule_name} rule.",
                knowledge_type="example",
                rule_id=decision.rule_id,
                rewrite_allowed=True,
                severity=decision.severity,
                doc_type=decision.document_type,
                metadata={
                    "source": "accepted_rewrite",
                    "decision_id": decision.id,
                    "confidence": decision.confidence,
                    "has_context": True
                }
            ))
        
        logger.info(f"✅ Mined {len(chunks)} chunks from {len(decisions)} accepted rewrites")
        return chunks
    
    def mine_rejected_rewrites(self) -> List[DecisionChunk]:
        """
        Mine chunks from REJECTED rewrites.
        
        THIS IS GOLD - this is negative knowledge in the wild.
        These are cases where the rule triggered but SHOULD NOT have.
        """
        decisions = self.history_logger.load_history()
        chunks = []
        
        for decision in decisions:
            # Only process rejected rewrites
            if decision.user_accepted is not False:
                continue
            
            rejection_reason = decision.user_rejection_reason or "Context makes rewrite inappropriate"
            
            # Create negative knowledge chunk
            chunks.append(DecisionChunk.create(
                title=f"Do NOT Rewrite: {decision.rule_name} Exception",
                question=f"Should this sentence be rewritten: '{decision.sentence}'?",
                answer=f"NO. While this appears to violate {decision.rule_name}, it should NOT be rewritten. Reason: {rejection_reason}. Context: {decision.paragraph}",
                knowledge_type="negative",
                rule_id=decision.rule_id,
                rewrite_allowed=False,
                severity="high",  # Rejections are high-value knowledge
                doc_type=decision.document_type,
                metadata={
                    "source": "rejected_rewrite",
                    "decision_id": decision.id,
                    "suggested_rewrite": decision.suggested_rewrite,
                    "rejection_reason": rejection_reason,
                    "original_confidence": decision.confidence
                }
            ))
            
            # Also create exception chunk explaining the context
            chunks.append(DecisionChunk.create(
                title=f"Exception: {decision.rule_name} in {decision.document_type}",
                question=f"When should {decision.rule_name} NOT be applied?",
                answer=f"Do not apply {decision.rule_name} when: {rejection_reason}. Real example from {decision.document_type}: '{decision.sentence}' was correctly left unchanged.",
                knowledge_type="exception",
                rule_id=decision.rule_id,
                rewrite_allowed=False,
                severity="high",
                doc_type=decision.document_type,
                metadata={
                    "source": "rejected_rewrite",
                    "decision_id": decision.id,
                    "learned_from_user": True
                }
            ))
        
        logger.info(f"✅ Mined {len(chunks)} chunks from rejected rewrites (NEGATIVE KNOWLEDGE)")
        return chunks
    
    def mine_contextual_patterns(self) -> List[DecisionChunk]:
        """
        Mine chunks that show how context affects rewrite decisions.
        
        Same rule, different doc types, different decisions.
        """
        decisions = self.history_logger.load_history()
        chunks = []
        
        # Group by rule_id and doc_type
        by_rule_and_doc = {}
        for d in decisions:
            key = (d.rule_id, d.document_type)
            if key not in by_rule_and_doc:
                by_rule_and_doc[key] = []
            by_rule_and_doc[key].append(d)
        
        # For each rule+doctype combo, create contextual chunks
        for (rule_id, doc_type), group_decisions in by_rule_and_doc.items():
            if len(group_decisions) < 3:  # Need at least 3 examples
                continue
            
            accepted = [d for d in group_decisions if d.user_accepted is True]
            rejected = [d for d in group_decisions if d.user_accepted is False]
            
            if accepted:
                # Create a contextual rule chunk
                examples = [f"'{d.sentence}' → '{d.actual_rewrite}'" for d in accepted[:3]]
                chunks.append(DecisionChunk.create(
                    title=f"{rule_id} in {doc_type} documents",
                    question=f"How does {rule_id} apply to {doc_type} documentation?",
                    answer=f"In {doc_type} documentation, {rule_id} should be applied. Real examples: {'; '.join(examples)}",
                    knowledge_type="rule",
                    rule_id=rule_id,
                    rewrite_allowed=True,
                    severity="medium",
                    doc_type=doc_type,
                    metadata={
                        "source": "contextual_pattern",
                        "example_count": len(accepted)
                    }
                ))
            
            if rejected:
                # Create a contextual exception chunk
                reasons = list(set([d.user_rejection_reason for d in rejected if d.user_rejection_reason]))
                chunks.append(DecisionChunk.create(
                    title=f"{rule_id} exceptions in {doc_type}",
                    question=f"When should {rule_id} NOT be applied in {doc_type} documentation?",
                    answer=f"In {doc_type} documentation, {rule_id} should NOT be applied when: {'; '.join(reasons[:3])}",
                    knowledge_type="exception",
                    rule_id=rule_id,
                    rewrite_allowed=False,
                    severity="high",
                    doc_type=doc_type,
                    metadata={
                        "source": "contextual_pattern",
                        "rejection_count": len(rejected)
                    }
                ))
        
        logger.info(f"✅ Mined {len(chunks)} contextual pattern chunks")
        return chunks
    
    def mine_low_confidence_decisions(self) -> List[DecisionChunk]:
        """
        Mine chunks from LOW CONFIDENCE decisions.
        
        These are the messy, borderline cases that teach nuance.
        """
        decisions = self.history_logger.load_history()
        chunks = []
        
        for decision in decisions:
            if decision.confidence not in ["low", "uncertain"]:
                continue
            
            # Create nuanced example chunks
            outcome = "accepted" if decision.user_accepted else "rejected"
            
            chunks.append(DecisionChunk.create(
                title=f"Borderline Case: {decision.rule_name}",
                question=f"Is this a clear {decision.rule_name} violation: '{decision.sentence}'?",
                answer=f"This is a borderline case. The rule technically applies, but context matters. User decision: {outcome}. Reason: {decision.user_rejection_reason or decision.justification}",
                knowledge_type="example",
                rule_id=decision.rule_id,
                rewrite_allowed=decision.user_accepted or False,
                severity="low",  # Borderline cases are lower severity
                doc_type=decision.document_type,
                metadata={
                    "source": "low_confidence",
                    "decision_id": decision.id,
                    "confidence": decision.confidence,
                    "borderline": True
                }
            ))
        
        logger.info(f"✅ Mined {len(chunks)} chunks from low-confidence decisions")
        return chunks
    
    def mine_all(self) -> List[DecisionChunk]:
        """Mine all possible chunks from history."""
        logger.info("\n" + "="*60)
        logger.info("MINING REAL REWRITE HISTORY")
        logger.info("="*60)
        
        all_chunks = []
        
        # Mine accepted rewrites
        accepted_chunks = self.mine_accepted_rewrites()
        all_chunks.extend(accepted_chunks)
        
        # Mine rejected rewrites (CRITICAL)
        rejected_chunks = self.mine_rejected_rewrites()
        all_chunks.extend(rejected_chunks)
        
        # Mine contextual patterns
        contextual_chunks = self.mine_contextual_patterns()
        all_chunks.extend(contextual_chunks)
        
        # Mine low-confidence decisions
        borderline_chunks = self.mine_low_confidence_decisions()
        all_chunks.extend(borderline_chunks)
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ TOTAL MINED: {len(all_chunks)} chunks from real history")
        logger.info("="*60)
        
        self.mined_chunks = all_chunks
        return all_chunks
    
    def save_mined_chunks(self, output_file: str = "data/mined_chunks.json"):
        """Save mined chunks to file."""
        import json
        from datetime import datetime
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source": "real_rewrite_history",
                "total_chunks": len(self.mined_chunks)
            },
            "chunks": [chunk.to_dict() for chunk in self.mined_chunks]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(self.mined_chunks)} mined chunks to {output_path}")


def main():
    """Main entry point for mining real history."""
    miner = RealHistoryMiner()
    
    # Mine all chunks
    chunks = miner.mine_all()
    
    if not chunks:
        logger.warning("\n⚠️  No history to mine. Start logging rewrite decisions first!")
        logger.info("\nTo start collecting data:")
        logger.info("  1. Integrate rewrite_decision_logger.py into your app")
        logger.info("  2. Log every rewrite suggestion")
        logger.info("  3. Capture user acceptance/rejection")
        logger.info("  4. Run this script again")
        return 1
    
    # Save chunks
    miner.save_mined_chunks()
    
    # Statistics
    stats = {
        "accepted_examples": len([c for c in chunks if c.metadata.get("source") == "accepted_rewrite"]),
        "rejected_examples": len([c for c in chunks if c.metadata.get("source") == "rejected_rewrite"]),
        "contextual_patterns": len([c for c in chunks if c.metadata.get("source") == "contextual_pattern"]),
        "borderline_cases": len([c for c in chunks if c.metadata.get("source") == "low_confidence"])
    }
    
    logger.info("\n📊 Mining Statistics:")
    for key, count in stats.items():
        logger.info(f"   {key}: {count}")
    
    logger.info("\n✅ Real history mining complete")
    logger.info(f"📁 Mined chunks saved to: data/mined_chunks.json")
    logger.info(f"💡 Next: Merge with base KB using build_knowledge_base.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
