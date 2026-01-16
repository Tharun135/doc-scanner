"""
Pattern Chunk Generator - Structural writing patterns.

Creates chunks for document structure patterns:
- Procedures (how to write step-by-step instructions)
- Lists (when to use bullets vs numbers)
- Tables (how to structure tabular data)
- Headings (hierarchy and formatting)
- Notes/warnings (when to use admonitions)

Target: 50-100 chunks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk
from typing import List


# Structural writing patterns
STRUCTURAL_PATTERNS = [
    # Procedures
    {
        "pattern_name": "Procedure Structure",
        "category": "procedures",
        "chunks": [
            {
                "question": "How should a procedure be structured?",
                "answer": "A procedure should have: 1) Clear title stating the goal, 2) Prerequisites or preconditions, 3) Numbered steps in sequential order, 4) Expected result or outcome."
            },
            {
                "question": "When should procedure steps be numbered?",
                "answer": "Use numbered steps when order matters. Steps must be performed in sequence. If steps can be done in any order, use bullets instead."
            },
            {
                "question": "How long should a procedure step be?",
                "answer": "Each step should be one action. If a step requires multiple actions, break it into substeps. Maximum one sentence per step."
            },
            {
                "question": "Should procedures include explanations?",
                "answer": "Procedures should focus on actions. Keep explanations brief. If extensive explanation needed, add a separate 'About' section before the procedure."
            },
            {
                "question": "How should procedure preconditions be presented?",
                "answer": "List preconditions before step 1 using a 'Before you begin' or 'Prerequisites' section. Use bullets for multiple preconditions."
            }
        ]
    },
    
    # Lists
    {
        "pattern_name": "List Formatting",
        "category": "lists",
        "chunks": [
            {
                "question": "When should I use bulleted lists?",
                "answer": "Use bullets for items without sequence or priority. All items are equal in importance and can be read in any order."
            },
            {
                "question": "When should I use numbered lists?",
                "answer": "Use numbers for: 1) Sequential steps, 2) Ranked items (first, second, third), 3) Items that will be referenced by number."
            },
            {
                "question": "How should list items be capitalized?",
                "answer": "If list items are complete sentences, capitalize first word and use end punctuation. If fragments, use lowercase (unless proper noun) and no punctuation."
            },
            {
                "question": "Should list items be parallel in structure?",
                "answer": "Yes. All items in a list must use parallel grammatical structure. If first item starts with a verb, all items must start with verbs."
            },
            {
                "question": "How many items should a list have?",
                "answer": "Minimum 2 items for a list. If more than 7-9 items, consider grouping into categories or splitting into multiple lists."
            }
        ]
    },
    
    # Tables
    {
        "pattern_name": "Table Structure",
        "category": "tables",
        "chunks": [
            {
                "question": "When should information be presented in a table?",
                "answer": "Use tables for: 1) Comparing multiple items across same attributes, 2) Reference data, 3) Specifications, 4) Configurations. Avoid tables for simple lists."
            },
            {
                "question": "How should table headers be formatted?",
                "answer": "Table headers should be concise (1-3 words), use title case, and clearly identify column content. First column typically identifies rows."
            },
            {
                "question": "Should tables have descriptions?",
                "answer": "Yes. Introduce every table with a sentence explaining its purpose. Use 'The following table...' or 'Table X shows...'."
            },
            {
                "question": "How should table cells be formatted?",
                "answer": "Keep cell content concise. Use sentence fragments, not full sentences. Align text left, numbers right. Use consistent formatting within columns."
            },
            {
                "question": "When should a table be split?",
                "answer": "Split tables that: 1) Don't fit on one page/screen, 2) Have more than 7-8 columns, 3) Mix different types of information."
            }
        ]
    },
    
    # Headings
    {
        "pattern_name": "Heading Hierarchy",
        "category": "headings",
        "chunks": [
            {
                "question": "How should heading levels be used?",
                "answer": "Use heading hierarchy to show document structure. H1 for main title, H2 for major sections, H3 for subsections. Never skip levels (H1 to H3)."
            },
            {
                "question": "How should headings be capitalized?",
                "answer": "Use sentence case (capitalize first word only) or title case (capitalize major words). Be consistent throughout the document. Sentence case is more modern and readable."
            },
            {
                "question": "Should headings be numbered?",
                "answer": "Number headings when: 1) Document will be referenced by section number, 2) Formal technical or legal document, 3) Multi-level TOC needed. Otherwise, use unnumbered."
            },
            {
                "question": "How long should a heading be?",
                "answer": "Headings should be concise: 2-8 words. Use nouns and verbs, avoid articles (a, an, the). Heading should clearly identify section content."
            },
            {
                "question": "Should headings be complete sentences?",
                "answer": "No. Headings should be phrases, not sentences. No end punctuation (unless question). Exception: FAQ sections can use questions as headings."
            }
        ]
    },
    
    # Notes and Admonitions
    {
        "pattern_name": "Notes and Warnings",
        "category": "admonitions",
        "chunks": [
            {
                "question": "When should I use a Note?",
                "answer": "Use NOTE for helpful supplementary information that enhances understanding but isn't critical. Reader can skip without losing comprehension."
            },
            {
                "question": "When should I use a Warning?",
                "answer": "Use WARNING for actions that could cause data loss, system damage, or safety issues. Warnings are critical and must not be ignored."
            },
            {
                "question": "When should I use a Caution?",
                "answer": "Use CAUTION for actions that could cause unexpected results or minor problems. Less severe than warning but more important than note."
            },
            {
                "question": "When should I use a Tip?",
                "answer": "Use TIP for best practices, shortcuts, or expert advice that improves efficiency or quality. Tips add value but aren't required knowledge."
            },
            {
                "question": "How should admonitions be formatted?",
                "answer": "Place admonitions before the step or paragraph they relate to. Keep text concise (1-3 sentences). Use specific, actionable language."
            }
        ]
    },
    
    # Code Examples
    {
        "pattern_name": "Code Examples",
        "category": "code",
        "chunks": [
            {
                "question": "How should code examples be introduced?",
                "answer": "Introduce code with a sentence explaining what it does and when to use it. Example: 'The following code authenticates the user:'"
            },
            {
                "question": "Should code examples be complete or excerpts?",
                "answer": "Provide complete, runnable examples when possible. If showing excerpt, indicate with comments where omitted code goes: '// ... rest of function'"
            },
            {
                "question": "Should code examples include comments?",
                "answer": "Yes. Comment non-obvious code. Explain why, not what (code shows what). Focus comments on business logic and key decisions."
            },
            {
                "question": "How should code examples be tested?",
                "answer": "All code examples must be tested and verified to work. Broken examples destroy user trust and waste debugging time."
            },
            {
                "question": "Should inline code use different formatting than code blocks?",
                "answer": "Yes. Use inline code for: single keywords, short expressions, function names. Use code blocks for: multiple lines, complete functions, runnable examples."
            }
        ]
    },
    
    # Cross-references
    {
        "pattern_name": "Cross-references",
        "category": "links",
        "chunks": [
            {
                "question": "How should I write cross-references?",
                "answer": "Use descriptive link text that works out of context. Avoid 'click here' or 'this link'. Example: 'See the Installation Guide' not 'See this page'."
            },
            {
                "question": "When should I link to other sections?",
                "answer": "Link when: 1) Referenced topic explained elsewhere, 2) User needs prerequisite knowledge, 3) Avoiding duplication. Don't link for common knowledge."
            },
            {
                "question": "Should external links be marked differently?",
                "answer": "Yes. Indicate external links (to other sites) with icon or text. Users need to know when they're leaving your documentation."
            },
            {
                "question": "How should I reference figures and tables?",
                "answer": "Reference by number and type: 'Figure 1 shows...', 'See Table 2'. Place reference before the figure/table, never after."
            }
        ]
    },
    
    # Error Messages
    {
        "pattern_name": "Error Message Documentation",
        "category": "errors",
        "chunks": [
            {
                "question": "How should error messages be documented?",
                "answer": "Document errors with: 1) Exact error text (in code format), 2) What causes the error, 3) How to fix it, 4) How to prevent it."
            },
            {
                "question": "Should error documentation include error codes?",
                "answer": "Yes. Include exact error code if system generates one. Users search for error codes when troubleshooting."
            },
            {
                "question": "How should troubleshooting steps be presented?",
                "answer": "Present troubleshooting as: 1) Check this first (most common cause), 2) Check this next, 3) Last resort steps. Order by likelihood."
            }
        ]
    },
]


def generate_pattern_chunks() -> List[DecisionChunk]:
    """
    Generate structural pattern chunks.
    
    These chunks teach the AI about document structure and formatting patterns.
    
    Returns:
        List of DecisionChunks (target: 50-100 chunks)
    """
    chunks = []
    
    for pattern_group in STRUCTURAL_PATTERNS:
        pattern_name = pattern_group["pattern_name"]
        category = pattern_group["category"]
        
        for i, chunk_data in enumerate(pattern_group["chunks"]):
            chunks.append(DecisionChunk.create(
                title=f"{pattern_name} - Rule {i+1}",
                question=chunk_data["question"],
                answer=chunk_data["answer"],
                knowledge_type="pattern",
                doc_type="pattern",
                severity="medium",
                metadata={
                    "pattern_name": pattern_name,
                    "category": category,
                    "pattern_index": i
                }
            ))
    
    print(f"✅ Generated {len(chunks)} pattern chunks from {len(STRUCTURAL_PATTERNS)} pattern categories")
    return chunks


def add_custom_pattern(pattern_name: str, category: str, 
                       question: str, answer: str) -> DecisionChunk:
    """
    Add a custom structural pattern chunk.
    
    Use this to add company-specific or project-specific patterns.
    """
    return DecisionChunk.create(
        title=f"{pattern_name} - Custom Rule",
        question=question,
        answer=answer,
        knowledge_type="pattern",
        doc_type="pattern",
        severity="medium",
        metadata={
            "pattern_name": pattern_name,
            "category": category,
            "custom": True
        }
    )


if __name__ == "__main__":
    # Test generation
    chunks = generate_pattern_chunks()
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Average token count: {sum(c.get_token_count() for c in chunks) / len(chunks):.1f}")
    print(f"   Categories:")
    for pattern in STRUCTURAL_PATTERNS:
        category = pattern["category"]
        count = sum(1 for c in chunks if c.metadata.get("category") == category)
        print(f"      {category}: {count}")
    print(f"\n✅ Pattern chunk generation successful!")
