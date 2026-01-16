"""
Knowledge Base Builder - Generate and index all decision chunks.

This is the main orchestrator that:
1. Generates chunks from all factories
2. Validates chunks
3. Indexes to vector database
4. Reports statistics

Run this to rebuild your entire knowledge base.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from chunk_factory.rule_chunks import generate_rule_chunks
from chunk_factory.example_chunks import generate_example_chunks
from chunk_factory.exception_chunks import generate_exception_chunks
from chunk_factory.pattern_chunks import generate_pattern_chunks
from app.decision_chunk import DecisionChunk, validate_chunk_collection
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    """Builds and manages the knowledge base."""
    
    def __init__(self, output_file: str = "data/knowledge_base.json"):
        self.output_file = output_file
        self.chunks: List[DecisionChunk] = []
        self.stats = {}
    
    def generate_all_chunks(self) -> List[DecisionChunk]:
        """Generate chunks from all factories."""
        logger.info("=" * 60)
        logger.info("GENERATING KNOWLEDGE BASE CHUNKS")
        logger.info("=" * 60)
        
        all_chunks = []
        
        # 1. Rule chunks (target: 60+ from 10 rules × 6)
        logger.info("\n📋 Generating rule chunks...")
        rule_chunks = generate_rule_chunks()
        all_chunks.extend(rule_chunks)
        logger.info(f"   ✅ {len(rule_chunks)} rule chunks generated")
        
        # 2. Example chunks from rewrites (target: 30+ from 10 rewrites × 3)
        logger.info("\n📚 Generating example chunks...")
        example_chunks = generate_example_chunks()
        all_chunks.extend(example_chunks)
        logger.info(f"   ✅ {len(example_chunks)} example chunks generated")
        
        # 3. Negative knowledge chunks (target: 100+)
        logger.info("\n🚫 Generating negative knowledge chunks...")
        exception_chunks = generate_exception_chunks()
        all_chunks.extend(exception_chunks)
        logger.info(f"   ✅ {len(exception_chunks)} negative knowledge chunks generated")
        
        # 4. Pattern chunks (target: 50+)
        logger.info("\n📐 Generating pattern chunks...")
        pattern_chunks = generate_pattern_chunks()
        all_chunks.extend(pattern_chunks)
        logger.info(f"   ✅ {len(pattern_chunks)} pattern chunks generated")
        
        self.chunks = all_chunks
        return all_chunks
    
    def validate_chunks(self) -> bool:
        """Validate all chunks before indexing."""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATING CHUNKS")
        logger.info("=" * 60)
        
        # Check pre-embedding gates
        errors = []
        
        # 1. Token count validation
        logger.info("\n🔍 Checking token counts...")
        for chunk in self.chunks:
            token_count = chunk.get_token_count()
            if token_count > 200:
                errors.append(f"Chunk {chunk.id} exceeds 200 tokens: {token_count}")
        
        if not errors:
            logger.info("   ✅ All chunks under 200 tokens")
        
        # 2. Mandatory metadata validation
        logger.info("\n🔍 Checking mandatory metadata...")
        required_fields = ["knowledge_type", "rewrite_allowed", "severity", "doc_type"]
        
        for chunk in self.chunks:
            for field in required_fields:
                if not hasattr(chunk, field) or getattr(chunk, field) is None:
                    errors.append(f"Chunk {chunk.id} missing required field: {field}")
        
        if not errors:
            logger.info("   ✅ All chunks have required metadata")
        
        # 3. Collection-level validation
        logger.info("\n🔍 Checking for duplicates and consistency...")
        is_valid, validation_errors = validate_chunk_collection(self.chunks)
        errors.extend(validation_errors)
        
        # Report errors
        if errors:
            logger.error(f"\n❌ Validation failed with {len(errors)} errors:")
            for error in errors[:10]:  # Show first 10
                logger.error(f"   - {error}")
            if len(errors) > 10:
                logger.error(f"   ... and {len(errors) - 10} more errors")
            return False
        
        logger.info("   ✅ No duplicates or consistency issues found")
        logger.info("\n✅ All validation checks passed")
        return True
    
    def compute_statistics(self) -> Dict[str, Any]:
        """Compute knowledge base statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("KNOWLEDGE BASE STATISTICS")
        logger.info("=" * 60)
        
        stats = {
            "total_chunks": len(self.chunks),
            "by_knowledge_type": {},
            "by_doc_type": {},
            "by_severity": {},
            "by_rewrite_allowed": {"true": 0, "false": 0},
            "token_distribution": {
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0
            },
            "health_status": "",
            "generated_at": datetime.now().isoformat()
        }
        
        # Count by knowledge type
        for chunk in self.chunks:
            kt = chunk.knowledge_type
            stats["by_knowledge_type"][kt] = stats["by_knowledge_type"].get(kt, 0) + 1
            
            dt = chunk.doc_type
            stats["by_doc_type"][dt] = stats["by_doc_type"].get(dt, 0) + 1
            
            sev = chunk.severity
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
            
            if chunk.rewrite_allowed:
                stats["by_rewrite_allowed"]["true"] += 1
            else:
                stats["by_rewrite_allowed"]["false"] += 1
        
        # Token statistics
        token_counts = [chunk.get_token_count() for chunk in self.chunks]
        if token_counts:
            stats["token_distribution"]["min"] = min(token_counts)
            stats["token_distribution"]["max"] = max(token_counts)
            stats["token_distribution"]["avg"] = sum(token_counts) / len(token_counts)
            stats["token_distribution"]["median"] = sorted(token_counts)[len(token_counts) // 2]
        
        # Health status
        total = stats["total_chunks"]
        if total < 500:
            stats["health_status"] = "UNDERFED"
            status_emoji = "⚠️"
        elif total < 1200:
            stats["health_status"] = "HEALTHY"
            status_emoji = "✅"
        else:
            stats["health_status"] = "NOISY"
            status_emoji = "⚠️"
        
        # Print statistics
        logger.info(f"\n{status_emoji} Health Status: {stats['health_status']}")
        logger.info(f"📊 Total Chunks: {stats['total_chunks']}")
        
        logger.info("\n📂 By Knowledge Type:")
        for kt, count in stats["by_knowledge_type"].items():
            logger.info(f"   {kt:15} : {count:4} ({count/total*100:.1f}%)")
        
        logger.info("\n📁 By Document Type:")
        for dt, count in stats["by_doc_type"].items():
            logger.info(f"   {dt:20} : {count:4} ({count/total*100:.1f}%)")
        
        logger.info("\n⚡ By Severity:")
        for sev in ["low", "medium", "high", "critical"]:
            count = stats["by_severity"].get(sev, 0)
            logger.info(f"   {sev:10} : {count:4} ({count/total*100:.1f}%)")
        
        logger.info("\n✏️  Rewrite Allowed:")
        logger.info(f"   Yes: {stats['by_rewrite_allowed']['true']:4} ({stats['by_rewrite_allowed']['true']/total*100:.1f}%)")
        logger.info(f"   No:  {stats['by_rewrite_allowed']['false']:4} ({stats['by_rewrite_allowed']['false']/total*100:.1f}%)")
        
        logger.info("\n🔢 Token Distribution:")
        logger.info(f"   Min:    {stats['token_distribution']['min']}")
        logger.info(f"   Max:    {stats['token_distribution']['max']}")
        logger.info(f"   Avg:    {stats['token_distribution']['avg']:.1f}")
        logger.info(f"   Median: {stats['token_distribution']['median']}")
        
        self.stats = stats
        return stats
    
    def save_to_file(self):
        """Save chunks to JSON file."""
        logger.info("\n" + "=" * 60)
        logger.info("SAVING TO FILE")
        logger.info("=" * 60)
        
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert chunks to dictionaries
        chunks_data = [chunk.to_dict() for chunk in self.chunks]
        
        # Create output structure
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_chunks": len(chunks_data),
                "version": "1.0",
                "statistics": self.stats
            },
            "chunks": chunks_data
        }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved {len(chunks_data)} chunks to {output_path}")
        logger.info(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    def build(self) -> bool:
        """Main build process."""
        logger.info("\n" + "🔨 " * 30)
        logger.info("BUILDING KNOWLEDGE BASE")
        logger.info("🔨 " * 30)
        
        # Generate chunks
        self.generate_all_chunks()
        
        # Validate chunks
        if not self.validate_chunks():
            logger.error("\n❌ Build failed: Validation errors")
            return False
        
        # Compute statistics
        self.compute_statistics()
        
        # Save to file
        self.save_to_file()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ BUILD COMPLETE")
        logger.info("=" * 60)
        
        return True


def main():
    """Main entry point."""
    builder = KnowledgeBaseBuilder(output_file="data/knowledge_base.json")
    
    success = builder.build()
    
    if success:
        logger.info("\n🎉 Knowledge base built successfully!")
        logger.info(f"📊 Total chunks: {builder.stats['total_chunks']}")
        logger.info(f"💚 Status: {builder.stats['health_status']}")
        
        if builder.stats['health_status'] == 'UNDERFED':
            logger.warning("\n⚠️  Warning: Knowledge base is UNDERFED (< 500 chunks)")
            logger.warning("   Add more examples, rules, or patterns to reach 500+")
        elif builder.stats['health_status'] == 'NOISY':
            logger.warning("\n⚠️  Warning: Knowledge base is NOISY (> 1200 chunks)")
            logger.warning("   Consider pruning redundant chunks")
        else:
            logger.info("\n✅ Knowledge base size is healthy (500-1200 chunks)")
        
        return 0
    else:
        logger.error("\n❌ Knowledge base build failed")
        return 1


if __name__ == "__main__":
    exit(main())
