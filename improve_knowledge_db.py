"""
PRACTICAL KNOWLEDGE BASE ENHANCER
Run this script to immediately improve your Doc Scanner's AI suggestions.
"""

from app.llamaindex_ai import llamaindex_ai_engine
from datetime import datetime
import os

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

def enhance_knowledge_base():
    """Main function to enhance the knowledge base."""
    print("🚀 ENHANCING YOUR DOC SCANNER KNOWLEDGE BASE")
    print("=" * 50)
    
    try:
        add_business_writing_knowledge()
        add_technical_documentation_patterns()
        add_grammar_and_style_enhancements()
        add_software_writing_patterns()
        
        print("\n🎉 KNOWLEDGE BASE ENHANCEMENT COMPLETE!")
        print("\nYour Doc Scanner now has enhanced knowledge for:")
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
