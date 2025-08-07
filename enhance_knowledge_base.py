"""
DATABASE KNOWLEDGE ENHANCEMENT TOOLKIT
This tool helps you improve and expand your local RAG knowledge base for better AI suggestions.
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

def show_current_knowledge_stats():
    """Display current knowledge base statistics."""
    print("📊 CURRENT KNOWLEDGE BASE STATUS")
    print("=" * 50)
    
    # Check ChromaDB size
    chroma_path = "chroma_db/chroma.sqlite3"
    if os.path.exists(chroma_path):
        size_mb = os.path.getsize(chroma_path) / (1024 * 1024)
        print(f"📦 ChromaDB Size: {size_mb:.2f} MB")
    else:
        print("📦 ChromaDB Size: Not initialized")
    
    # Check rules count
    rules_dir = "app/rules"
    if os.path.exists(rules_dir):
        rules_count = len([f for f in os.listdir(rules_dir) if f.endswith('.py') and f != '__init__.py'])
        print(f"📚 Writing Rules: {rules_count} files")
    else:
        print("📚 Writing Rules: Directory not found")
    
    print("\n🎯 IMPROVEMENT OPPORTUNITIES:")
    print("1. Add domain-specific writing guides")
    print("2. Include industry-specific terminology")
    print("3. Add more example transformations")
    print("4. Include style guide templates")
    print("5. Add multilingual writing patterns")

def get_knowledge_enhancement_strategies():
    """Return strategies for enhancing the knowledge base."""
    return {
        "content_types": {
            "Technical Writing": {
                "description": "Software documentation, API guides, technical specs",
                "examples": ["API documentation patterns", "Code comment best practices", "Technical term definitions"],
                "priority": "HIGH"
            },
            "Business Writing": {
                "description": "Reports, proposals, emails, presentations",
                "examples": ["Executive summary templates", "Business terminology", "Professional tone guidelines"],
                "priority": "HIGH"
            },
            "Academic Writing": {
                "description": "Research papers, thesis, scholarly articles",
                "examples": ["Citation formats", "Academic vocabulary", "Research methodology language"],
                "priority": "MEDIUM"
            },
            "Creative Writing": {
                "description": "Stories, blogs, marketing copy",
                "examples": ["Narrative structures", "Persuasive language", "Brand voice guidelines"],
                "priority": "MEDIUM"
            },
            "Legal Writing": {
                "description": "Contracts, legal documents, compliance",
                "examples": ["Legal terminology", "Contract language patterns", "Compliance standards"],
                "priority": "LOW"
            }
        },
        "improvement_methods": [
            "Import existing style guides",
            "Add company-specific terminology",
            "Include industry best practices",
            "Add multilingual patterns",
            "Import writing samples for analysis"
        ]
    }

def create_custom_knowledge_template():
    """Create templates for adding custom knowledge."""
    templates = {
        "style_guide": """
# Custom Style Guide Template

## Voice and Tone
- Preferred tone: [Professional/Casual/Technical]
- Target audience: [Developers/Business users/General public]
- Key principles: [Clarity/Brevity/Accuracy]

## Terminology Standards
- Use "click" instead of "select"
- Use "sign in" instead of "log in" 
- Use "app" instead of "application"

## Grammar Preferences
- Use Oxford comma: Yes/No
- Use contractions: Yes/No
- Preferred tense: Present/Past/Future

## Formatting Standards
- Headings: Title Case/Sentence case
- Lists: Parallel structure required
- Numbers: Spell out under 10/Always use numerals
        """,
        
        "technical_terms": """
# Technical Terminology Guide

## Software Development Terms
- "Repository" not "repo" in formal docs
- "Function" not "method" for standalone functions
- "Parameter" not "argument" in documentation

## User Interface Terms
- "Button" for clickable elements
- "Field" for input areas
- "Menu" for navigation lists

## Action Words
- "Configure" not "setup" (verb vs noun)
- "Log in" (verb) vs "login" (noun)
- "Set up" (verb) vs "setup" (noun)
        """,
        
        "industry_specific": """
# Industry-Specific Writing Guide

## [Your Industry] Standards
- Key concepts: [List important concepts]
- Preferred terminology: [Industry-specific terms]
- Compliance requirements: [Regulatory language needs]

## Common Patterns
- How to describe processes
- How to explain technical concepts
- How to structure documents
        """
    }
    
    return templates

def demonstrate_knowledge_addition():
    """Show how to add knowledge to the database."""
    print("\n🔧 HOW TO ENHANCE YOUR KNOWLEDGE BASE")
    print("=" * 50)
    
    print("\n📝 METHOD 1: Add Custom Documents")
    print("   ├── Create text files with writing guidelines")
    print("   ├── Include examples and patterns")
    print("   └── Import using add_document_to_knowledge()")
    
    print("\n📚 METHOD 2: Import Existing Style Guides")
    print("   ├── Company style guides")
    print("   ├── Industry standards documents")
    print("   └── Writing best practices compilations")
    
    print("\n🎯 METHOD 3: Add Domain-Specific Rules")
    print("   ├── Technical writing patterns")
    print("   ├── Business communication standards")
    print("   └── Academic writing conventions")
    
    print("\n🤖 METHOD 4: Learning from Usage")
    print("   ├── Analyze user feedback patterns")
    print("   ├── Track common correction types")
    print("   └── Auto-generate improvement rules")

def show_enhancement_code_examples():
    """Show practical code examples for enhancing the database."""
    print("\n💻 CODE EXAMPLES FOR KNOWLEDGE ENHANCEMENT")
    print("=" * 50)
    
    examples = {
        "Add Style Guide": '''
from app.llamaindex_ai import llamaindex_ai_engine

# Add your company's style guide
style_guide = """
Company Writing Style Guide:

1. Use active voice in all documentation
2. Write in second person (you, your)
3. Use parallel structure in lists
4. Avoid jargon and acronyms
5. Keep sentences under 20 words

Examples:
- Good: "Click Save to store your changes"
- Bad: "Changes can be stored by clicking Save"
"""

llamaindex_ai_engine.add_document_to_knowledge(
    content=style_guide,
    metadata={"type": "style_guide", "source": "company"}
)
        ''',
        
        "Add Technical Terms": '''
# Add technical terminology database
tech_terms = """
Technical Writing Standards:

API Documentation:
- Use "endpoint" not "API call"
- Use "request" and "response" 
- Include example code snippets

Error Messages:
- Be specific about the problem
- Suggest concrete solutions
- Use friendly, helpful tone

Code Documentation:
- Explain the "why" not just "what"
- Include usage examples
- Document edge cases
"""

llamaindex_ai_engine.add_document_to_knowledge(
    content=tech_terms,
    metadata={"type": "technical_guide", "domain": "software"}
)
        ''',
        
        "Import from File": '''
# Import existing documents
def import_knowledge_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    llamaindex_ai_engine.add_document_to_knowledge(
        content=content,
        metadata={
            "type": "imported_document",
            "source": file_path,
            "imported_date": datetime.now().isoformat()
        }
    )
    print(f"✅ Imported knowledge from {file_path}")

# Usage
import_knowledge_from_file("company_style_guide.txt")
        '''
    }
    
    for title, code in examples.items():
        print(f"\n🔹 {title}:")
        print(code)

def create_knowledge_enhancement_script():
    """Create a practical script for users to enhance their knowledge base."""
    script_content = '''
"""
KNOWLEDGE BASE ENHANCEMENT SCRIPT
Run this to add custom knowledge to your Doc Scanner's RAG database.
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

def enhance_knowledge_base():
    """Main function to enhance the knowledge base."""
    print("🚀 ENHANCING YOUR DOC SCANNER KNOWLEDGE BASE")
    print("=" * 50)
    
    try:
        add_business_writing_knowledge()
        add_technical_documentation_patterns()
        add_grammar_and_style_enhancements()
        
        print("\\n🎉 KNOWLEDGE BASE ENHANCEMENT COMPLETE!")
        print("\\nYour Doc Scanner now has enhanced knowledge for:")
        print("✅ Business writing excellence")
        print("✅ Technical documentation standards")
        print("✅ Advanced grammar and style rules")
        print("\\n🎯 Result: Better, more specific AI suggestions!")
        
    except Exception as e:
        print(f"❌ Error enhancing knowledge base: {e}")
        print("Make sure your Doc Scanner app is properly initialized.")

if __name__ == "__main__":
    enhance_knowledge_base()
'''
    
    return script_content

def main():
    """Main demonstration function."""
    show_current_knowledge_stats()
    
    strategies = get_knowledge_enhancement_strategies()
    
    print("\n🎯 KNOWLEDGE ENHANCEMENT STRATEGIES")
    print("=" * 50)
    
    for content_type, details in strategies["content_types"].items():
        print(f"\n📋 {content_type} ({details['priority']} Priority)")
        print(f"   Description: {details['description']}")
        print("   Examples:")
        for example in details['examples']:
            print(f"   • {example}")
    
    demonstrate_knowledge_addition()
    show_enhancement_code_examples()
    
    print("\n🔧 NEXT STEPS TO IMPROVE YOUR DATABASE:")
    print("=" * 50)
    print("1. Run the knowledge enhancement script")
    print("2. Add your company's style guide")
    print("3. Import domain-specific terminology")
    print("4. Add industry best practices")
    print("5. Include example transformations")

if __name__ == "__main__":
    main()
