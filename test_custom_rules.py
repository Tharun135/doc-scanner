"""
Custom Rule Management Utility
Add domain-specific rules to the RAG knowledge base.
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demonstrate_custom_rule_addition():
    """Demonstrate adding custom domain-specific rules."""
    
    print("🔧 Custom Rule Addition Demonstration\n")
    
    # Import the RAG system
    try:
        from app.rules.rag_main import add_writing_rule, get_rag_suggestion
        print("✅ RAG system imported successfully")
    except Exception as e:
        print(f"❌ Error importing RAG system: {e}")
        return
    
    # Example custom rules for different domains
    custom_rules = [
        {
            # Software Documentation Rule
            "issue_pattern": "missing code example",
            "rule_title": "Include Code Examples",
            "issue_description": "Technical instructions should include practical code examples",
            "solution": "Add clear, executable code examples that demonstrate the concept",
            "examples": [
                {
                    "wrong": "Use the authenticate function to log in users.",
                    "right": "Use the authenticate function to log in users:\n\n```python\nuser = authenticate(username, password)\nif user:\n    print('Login successful')\n```",
                    "explanation": "Code examples make instructions clearer and actionable"
                }
            ],
            "category": "clarity",
            "severity": "medium",
            "keywords": ["code example", "technical documentation", "programming", "implementation"]
        },
        {
            # Academic Writing Rule
            "issue_pattern": "first person in academic writing",
            "rule_title": "Avoid First Person in Academic Writing",
            "issue_description": "Academic writing should maintain objectivity by avoiding first person",
            "solution": "Use third person or passive voice in formal academic contexts",
            "examples": [
                {
                    "wrong": "I believe this study shows significant results.",
                    "right": "This study demonstrates significant results.",
                    "explanation": "Remove personal opinion language to maintain academic objectivity"
                },
                {
                    "wrong": "We conducted experiments to test our hypothesis.",
                    "right": "Experiments were conducted to test the hypothesis.",
                    "explanation": "Use passive voice to focus on the research rather than researchers"
                }
            ],
            "category": "tone",
            "severity": "medium",
            "keywords": ["academic writing", "first person", "objectivity", "formal tone"]
        },
        {
            # API Documentation Rule
            "issue_pattern": "missing error handling information",
            "rule_title": "Document Error Responses",
            "issue_description": "API documentation should include error response formats",
            "solution": "Document all possible error responses with status codes and formats",
            "examples": [
                {
                    "wrong": "POST /api/users - Creates a new user",
                    "right": "POST /api/users - Creates a new user\n\nSuccess: 201 Created\nError: 400 Bad Request {\"error\": \"Invalid email format\"}",
                    "explanation": "Include both success and error response formats"
                }
            ],
            "category": "formatting",
            "severity": "high",
            "keywords": ["API documentation", "error handling", "status codes", "response format"]
        },
        {
            # Legal Document Rule
            "issue_pattern": "ambiguous legal language",
            "rule_title": "Precise Legal Language",
            "issue_description": "Legal documents require precise, unambiguous language",
            "solution": "Use specific terms and avoid words that could be interpreted multiple ways",
            "examples": [
                {
                    "wrong": "The party may terminate this agreement at any time.",
                    "right": "Either party may terminate this agreement with 30 days written notice.",
                    "explanation": "Specify which party and the exact termination process"
                }
            ],
            "category": "clarity",
            "severity": "high",
            "keywords": ["legal language", "precision", "ambiguity", "contracts"]
        }
    ]
    
    print("📝 Adding Custom Domain-Specific Rules:\n")
    
    # Add each custom rule
    for i, rule in enumerate(custom_rules, 1):
        print(f"Rule {i}: {rule['rule_title']}")
        print(f"Domain: {rule['category'].title()}")
        print(f"Description: {rule['issue_description']}")
        
        # Add the rule
        success = add_writing_rule(rule)
        if success:
            print("✅ Rule added successfully")
        else:
            print("❌ Failed to add rule")
        
        print()
    
    # Test the custom rules
    print("🧪 Testing Custom Rules:\n")
    
    test_cases = [
        {
            "issue": "missing code example",
            "sentence": "Use the authenticate function to log in users.",
            "category": "clarity"
        },
        {
            "issue": "first person in academic writing",
            "sentence": "I believe this study shows significant results.",
            "category": "tone"
        },
        {
            "issue": "missing error handling information",
            "sentence": "POST /api/users - Creates a new user",
            "category": "formatting"
        },
        {
            "issue": "ambiguous legal language",
            "sentence": "The party may terminate this agreement at any time.",
            "category": "clarity"
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['issue']}")
        print(f"Sentence: \"{test_case['sentence']}\"")
        
        suggestion = get_rag_suggestion(
            issue_text=test_case['issue'],
            sentence_context=test_case['sentence'],
            category=test_case['category']
        )
        
        print(f"💡 Suggestion: {suggestion.get('suggestion', 'No suggestion')[:150]}...")
        print(f"🔍 Source: {suggestion.get('source', 'Unknown')}")
        print(f"📊 Confidence: {suggestion.get('confidence', 0.0)}")
        print()
    
    print("🎯 Custom Rule Demonstration Complete!")

def interactive_rule_builder():
    """Interactive utility to build custom rules."""
    
    print("🔧 Interactive Custom Rule Builder\n")
    print("Create your own writing rules for specific domains or needs.\n")
    
    try:
        from app.rules.rag_main import add_writing_rule
    except Exception as e:
        print(f"❌ Error importing RAG system: {e}")
        return
    
    # Get rule information from user
    print("Enter the details for your custom rule:")
    
    rule_title = input("Rule Title: ") or "Custom Rule"
    issue_pattern = input("Issue Pattern (what to detect): ") or "custom issue"
    issue_description = input("Issue Description: ") or "Custom writing issue"
    solution = input("Solution: ") or "Apply custom solution"
    category = input("Category (grammar/clarity/tone/formatting/punctuation/accessibility/terminology/capitalization): ") or "clarity"
    severity = input("Severity (high/medium/low): ") or "medium"
    
    print("\nAdd an example (optional):")
    wrong_example = input("Wrong example: ")
    right_example = input("Correct example: ")
    explanation = input("Explanation: ")
    
    keywords_input = input("Keywords (comma-separated): ")
    keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else [issue_pattern]
    
    # Build the rule
    custom_rule = {
        "issue_pattern": issue_pattern,
        "rule_title": rule_title,
        "issue_description": issue_description,
        "solution": solution,
        "category": category,
        "severity": severity,
        "keywords": keywords
    }
    
    if wrong_example and right_example:
        custom_rule["examples"] = [{
            "wrong": wrong_example,
            "right": right_example,
            "explanation": explanation or "Custom example"
        }]
    else:
        custom_rule["examples"] = []
    
    print(f"\n📋 Custom Rule Created:")
    print(f"Title: {rule_title}")
    print(f"Pattern: {issue_pattern}")
    print(f"Category: {category}")
    print(f"Severity: {severity}")
    
    # Add the rule
    success = add_writing_rule(custom_rule)
    if success:
        print("✅ Custom rule added successfully to the knowledge base!")
        
        # Test the rule
        test_sentence = input("\nEnter a test sentence to try your new rule: ")
        if test_sentence:
            from app.rules.rag_main import get_rag_suggestion
            suggestion = get_rag_suggestion(issue_pattern, test_sentence, category)
            print(f"\n💡 Test Result: {suggestion.get('suggestion', 'No suggestion')[:200]}...")
    else:
        print("❌ Failed to add custom rule")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Demonstrate pre-built custom rules")
    print("2. Interactive rule builder")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        demonstrate_custom_rule_addition()
    elif choice == "2":
        interactive_rule_builder()
    else:
        print("Running demonstration...")
        demonstrate_custom_rule_addition()
