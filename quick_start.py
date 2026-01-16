"""
Quick Start Script - Build and Evaluate Knowledge Base

Run this to:
1. Generate all chunks
2. Validate them
3. Save to JSON
4. Run evaluation
5. Show results
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable] + cmd,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Failed with return code {result.returncode}")
        return False
    
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        DocScanner Knowledge Base - Quick Start            ║
    ║                                                           ║
    ║   From Theory to Execution - Decision-Focused RAG        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Build knowledge base
    if not run_command(['build_knowledge_base.py'], 'Building Knowledge Base'):
        print("\n❌ Build failed. Check errors above.")
        return 1
    
    # Step 2: Run evaluation
    if not run_command(['evaluate_knowledge_base.py'], 'Evaluating Knowledge Base'):
        print("\n❌ Evaluation failed. Check errors above.")
        return 1
    
    # Step 3: Summary
    print("\n" + "="*60)
    print("✅ QUICK START COMPLETE")
    print("="*60)
    
    kb_file = Path('data/knowledge_base.json')
    if kb_file.exists():
        size_kb = kb_file.stat().st_size / 1024
        print(f"\n📁 Knowledge base: data/knowledge_base.json ({size_kb:.1f} KB)")
    
    print("\n📊 Next Steps:")
    print("   1. Review: data/knowledge_base.json")
    print("   2. Check metrics: data/kb_evaluation_metrics.json")
    print("   3. Add more rules in: chunk_factory/rule_chunks.py")
    print("   4. Mine rewrites in: chunk_factory/example_chunks.py")
    print("   5. Integrate with vector store (see IMPLEMENTATION_STATUS.md)")
    
    print("\n📖 Documentation:")
    print("   - KNOWLEDGE_BASE_IMPLEMENTATION.md - Full guide")
    print("   - IMPLEMENTATION_STATUS.md - Current status & next steps")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
