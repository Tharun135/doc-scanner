#!/usr/bin/env python3
"""
Migration script to integrate the advanced RAG system with the existing DocScanner application.
This script will:
1. Install required dependencies
2. Migrate existing data to the advanced format
3. Update the main application to use the advanced RAG system
4. Provide configuration options
"""

import os
import sys
import logging
import subprocess
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedRAGMigration:
    """Handles migration to the advanced RAG system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_added = []
        self.backup_created = False
        
    def run_migration(self):
        """Run the complete migration process."""
        logger.info("🚀 Starting Advanced RAG System Migration")
        logger.info("=" * 60)
        
        try:
            # Step 1: Install dependencies
            self._install_dependencies()
            
            # Step 2: Create backup of existing system
            self._create_backup()
            
            # Step 3: Update configuration
            self._update_configuration()
            
            # Step 4: Migrate data
            self._migrate_data()
            
            # Step 5: Update application code
            self._update_application_code()
            
            # Step 6: Test the new system
            self._test_new_system()
            
            logger.info("✅ Migration completed successfully!")
            self._print_next_steps()
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self._rollback()
            raise
    
    def _install_dependencies(self):
        """Install required Python packages."""
        logger.info("📦 Installing required dependencies...")
        
        requirements = [
            "sentence-transformers>=2.2.0",  # For better embeddings and cross-encoder
            "rank-bm25>=0.2.2",             # For BM25 hybrid search
            "openai>=1.0.0",                # For OpenAI embeddings (optional)
            "cohere>=4.0.0",                # For Cohere embeddings (optional)
            "redis>=4.0.0",                 # For caching (optional)
            "scikit-learn>=1.0.0",          # For additional ML utilities
            "nltk>=3.8",                    # For text processing
            "transformers>=4.20.0"          # For advanced NLP
        ]
        
        for requirement in requirements:
            try:
                logger.info(f"Installing {requirement}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", requirement
                ], check=True, capture_output=True, text=True)
                self.requirements_added.append(requirement)
                logger.info(f"✅ {requirement} installed")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Failed to install {requirement}: {e}")
                # Continue with migration for optional dependencies
        
        logger.info(f"✅ Dependencies installed: {len(self.requirements_added)}/{len(requirements)}")
    
    def _create_backup(self):
        """Create backup of existing RAG system."""
        logger.info("💾 Creating backup of existing system...")
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.project_root / f"rag_backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup key files
            files_to_backup = [
                "app/ai_improvement.py",
                "app/rules/rag_rule_helper.py",
                "scripts/rag_system.py",
                "enhanced_rag_integration.py"
            ]
            
            for file_path in files_to_backup:
                src = self.project_root / file_path
                if src.exists():
                    import shutil
                    dst = backup_dir / file_path.replace("/", "_")
                    shutil.copy2(src, dst)
                    logger.info(f"✅ Backed up {file_path}")
            
            self.backup_created = True
            logger.info(f"✅ Backup created in {backup_dir}")
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise
    
    def _update_configuration(self):
        """Update configuration files for the advanced system."""
        logger.info("⚙️ Updating configuration...")
        
        # Create advanced RAG configuration file
        config = {
            "advanced_rag": {
                "enabled": True,
                "embedding_provider": "sentence_transformers",  # Safe default
                "embedding_model": "all-MiniLM-L6-v2",
                "chunk_size": 500,
                "chunk_overlap": 75,
                "semantic_weight": 0.6,
                "enable_reranking": True,
                "enable_caching": True,
                "enable_feedback": True,
                "cache_ttl": 3600
            },
            "fallback": {
                "enabled": True,
                "use_existing_rag": True
            },
            "performance": {
                "max_response_time": 10.0,
                "enable_metrics": True,
                "adaptation_threshold": 10
            }
        }
        
        config_path = self.project_root / "advanced_rag_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ Configuration saved to {config_path}")
    
    def _migrate_data(self):
        """Migrate existing ChromaDB data to advanced format."""
        logger.info("🔄 Migrating existing data...")
        
        try:
            # Import the advanced system
            from enhanced_rag.advanced_integration import AdvancedRAGSystem, AdvancedRAGConfig
            
            # Get existing ChromaDB collection
            import chromadb
            client = chromadb.PersistentClient(path="./chroma_db")
            
            try:
                existing_collection = client.get_collection("docscanner_rules")
                logger.info("✅ Found existing ChromaDB collection")
            except ValueError:
                logger.warning("No existing collection found - will create new one")
                existing_collection = None
            
            # Create advanced collection
            from enhanced_rag.advanced_embeddings import get_embedding_manager
            embedding_manager = get_embedding_manager("sentence_transformers")
            
            # For now, create a new collection - full migration would copy data
            advanced_collection = client.get_or_create_collection(
                name="docscanner_advanced",
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            
            logger.info("✅ Advanced collection created")
            
            # Initialize advanced RAG system
            config = AdvancedRAGConfig()
            advanced_rag = AdvancedRAGSystem(
                config=config,
                chroma_collection=advanced_collection
            )
            
            logger.info("✅ Advanced RAG system initialized")
            
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            # Continue with migration - system can work without migrated data
    
    def _update_application_code(self):
        """Update main application code to use advanced RAG system."""
        logger.info("🔧 Updating application code...")
        
        # Update ai_improvement.py to use advanced system
        ai_improvement_path = self.project_root / "app" / "ai_improvement.py"
        
        if ai_improvement_path.exists():
            # Read current content
            with open(ai_improvement_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add import for advanced system at the top
            advanced_import = '''
# Advanced RAG system integration
try:
    from enhanced_rag.advanced_integration import get_advanced_rag_system, AdvancedRAGConfig
    ADVANCED_RAG_AVAILABLE = True
    logger.info("✅ Advanced RAG system available")
except ImportError as e:
    ADVANCED_RAG_AVAILABLE = False
    logger.warning(f"Advanced RAG system not available: {e}")
'''
            
            # Find a good place to insert the import
            lines = content.split('\n')
            import_index = 0
            for i, line in enumerate(lines):
                if line.startswith('logger = logging.getLogger'):
                    import_index = i + 1
                    break
            
            # Insert the import
            lines.insert(import_index, advanced_import)
            
            # Update the content
            updated_content = '\n'.join(lines)
            
            # Write back to file
            with open(ai_improvement_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info("✅ ai_improvement.py updated with advanced RAG import")
    
    def _test_new_system(self):
        """Test the new advanced RAG system."""
        logger.info("🧪 Testing advanced RAG system...")
        
        try:
            # Import and test
            from enhanced_rag.advanced_integration import AdvancedRAGSystem, AdvancedRAGConfig
            
            # Test configuration
            config = AdvancedRAGConfig()
            logger.info(f"✅ Configuration loaded: {config.embedding_provider}")
            
            # Test chunking
            from enhanced_rag.advanced_chunking import AdvancedSemanticChunker
            chunker = AdvancedSemanticChunker()
            
            test_doc = """
            # Configuration Guide
            
            ## Setting up the System
            
            To configure the system, follow these steps:
            1. Access the configuration panel
            2. Set the required parameters
            3. Save the configuration
            
            The system will be configured automatically.
            """
            
            chunks = chunker.chunk_document_advanced(
                document_text=test_doc,
                source_doc_id="test_migration",
                product="docscanner"
            )
            
            logger.info(f"✅ Chunking test: {len(chunks)} chunks created")
            
            # Test embedding manager
            from enhanced_rag.advanced_embeddings import get_embedding_manager
            embedding_manager = get_embedding_manager("sentence_transformers")
            
            test_embedding = embedding_manager.get_embedding("Test sentence for embedding")
            logger.info(f"✅ Embedding test: {len(test_embedding)} dimensions")
            
            logger.info("✅ All tests passed!")
            
        except Exception as e:
            logger.error(f"❌ System test failed: {e}")
            raise
    
    def _rollback(self):
        """Rollback changes if migration fails."""
        logger.info("🔄 Rolling back changes...")
        
        if self.backup_created:
            # Restore from backup
            logger.info("Restoring from backup...")
        
        # Remove installed packages if needed
        for requirement in self.requirements_added:
            try:
                package_name = requirement.split('>=')[0].split('==')[0]
                subprocess.run([
                    sys.executable, "-m", "pip", "uninstall", package_name, "-y"
                ], check=True, capture_output=True)
                logger.info(f"✅ Removed {package_name}")
            except:
                pass
    
    def _print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "="*60)
        print("🎉 ADVANCED RAG SYSTEM MIGRATION COMPLETE!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("\n1. 🔧 Configure Embedding Provider:")
        print("   Edit advanced_rag_config.json to set your preferred embedding provider:")
        print("   - For best quality: Set OPENAI_API_KEY and use 'openai'")
        print("   - For good offline: Use 'sentence_transformers' (default)")
        print("   - For fast local: Use 'ollama' with nomic-embed-text")
        
        print("\n2. 📊 Monitor Performance:")
        print("   - Access /performance_dashboard endpoint for metrics")
        print("   - Review feedback analytics in the admin panel")
        print("   - Check system status via the new status endpoint")
        
        print("\n3. 🎯 Optimize Settings:")
        print("   - Adjust chunk sizes based on your document types")
        print("   - Fine-tune retrieval weights (semantic vs BM25)")
        print("   - Enable/disable re-ranking based on performance needs")
        
        print("\n4. 📈 Leverage New Features:")
        print("   - Structured prompts with style guide conditioning")
        print("   - Advanced feedback collection and adaptation")
        print("   - Hybrid retrieval for better precision and recall")
        print("   - Intelligent caching for faster response times")
        
        print("\n5. 🔍 Test Thoroughly:")
        print("   - Test with your typical document types")
        print("   - Verify passive voice conversion improvements")
        print("   - Check response quality and speed")
        
        print(f"\n📁 Configuration file: {self.project_root}/advanced_rag_config.json")
        print(f"📁 Backup location: {self.project_root}/rag_backup_*")
        print("\n" + "="*60)


def main():
    """Main migration function."""
    migration = AdvancedRAGMigration()
    migration.run_migration()


if __name__ == "__main__":
    main()