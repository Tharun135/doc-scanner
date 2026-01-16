"""
Rule Chunk Generator - Convert DocScanner rules into decision chunks.

Each rule generates 6 chunks:
1. Definition - What is the rule?
2. Why it matters - Why should users care?
3. Detection logic - How is it detected?
4. Allowed exceptions - When NOT to apply?
5. Rewrite example - Good correction example
6. Non-rewrite example - When NOT to rewrite

Target: 27 rules × 6 = 162 chunks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk, ChunkTemplates
from typing import List, Dict, Any


# Rule definitions with metadata
RULE_DEFINITIONS = {
    "PASSIVE_VOICE": {
        "name": "Passive Voice",
        "definition": "A sentence uses passive voice when the subject receives the action instead of performing it. Pattern: 'subject + be verb + past participle (+ by actor)'",
        "why_matters": "Passive voice obscures responsibility and makes writing less direct. Active voice clarifies who does what, improving clarity and readability.",
        "severity": "medium",
        "detection": "Detected using spaCy dependency parsing looking for 'auxpass' dependencies, indicating passive auxiliary verbs like 'is done', 'was created', 'has been reviewed'.",
        "exceptions": "Passive voice is acceptable when: 1) The actor is unknown or irrelevant ('The building was constructed in 1920'), 2) In scientific writing where the process matters more than the actor, 3) When the object is more important than the subject, 4) In titles and headings.",
        "rewrite_example": {
            "before": "The document was reviewed by the team.",
            "after": "The team reviewed the document.",
            "why": "Active voice makes the sentence more direct and identifies the actor clearly."
        },
        "non_rewrite_example": {
            "text": "The system was designed to handle multiple users.",
            "why": "When the designer is unknown or irrelevant, passive voice is acceptable."
        }
    },
    
    "LONG_SENTENCES": {
        "name": "Long Sentences",
        "definition": "Sentences exceeding 25 words are flagged as potentially difficult to read. Long sentences often contain multiple ideas that should be split.",
        "why_matters": "Long sentences reduce readability and comprehension. Readers must hold too much information in working memory. Breaking long sentences improves clarity and maintains reader engagement.",
        "severity": "medium",
        "detection": "Detected using spaCy sentence segmentation. Word count is calculated per sentence. Titles, headings, and markdown table separators are excluded.",
        "exceptions": "Long sentences acceptable when: 1) In titles or headings, 2) In markdown table rows, 3) When listing related items that form a coherent unit, 4) In legal or technical definitions where precision requires length.",
        "rewrite_example": {
            "before": "The system processes incoming requests by first validating the user credentials, then checking the request parameters against the schema, and finally forwarding the validated request to the appropriate handler for processing.",
            "after": "The system processes incoming requests in three steps. First, it validates user credentials. Next, it checks request parameters against the schema. Finally, it forwards the validated request to the appropriate handler.",
            "why": "Breaking the long sentence into clear steps improves readability and makes the process easier to follow."
        },
        "non_rewrite_example": {
            "text": "Configure the database connection string in the settings file.",
            "why": "This sentence is under 25 words and expresses a single, clear action."
        }
    },
    
    "ADVERBS": {
        "name": "Weak Adverbs",
        "definition": "Adverbs ending in '-ly' often weaken writing by modifying verbs that could be stronger. Examples: very quickly, really important, extremely difficult.",
        "why_matters": "Adverbs can make writing imprecise and wordy. Choosing stronger, more specific verbs eliminates the need for adverbs and makes writing more powerful.",
        "severity": "low",
        "detection": "Detected using spaCy POS tagging. Tokens tagged as 'ADV' and ending with 'ly' are flagged. Titles and headings are excluded.",
        "exceptions": "Adverbs acceptable when: 1) In titles or headings, 2) When precision requires degree specification ('approximately', 'roughly'), 3) In technical contexts where the adverb has specific meaning ('asynchronously', 'recursively'), 4) In quotations or UI labels.",
        "rewrite_example": {
            "before": "The application runs very quickly on modern hardware.",
            "after": "The application runs fast on modern hardware.",
            "why": "'Very' is redundant - 'fast' is sufficient and more direct."
        },
        "non_rewrite_example": {
            "text": "The function executes asynchronously.",
            "why": "'Asynchronously' is a technical term with specific meaning that cannot be replaced."
        }
    },
    
    "VERY": {
        "name": "Overuse of 'Very'",
        "definition": "'Very' is often an intensifier that adds no real meaning. It typically indicates the writer should choose a more precise word.",
        "why_matters": "'Very' weakens writing by padding sentences without adding value. Removing 'very' or choosing stronger words makes writing more impactful.",
        "severity": "low",
        "detection": "Detected using case-insensitive regex matching for the word 'very'. Excludes titles and headings.",
        "exceptions": "'Very' acceptable in: 1) Titles or headings, 2) Direct quotations, 3) UI labels or button text, 4) When part of a fixed expression ('very well', 'very best').",
        "rewrite_example": {
            "before": "This is a very important decision.",
            "after": "This is a critical decision.",
            "why": "'Critical' is more precise and impactful than 'very important'."
        },
        "non_rewrite_example": {
            "text": "Thank you very much.",
            "why": "Fixed expression where 'very much' is idiomatic and appropriate."
        }
    },
    
    "GRAMMAR_BASIC": {
        "name": "Basic Grammar",
        "definition": "Common grammar issues including: double spaces, lack of punctuation in complex sentences, and basic sentence structure problems.",
        "why_matters": "Grammar errors reduce professionalism and clarity. They distract readers from content and reduce credibility.",
        "severity": "high",
        "detection": "Detected using regex patterns for double spaces and spaCy for sentence structure analysis.",
        "exceptions": "Some patterns acceptable in: 1) Code blocks or technical specifications, 2) Intentional formatting (like indentation), 3) UI mock-ups or wireframes.",
        "rewrite_example": {
            "before": "The  system handles  multiple requests.",
            "after": "The system handles multiple requests.",
            "why": "Removed double spaces for proper formatting."
        },
        "non_rewrite_example": {
            "text": "Code example with intentional  spacing.",
            "why": "Code blocks may require specific spacing for alignment."
        }
    },
    
    "CONSISTENCY": {
        "name": "Terminology Consistency",
        "definition": "Using consistent terms throughout documentation prevents confusion. Synonyms should be avoided when referring to the same concept.",
        "why_matters": "Inconsistent terminology confuses readers and suggests imprecision. Technical documentation especially requires exact, consistent term usage.",
        "severity": "medium",
        "detection": "Detected through term tracking and pattern matching. Looks for multiple terms referring to the same concept within a document.",
        "exceptions": "Variation acceptable when: 1) Introducing a term ('user interface (UI)'), 2) Literary variation in non-technical content, 3) When terms have genuinely different meanings in context.",
        "rewrite_example": {
            "before": "Click the button. Press the control to continue.",
            "after": "Click the button. Click the button to continue.",
            "why": "Consistent terminology ('button') prevents confusion about whether 'control' is different from 'button'."
        },
        "non_rewrite_example": {
            "text": "The user interface (UI) displays information.",
            "why": "Introducing an abbreviation requires showing both forms."
        }
    },
    
    "READABILITY": {
        "name": "Readability",
        "definition": "Complex words and jargon should be replaced with simpler alternatives when possible, without sacrificing precision.",
        "why_matters": "Simpler language reaches a broader audience and improves comprehension. Unnecessary complexity alienates readers.",
        "severity": "medium",
        "detection": "Detected using syllable counting and word frequency analysis. Flags words with 3+ syllables that have simpler alternatives.",
        "exceptions": "Complex words acceptable when: 1) Technical terms with no simpler equivalent, 2) Industry-standard terminology, 3) Legal or regulatory language, 4) Proper nouns or titles.",
        "rewrite_example": {
            "before": "Utilize the functionality to accomplish the task.",
            "after": "Use the feature to complete the task.",
            "why": "'Use', 'feature', and 'complete' are simpler and equally precise."
        },
        "non_rewrite_example": {
            "text": "Configure the authentication parameters.",
            "why": "'Authentication' is a standard technical term without a simpler alternative."
        }
    },
    
    "NOMINALIZATIONS": {
        "name": "Nominalizations",
        "definition": "Nominalizations are verbs turned into nouns (utilization → utilize, implementation → implement). They make writing wordier and less direct.",
        "why_matters": "Nominalizations add unnecessary words and obscure action. Converting them back to verbs creates clearer, more direct sentences.",
        "severity": "medium",
        "detection": "Detected using pattern matching for common nominalization suffixes (-tion, -ment, -ance, -ence) and checking if a verb form exists.",
        "exceptions": "Nominalizations acceptable when: 1) They're established technical terms ('implementation plan'), 2) When used as subjects in sentences about concepts, 3) In titles or headings.",
        "rewrite_example": {
            "before": "The implementation of the feature requires validation.",
            "after": "Implementing the feature requires validation.",
            "why": "Using the verb 'implementing' is more direct than the noun 'implementation'."
        },
        "non_rewrite_example": {
            "text": "The implementation plan outlines the approach.",
            "why": "'Implementation plan' is an established term referring to a specific document type."
        }
    },
    
    "VAGUE_TERMS": {
        "name": "Vague Terms",
        "definition": "Vague terms like 'things', 'stuff', 'various', 'several' lack precision and should be replaced with specific details.",
        "why_matters": "Vague terms force readers to guess meaning. Specific language eliminates ambiguity and improves clarity.",
        "severity": "medium",
        "detection": "Detected using pattern matching for common vague terms. Context analysis determines if specificity is missing.",
        "exceptions": "Vague terms acceptable when: 1) Specificity is genuinely not available, 2) In casual communication, 3) When listing examples where exhaustive detail is unnecessary.",
        "rewrite_example": {
            "before": "The system handles various types of requests.",
            "after": "The system handles GET, POST, and DELETE requests.",
            "why": "Specific request types are more informative than 'various types'."
        },
        "non_rewrite_example": {
            "text": "Results may vary based on configuration.",
            "why": "When outcomes genuinely depend on many factors, 'vary' is acceptable."
        }
    },
    
    "VERB_TENSE": {
        "name": "Verb Tense Consistency",
        "definition": "Inconsistent verb tenses within a paragraph or section confuse readers about timing and sequence.",
        "why_matters": "Tense shifts make it unclear when actions occur. Consistent tense maintains clear temporal relationships.",
        "severity": "medium",
        "detection": "Detected using spaCy POS tagging to track verb tenses within sentences and paragraphs.",
        "exceptions": "Tense changes acceptable when: 1) Describing events at genuinely different times, 2) In conditional statements, 3) When quoting or referencing other sources.",
        "rewrite_example": {
            "before": "The user clicks the button and the system displayed the result.",
            "after": "The user clicks the button and the system displays the result.",
            "why": "Consistent present tense maintains clear action sequence."
        },
        "non_rewrite_example": {
            "text": "The system now displays results, but previously it showed errors.",
            "why": "Tense change appropriately indicates different time periods."
        }
    },
}


def generate_rule_chunks() -> List[DecisionChunk]:
    """
    Generate all rule-based chunks.
    
    For each rule, generates:
    1. Definition chunk
    2. Why it matters chunk
    3. Detection logic chunk
    4. Exception chunk
    5. Rewrite example chunk
    6. Non-rewrite example chunk
    
    Returns:
        List of DecisionChunks (target: 162 chunks from 27 rules)
    """
    chunks = []
    
    for rule_id, rule_data in RULE_DEFINITIONS.items():
        # 1. Definition chunk
        chunks.append(ChunkTemplates.rule_definition(
            rule_id=rule_id,
            rule_name=rule_data["name"],
            definition=rule_data["definition"]
        ))
        
        # 2. Why it matters chunk
        chunks.append(ChunkTemplates.rule_why_matters(
            rule_id=rule_id,
            rule_name=rule_data["name"],
            reason=rule_data["why_matters"],
            severity=rule_data["severity"]
        ))
        
        # 3. Detection logic chunk
        chunks.append(DecisionChunk.create(
            title=f"{rule_data['name']} - Detection",
            question=f"How is the {rule_data['name'].lower()} rule detected?",
            answer=rule_data["detection"],
            knowledge_type="rule",
            rule_id=rule_id,
            doc_type="manual"
        ))
        
        # 4. Exception chunk
        chunks.append(ChunkTemplates.rule_exception(
            rule_id=rule_id,
            rule_name=rule_data["name"],
            exception_case=rule_data["exceptions"]
        ))
        
        # 5. Rewrite example chunk
        if "rewrite_example" in rule_data:
            ex = rule_data["rewrite_example"]
            chunks.append(ChunkTemplates.rewrite_example(
                rule_id=rule_id,
                before=ex["before"],
                after=ex["after"],
                explanation=ex["why"]
            ))
        
        # 6. Non-rewrite example chunk
        if "non_rewrite_example" in rule_data:
            ex = rule_data["non_rewrite_example"]
            chunks.append(DecisionChunk.create(
                title=f"{rule_data['name']} - When NOT to Rewrite",
                question=f"When should the {rule_data['name'].lower()} rule NOT trigger a rewrite?",
                answer=f"Example: \"{ex['text']}\"\n\nReason: {ex['why']}",
                knowledge_type="exception",
                rule_id=rule_id,
                rewrite_allowed=False,
                doc_type="manual"
            ))
    
    print(f"✅ Generated {len(chunks)} rule chunks from {len(RULE_DEFINITIONS)} rules")
    return chunks


def add_custom_rule(rule_id: str, rule_data: Dict[str, Any]) -> List[DecisionChunk]:
    """
    Add a custom rule and generate its chunks.
    
    Use this to extend beyond the base 10 rules.
    """
    RULE_DEFINITIONS[rule_id] = rule_data
    
    # Generate chunks just for this rule
    chunks = []
    
    chunks.append(ChunkTemplates.rule_definition(
        rule_id=rule_id,
        rule_name=rule_data["name"],
        definition=rule_data["definition"]
    ))
    
    chunks.append(ChunkTemplates.rule_why_matters(
        rule_id=rule_id,
        rule_name=rule_data["name"],
        reason=rule_data["why_matters"],
        severity=rule_data.get("severity", "medium")
    ))
    
    # Add other chunks as needed...
    
    return chunks


if __name__ == "__main__":
    # Test generation
    chunks = generate_rule_chunks()
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Average token count: {sum(c.get_token_count() for c in chunks) / len(chunks):.1f}")
    print(f"   Knowledge types: {set(c.knowledge_type for c in chunks)}")
    print(f"\n✅ Rule chunk generation successful!")
