"""
PRACTICAL KNOWLEDGE BASE ENHANCER
Run this script to immediately improve your Doc Scanner's AI suggestions.
Automatically imports style guides from the style_guides/ directory.
"""

from app.llamaindex_ai import llamaindex_ai_engine
from datetime import datetime
import os
import glob

def add_business_writing_knowledge():
    """Add business writing best practices."""
    business_guide = """
    Business Writing Excellence Guide:
    
    Email Communication:
    - Use clear, specific subject lines
    - Lead with the main point
    - Use bullet points for multiple items
    - End with clear next steps
    
    Report Writing:
    - Start with executive summary
    - Use data to support claims
    - Include actionable recommendations
    - Structure with clear headings
    
    Presentation Content:
    - One main idea per slide
    - Use parallel structure in bullet points
    - Quantify benefits and results
    - End with clear call-to-action
    
    Common Business Phrases to Avoid:
    - "Circle back" → "Follow up"
    - "Touch base" → "Contact" or "Meet"
    - "Low-hanging fruit" → "Easy wins"
    - "Think outside the box" → "Be creative"
    """
    
    llamaindex_ai_engine.add_document_to_knowledge(
        content=business_guide,
        metadata={"type": "business_writing", "category": "professional"}
    )
    print("✅ Added business writing knowledge")

def add_technical_documentation_patterns():
    """Add technical documentation best practices."""
    tech_guide = """
    Technical Documentation Standards:
    
    API Documentation:
    - Include authentication details
    - Provide working code examples
    - Document all parameters
    - Show example responses
    - Include error codes and meanings
    
    User Guides:
    - Start with prerequisites
    - Use numbered steps for procedures
    - Include screenshots for UI elements
    - Provide troubleshooting section
    - End with related resources
    
    Code Comments:
    - Explain complex business logic
    - Document assumptions and limitations
    - Include examples for functions
    - Keep comments up-to-date
    - Use consistent formatting
    
    Architecture Documentation:
    - Include system diagrams
    - Explain design decisions
    - Document dependencies
    - Include deployment instructions
    - Maintain change logs
    """
    
    llamaindex_ai_engine.add_document_to_knowledge(
        content=tech_guide,
        metadata={"type": "technical_writing", "category": "development"}
    )
    print("✅ Added technical documentation knowledge")

def add_grammar_and_style_enhancements():
    """Add advanced grammar and style rules."""
    grammar_guide = """
    Advanced Grammar and Style Guide:
    
    Parallel Structure:
    - Wrong: "The app is fast, reliable, and has good security"
    - Right: "The app is fast, reliable, and secure"
    
    Conciseness Patterns:
    - "In order to" → "To"
    - "Due to the fact that" → "Because"
    - "At this point in time" → "Now"
    - "For the purpose of" → "For" or "To"
    
    Active Voice Conversions:
    - "The code was reviewed by the team" → "The team reviewed the code"
    - "Errors will be caught by the system" → "The system will catch errors"
    - "The feature was implemented by Sarah" → "Sarah implemented the feature"
    
    Clarity Improvements:
    - Replace vague pronouns with specific nouns
    - Use specific verbs instead of generic ones
    - Break up compound sentences
    - Place important information first
    """
    
    llamaindex_ai_engine.add_document_to_knowledge(
        content=grammar_guide,
        metadata={"type": "grammar_guide", "category": "style"}
    )
    print("✅ Added advanced grammar knowledge")

def add_software_writing_patterns():
    """Add software-specific writing patterns."""
    software_guide = """
    Software Writing Best Practices:
    
    User Interface Text:
    - Use action verbs for buttons: "Save", "Delete", "Create"
    - Write error messages that suggest solutions
    - Use consistent terminology throughout the app
    - Keep labels short but descriptive
    
    Documentation Patterns:
    - Start procedures with prerequisites
    - Use parallel structure in step lists
    - Include expected outcomes for each step
    - Provide alternative paths for different scenarios
    
    Code Documentation:
    - Document the "why" not just the "what"
    - Include examples for complex functions
    - Explain parameters and return values
    - Mention any side effects or dependencies
    
    Release Notes:
    - Group changes by type (Features, Fixes, Breaking Changes)
    - Use past tense for completed work
    - Include impact assessment for users
    - Provide migration guides for breaking changes
    """
    
    llamaindex_ai_engine.add_document_to_knowledge(
        content=software_guide,
        metadata={"type": "software_writing", "category": "technology"}
    )
    print("✅ Added software writing patterns")

def import_style_guides():
    """Import all style guides from the style_guides/ directory."""
    style_guides_path = "style_guides"
    
    if not os.path.exists(style_guides_path):
        print(f"⚠️  Style guides directory not found: {style_guides_path}")
        return
    
    # Map each file to a document type and description
    files_to_import = [
        {
            "path": "app-template.md",
            "type": "template",
            "category": "app_documentation",
            "description": "Standard template structure for Industrial Edge apps"
        },
        {
            "path": "company_style_guide.md",
            "type": "company_style",
            "category": "style_guide",
            "description": "Official company writing style guide"
        },
        {
            "path": "connector-template.md",
            "type": "template",
            "category": "connector_docs",
            "description": "Template structure for connector documentation"
        },
        {
            "path": "quick-start-for-devs.md",
            "type": "onboarding_guide",
            "category": "developer_docs",
            "description": "Quick start guide for writing developer documentation"
        },
        {
            "path": "README.md",
            "type": "readme",
            "category": "meta_docs",
            "description": "Readme for the style guide directory"
        },
        {
            "path": "RulesForContributors.md",
            "type": "contributor_rules",
            "category": "style_guide",
            "description": "Style and tone guide for all contributors"
        },
        {
            "path": "structured-writing.md",
            "type": "template",
            "category": "structured_docs",
            "description": "Standardized structure for writing documentation"
        }
    ]
    
    imported_count = 0
    
    # Import loop
    for file_info in files_to_import:
        file_path = os.path.join(style_guides_path, file_info['path'])
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_info['path']}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            llamaindex_ai_engine.add_document_to_knowledge(
                content=content,
                metadata={
                    "type": file_info["type"],
                    "category": file_info["category"],
                    "description": file_info["description"],
                    "filename": file_info["path"],
                    "source": file_info["path"],
                    "imported_date": datetime.now().isoformat()
                }
            )
            print(f"✅ Imported: {file_info['path']} ({file_info['description']})")
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Failed to import {file_info['path']}: {e}")
    
    if imported_count > 0:
        print(f"\n🎉 Successfully imported {imported_count} style guide(s)")
    else:
        print("\n📝 No style guides found to import")

def enhance_knowledge_base():
    """Main function to enhance the knowledge base."""
    print("🚀 ENHANCING YOUR DOC SCANNER KNOWLEDGE BASE")
    print("=" * 50)
    
    try:
        # Import style guides first
        print("\n📁 Importing Style Guides...")
        import_style_guides()
        
        # Add built-in knowledge
        print("\n📚 Adding Built-in Knowledge...")
        add_business_writing_knowledge()
        add_technical_documentation_patterns()
        add_grammar_and_style_enhancements()
        add_software_writing_patterns()
        
        print("\n🎉 KNOWLEDGE BASE ENHANCEMENT COMPLETE!")
        print("\nYour Doc Scanner now has enhanced knowledge for:")
        print("✅ Style guides imported")
        print("✅ Business writing excellence")
        print("✅ Technical documentation standards")
        print("✅ Advanced grammar and style rules")
        print("✅ Software-specific writing patterns")
        print("\n🎯 Result: Better, more specific AI suggestions!")
        
        # Show database status
        try:
            status = llamaindex_ai_engine.get_system_status()
            print(f"\n📊 System Status: {status.get('system_type', 'Local AI')}")
            print(f"💾 Model: {status.get('model', 'Unknown')}")
            print(f"💰 Cost: {status.get('cost', 'Free')}")
        except:
            print("\n📊 Knowledge base enhanced successfully!")
        
    except Exception as e:
        print(f"❌ Error enhancing knowledge base: {e}")
        print("Make sure your Doc Scanner app is properly initialized.")

if __name__ == "__main__":
    enhance_knowledge_base()

# Optional future use: Weekly updater
def weekly_knowledge_update():
    from datetime import datetime
    trends = f"""
    Writing Trends - {datetime.now().strftime('%Y-%m-%d')}:
    - Inclusive language
    - AI-first documentation strategies
    - Conversational tone for user interfaces
    - Micro-content best practices
    """
    llamaindex_ai_engine.add_document_to_knowledge(
        content=trends,
        metadata={"type": "trends_update", "source": "auto_script"}
    )
    print("📈 Added writing trends update")

# Quick test - Validate new suggestions
def test_enhanced_suggestions():
    """Test that the enhanced knowledge base is working."""
    try:
        from app.ai_improvement import ai_engine
        
        test_sentence = "The feature was implemented by the developer."
        result = ai_engine.generate_contextual_suggestion(
            feedback_text="Rewrite in active voice",
            sentence_context=test_sentence
        )
        
        print("\n🧪 Test Suggestion Result:")
        print(f"💬 Original: {test_sentence}")
        print(f"💡 Suggestion: {result.get('suggestion')}")
        
        # Additional test for business writing
        business_test = "We need to circle back on this low-hanging fruit."
        business_result = ai_engine.generate_contextual_suggestion(
            feedback_text="Improve business writing",
            sentence_context=business_test
        )
        
        print(f"\n💼 Business Writing Test:")
        print(f"💬 Original: {business_test}")
        print(f"💡 Suggestion: {business_result.get('suggestion')}")
        
    except Exception as e:
        print(f"⚠️  Test failed: {e}")
        print("   This is normal if the app isn't running or knowledge base isn't ready.")
