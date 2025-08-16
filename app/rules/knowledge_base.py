"""
Writing Rules Knowledge Base
Comprehensive rule definitions with solutions for RAG retrieval.
"""

WRITING_RULES_KNOWLEDGE_BASE = {
    "grammar_rules": [
        {
            "issue_pattern": "passive voice detected",
            "rule_title": "Active Voice Preference",
            "issue_description": "Passive voice makes writing less direct and harder to follow",
            "solution": "Convert passive voice to active voice by making the subject perform the action",
            "examples": [
                {
                    "wrong": "The report was written by the team.",
                    "right": "The team wrote the report.",
                    "explanation": "Move the performer of the action (team) to the subject position"
                },
                {
                    "wrong": "Mistakes were made in the calculation.",
                    "right": "We made mistakes in the calculation.",
                    "explanation": "Identify who made the mistakes and make them the subject"
                }
            ],
            "category": "grammar",
            "severity": "medium",
            "keywords": ["passive voice", "was written", "were made", "is done", "be verb + past participle"]
        },
        {
            "issue_pattern": "subject-verb agreement error",
            "rule_title": "Subject-Verb Agreement",
            "issue_description": "Subject and verb must agree in number (singular/plural)",
            "solution": "Match singular subjects with singular verbs, plural subjects with plural verbs",
            "examples": [
                {
                    "wrong": "The team are working on the project.",
                    "right": "The team is working on the project.",
                    "explanation": "Team is a collective noun treated as singular"
                },
                {
                    "wrong": "Each of the students have submitted their work.",
                    "right": "Each of the students has submitted their work.",
                    "explanation": "Each is singular, so use 'has' not 'have'"
                }
            ],
            "category": "grammar",
            "severity": "high",
            "keywords": ["subject verb agreement", "singular plural", "each", "every", "team", "group"]
        },
        {
            "issue_pattern": "unclear pronoun reference",
            "rule_title": "Clear Pronoun References",
            "issue_description": "Pronouns must clearly refer to specific nouns to avoid confusion",
            "solution": "Replace ambiguous pronouns with specific nouns or restructure the sentence",
            "examples": [
                {
                    "wrong": "When John met Bob, he was excited.",
                    "right": "When John met Bob, John was excited.",
                    "explanation": "Replace 'he' with the specific person's name to clarify who was excited"
                },
                {
                    "wrong": "The software has bugs. This is problematic.",
                    "right": "The software has bugs. These bugs are problematic.",
                    "explanation": "Replace vague 'this' with specific reference to what is problematic"
                }
            ],
            "category": "grammar",
            "severity": "medium",
            "keywords": ["pronoun reference", "unclear antecedent", "this", "that", "it", "they"]
        }
    ],
    
    "clarity_rules": [
        {
            "issue_pattern": "wordy phrase detected",
            "rule_title": "Eliminate Wordiness",
            "issue_description": "Wordy phrases make writing unnecessarily complex and harder to read",
            "solution": "Replace wordy phrases with simpler, more direct alternatives",
            "examples": [
                {
                    "wrong": "In order to complete the task",
                    "right": "To complete the task",
                    "explanation": "Remove unnecessary words 'in order' which add no meaning"
                },
                {
                    "wrong": "Due to the fact that",
                    "right": "Because",
                    "explanation": "Simple 'because' is clearer than the wordy phrase"
                },
                {
                    "wrong": "At this point in time",
                    "right": "Now",
                    "explanation": "One word 'now' replaces five unnecessary words"
                }
            ],
            "category": "clarity",
            "severity": "medium",
            "keywords": ["wordy phrases", "in order to", "due to the fact", "at this point in time", "verbose"]
        },
        {
            "issue_pattern": "jargon or technical term without explanation",
            "rule_title": "Define Technical Terms",
            "issue_description": "Technical jargon can confuse readers unfamiliar with the terms",
            "solution": "Define technical terms on first use or replace with simpler alternatives",
            "examples": [
                {
                    "wrong": "Implement API endpoints for CRUD operations",
                    "right": "Implement API endpoints for Create, Read, Update, Delete (CRUD) operations",
                    "explanation": "Define acronyms on first use to help all readers understand"
                },
                {
                    "wrong": "Optimize the algorithm's Big O complexity",
                    "right": "Optimize how efficiently the algorithm processes data",
                    "explanation": "Replace technical term with plain language explanation"
                }
            ],
            "category": "clarity",
            "severity": "low",
            "keywords": ["jargon", "technical terms", "acronyms", "API", "algorithm", "complex terminology"]
        }
    ],
    
    "punctuation_rules": [
        {
            "issue_pattern": "comma splice detected",
            "rule_title": "Fix Comma Splices",
            "issue_description": "Two independent clauses cannot be joined with just a comma",
            "solution": "Use semicolon, period, or coordinating conjunction with comma",
            "examples": [
                {
                    "wrong": "The meeting started late, everyone was frustrated.",
                    "right": "The meeting started late; everyone was frustrated.",
                    "explanation": "Use semicolon to properly join two independent clauses"
                },
                {
                    "wrong": "I studied hard, I passed the exam.",
                    "right": "I studied hard, so I passed the exam.",
                    "explanation": "Add coordinating conjunction 'so' with the comma"
                }
            ],
            "category": "punctuation",
            "severity": "high",
            "keywords": ["comma splice", "independent clauses", "run-on sentence", "semicolon"]
        }
    ],
    
    "tone_rules": [
        {
            "issue_pattern": "overly casual language",
            "rule_title": "Professional Tone",
            "issue_description": "Casual language may not be appropriate for professional documents",
            "solution": "Replace casual terms with more professional alternatives",
            "examples": [
                {
                    "wrong": "The code is pretty awesome and works great.",
                    "right": "The code is well-designed and functions effectively.",
                    "explanation": "Replace casual 'awesome' and 'great' with professional terms"
                },
                {
                    "wrong": "We gotta fix this ASAP.",
                    "right": "We need to address this immediately.",
                    "explanation": "Replace informal 'gotta' and 'ASAP' with formal language"
                }
            ],
            "category": "tone",
            "severity": "medium",
            "keywords": ["casual language", "awesome", "cool", "gotta", "ASAP", "informal tone"]
        }
    ],
    
    "formatting_rules": [
        {
            "issue_pattern": "inconsistent heading hierarchy",
            "rule_title": "Logical Heading Structure",
            "issue_description": "Headings should follow a logical hierarchy (H1 > H2 > H3)",
            "solution": "Ensure headings progress logically without skipping levels",
            "examples": [
                {
                    "wrong": "# Main Title\n### Subsection (skips H2)",
                    "right": "# Main Title\n## Section\n### Subsection",
                    "explanation": "Follow proper heading hierarchy without skipping levels"
                },
                {
                    "wrong": "## Introduction\n## Methods\n#### Results",
                    "right": "## Introduction\n## Methods\n## Results",
                    "explanation": "Keep sections at the same level consistent"
                }
            ],
            "category": "formatting",
            "severity": "medium",
            "keywords": ["heading hierarchy", "h1", "h2", "h3", "document structure", "outline"]
        },
        {
            "issue_pattern": "inconsistent list formatting",
            "rule_title": "Consistent List Formatting",
            "issue_description": "Lists should use consistent bullet styles and formatting",
            "solution": "Use the same bullet style and formatting throughout the document",
            "examples": [
                {
                    "wrong": "• First item\n- Second item\n* Third item",
                    "right": "• First item\n• Second item\n• Third item",
                    "explanation": "Use the same bullet character throughout the list"
                },
                {
                    "wrong": "1. First\n2) Second\n3. Third",
                    "right": "1. First\n2. Second\n3. Third",
                    "explanation": "Use consistent numbering format (periods vs parentheses)"
                }
            ],
            "category": "formatting",
            "severity": "low",
            "keywords": ["list formatting", "bullets", "numbering", "consistency"]
        }
    ],
    
    "tone_rules": [
        {
            "issue_pattern": "overly casual language",
            "rule_title": "Professional Tone",
            "issue_description": "Casual language may not be appropriate for professional documents",
            "solution": "Replace casual terms with more professional alternatives",
            "examples": [
                {
                    "wrong": "The code is pretty awesome and works great.",
                    "right": "The code is well-designed and functions effectively.",
                    "explanation": "Replace casual 'awesome' and 'great' with professional terms"
                },
                {
                    "wrong": "We gotta fix this ASAP.",
                    "right": "We need to address this immediately.",
                    "explanation": "Replace informal 'gotta' and 'ASAP' with formal language"
                }
            ],
            "category": "tone",
            "severity": "medium",
            "keywords": ["casual language", "awesome", "cool", "gotta", "ASAP", "informal tone"]
        },
        {
            "issue_pattern": "inconsistent voice",
            "rule_title": "Consistent Voice",
            "issue_description": "Maintain consistent voice (first, second, or third person) throughout",
            "solution": "Choose one voice perspective and use it consistently",
            "examples": [
                {
                    "wrong": "You should click the button. We recommend saving first.",
                    "right": "You should click the button. You should save first.",
                    "explanation": "Maintain second person voice throughout instructions"
                },
                {
                    "wrong": "I believe this approach works. Users will find it helpful.",
                    "right": "This approach works effectively. Users will find it helpful.",
                    "explanation": "Avoid mixing first person with third person references"
                }
            ],
            "category": "tone",
            "severity": "medium",
            "keywords": ["voice consistency", "first person", "second person", "third person", "perspective"]
        }
    ],
    
    "capitalization_rules": [
        {
            "issue_pattern": "incorrect proper noun capitalization",
            "rule_title": "Proper Noun Capitalization",
            "issue_description": "Proper nouns should be capitalized consistently",
            "solution": "Capitalize all proper nouns including names, places, and brands",
            "examples": [
                {
                    "wrong": "We use python and javascript for development.",
                    "right": "We use Python and JavaScript for development.",
                    "explanation": "Programming language names are proper nouns and should be capitalized"
                },
                {
                    "wrong": "The meeting is in new york next tuesday.",
                    "right": "The meeting is in New York next Tuesday.",
                    "explanation": "Capitalize proper nouns (places) and days of the week"
                }
            ],
            "category": "capitalization",
            "severity": "medium",
            "keywords": ["proper nouns", "names", "places", "brands", "programming languages"]
        },
        {
            "issue_pattern": "inconsistent title case",
            "rule_title": "Title Case for Headings",
            "issue_description": "Headings should use consistent title case formatting",
            "solution": "Capitalize major words in titles and headings",
            "examples": [
                {
                    "wrong": "how to write better documentation",
                    "right": "How to Write Better Documentation",
                    "explanation": "Capitalize major words in headings (not articles, prepositions, conjunctions)"
                },
                {
                    "wrong": "Getting Started With The API",
                    "right": "Getting Started with the API",
                    "explanation": "Don't capitalize articles (the) and short prepositions (with) unless they start the title"
                }
            ],
            "category": "capitalization",
            "severity": "low",
            "keywords": ["title case", "headings", "major words", "articles", "prepositions"]
        }
    ],
    
    "terminology_rules": [
        {
            "issue_pattern": "inconsistent technical terms",
            "rule_title": "Consistent Technical Terminology",
            "issue_description": "Use technical terms consistently throughout the document",
            "solution": "Choose one term and use it consistently; define abbreviations on first use",
            "examples": [
                {
                    "wrong": "The API endpoint returns data. The interface provides information.",
                    "right": "The API endpoint returns data. The API endpoint provides information.",
                    "explanation": "Use 'API endpoint' consistently instead of mixing with 'interface'"
                },
                {
                    "wrong": "Login to the system. After log-in, you can access features.",
                    "right": "Log in to the system. After logging in, you can access features.",
                    "explanation": "Use 'log in' (verb) consistently; 'login' is a noun"
                }
            ],
            "category": "terminology",
            "severity": "medium",
            "keywords": ["technical terms", "consistency", "API", "login", "terminology", "abbreviations"]
        },
        {
            "issue_pattern": "undefined acronym",
            "rule_title": "Define Acronyms on First Use",
            "issue_description": "Acronyms should be defined when first introduced",
            "solution": "Spell out acronyms on first use, then use the acronym consistently",
            "examples": [
                {
                    "wrong": "Configure the API for your application.",
                    "right": "Configure the Application Programming Interface (API) for your application.",
                    "explanation": "Define API on first use, then you can use 'API' throughout the document"
                },
                {
                    "wrong": "The REST service handles HTTP requests.",
                    "right": "The Representational State Transfer (REST) service handles HyperText Transfer Protocol (HTTP) requests.",
                    "explanation": "Define both REST and HTTP on first use"
                }
            ],
            "category": "terminology",
            "severity": "medium",
            "keywords": ["acronyms", "abbreviations", "API", "REST", "HTTP", "first use", "definition"]
        }
    ],
    
    "accessibility_rules": [
        {
            "issue_pattern": "non-inclusive language",
            "rule_title": "Inclusive Language",
            "issue_description": "Use language that includes and respects all readers",
            "solution": "Replace exclusionary terms with inclusive alternatives",
            "examples": [
                {
                    "wrong": "Hey guys, let's start the meeting.",
                    "right": "Hello everyone, let's start the meeting.",
                    "explanation": "Use 'everyone' instead of 'guys' to include all genders"
                },
                {
                    "wrong": "The system is dummy-proof.",
                    "right": "The system is user-friendly.",
                    "explanation": "Avoid terms that could be offensive; use positive descriptors"
                }
            ],
            "category": "accessibility",
            "severity": "high",
            "keywords": ["inclusive language", "guys", "dummy", "blacklist", "whitelist", "non-inclusive"]
        },
        {
            "issue_pattern": "missing alt text description",
            "rule_title": "Descriptive Alt Text",
            "issue_description": "Images need descriptive alt text for screen readers",
            "solution": "Provide meaningful alt text that describes the image content and purpose",
            "examples": [
                {
                    "wrong": "<img src='chart.png' alt='image'>",
                    "right": "<img src='chart.png' alt='Bar chart showing 50% increase in user engagement over 6 months'>",
                    "explanation": "Describe what the image shows and its significance"
                },
                {
                    "wrong": "<img src='button.png' alt='click here'>",
                    "right": "<img src='button.png' alt='Submit form button'>",
                    "explanation": "Describe the button's function, not just the action"
                }
            ],
            "category": "accessibility",
            "severity": "high",
            "keywords": ["alt text", "images", "screen readers", "accessibility", "descriptive"]
        },
        {
            "issue_pattern": "color-only information",
            "rule_title": "Don't Rely on Color Alone",
            "issue_description": "Information conveyed by color should have additional indicators",
            "solution": "Use text labels, patterns, or symbols in addition to color",
            "examples": [
                {
                    "wrong": "Click the red button to delete",
                    "right": "Click the Delete button (red) to remove the item",
                    "explanation": "Add text label so color-blind users can identify the button"
                },
                {
                    "wrong": "Required fields are shown in red",
                    "right": "Required fields are marked with an asterisk (*) and shown in red",
                    "explanation": "Use symbols in addition to color for accessibility"
                }
            ],
            "category": "accessibility",
            "severity": "high",
            "keywords": ["color", "color blind", "visual indicators", "symbols", "accessibility"]
        }
    ],
    
    "punctuation_rules": [
        {
            "issue_pattern": "comma splice detected",
            "rule_title": "Fix Comma Splices",
            "issue_description": "Two independent clauses cannot be joined with just a comma",
            "solution": "Use semicolon, period, or coordinating conjunction with comma",
            "examples": [
                {
                    "wrong": "The meeting started late, everyone was frustrated.",
                    "right": "The meeting started late; everyone was frustrated.",
                    "explanation": "Use semicolon to properly join two independent clauses"
                },
                {
                    "wrong": "I studied hard, I passed the exam.",
                    "right": "I studied hard, so I passed the exam.",
                    "explanation": "Add coordinating conjunction 'so' with the comma"
                }
            ],
            "category": "punctuation",
            "severity": "high",
            "keywords": ["comma splice", "independent clauses", "run-on sentence", "semicolon"]
        },
        {
            "issue_pattern": "missing oxford comma",
            "rule_title": "Oxford Comma Consistency",
            "issue_description": "Use Oxford comma consistently in lists for clarity",
            "solution": "Include comma before 'and' or 'or' in lists of three or more items",
            "examples": [
                {
                    "wrong": "We need apples, oranges and bananas.",
                    "right": "We need apples, oranges, and bananas.",
                    "explanation": "Oxford comma prevents ambiguity in lists"
                },
                {
                    "wrong": "The team includes developers, designers and project managers.",
                    "right": "The team includes developers, designers, and project managers.",
                    "explanation": "Clearer separation of list items with Oxford comma"
                }
            ],
            "category": "punctuation",
            "severity": "low",
            "keywords": ["oxford comma", "serial comma", "lists", "and", "or"]
        },
        {
            "issue_pattern": "incorrect apostrophe usage",
            "rule_title": "Proper Apostrophe Usage",
            "issue_description": "Apostrophes show possession or contractions, not plurals",
            "solution": "Use apostrophes for possession and contractions only",
            "examples": [
                {
                    "wrong": "The API's are working correctly.",
                    "right": "The APIs are working correctly.",
                    "explanation": "Don't use apostrophes for plurals"
                },
                {
                    "wrong": "Its a great solution for the companys needs.",
                    "right": "It's a great solution for the company's needs.",
                    "explanation": "Use apostrophes for contractions (it's) and possession (company's)"
                }
            ],
            "category": "punctuation",
            "severity": "medium",
            "keywords": ["apostrophe", "possession", "contractions", "plurals", "its", "it's"]
        }
    ],
    
    "clarity_rules": [
        {
            "issue_pattern": "wordy phrase detected",
            "rule_title": "Eliminate Wordiness",
            "issue_description": "Wordy phrases make writing unnecessarily complex and harder to read",
            "solution": "Replace wordy phrases with simpler, more direct alternatives",
            "examples": [
                {
                    "wrong": "In order to complete the task",
                    "right": "To complete the task",
                    "explanation": "Remove unnecessary words 'in order' which add no meaning"
                },
                {
                    "wrong": "Due to the fact that",
                    "right": "Because",
                    "explanation": "Simple 'because' is clearer than the wordy phrase"
                },
                {
                    "wrong": "At this point in time",
                    "right": "Now",
                    "explanation": "One word 'now' replaces five unnecessary words"
                }
            ],
            "category": "clarity",
            "severity": "medium",
            "keywords": ["wordy phrases", "in order to", "due to the fact", "at this point in time", "verbose"]
        },
        {
            "issue_pattern": "jargon or technical term without explanation",
            "rule_title": "Define Technical Terms",
            "issue_description": "Technical jargon can confuse readers unfamiliar with the terms",
            "solution": "Define technical terms on first use or replace with simpler alternatives",
            "examples": [
                {
                    "wrong": "Implement API endpoints for CRUD operations",
                    "right": "Implement API endpoints for Create, Read, Update, Delete (CRUD) operations",
                    "explanation": "Define acronyms on first use to help all readers understand"
                },
                {
                    "wrong": "Optimize the algorithm's Big O complexity",
                    "right": "Optimize how efficiently the algorithm processes data",
                    "explanation": "Replace technical term with plain language explanation"
                }
            ],
            "category": "clarity",
            "severity": "low",
            "keywords": ["jargon", "technical terms", "acronyms", "API", "algorithm", "complex terminology"]
        },
        {
            "issue_pattern": "nominalizations detected",
            "rule_title": "Avoid Nominalizations",
            "issue_description": "Turning verbs into nouns makes writing unnecessarily complex",
            "solution": "Use strong verbs instead of noun forms",
            "examples": [
                {
                    "wrong": "We made the decision to implement the solution.",
                    "right": "We decided to implement the solution.",
                    "explanation": "Use the verb 'decided' instead of the noun 'decision'"
                },
                {
                    "wrong": "The investigation of the issue was conducted by the team.",
                    "right": "The team investigated the issue.",
                    "explanation": "Use active voice with strong verb 'investigated'"
                }
            ],
            "category": "clarity",
            "severity": "medium",
            "keywords": ["nominalizations", "decision", "investigation", "implementation", "strong verbs"]
        },
        {
            "issue_pattern": "hedge words detected",
            "rule_title": "Minimize Hedge Words",
            "issue_description": "Excessive hedge words weaken your message and sound uncertain",
            "solution": "Use hedge words sparingly and be more direct when possible",
            "examples": [
                {
                    "wrong": "I think this might possibly be a somewhat good approach.",
                    "right": "This is a good approach.",
                    "explanation": "Remove unnecessary hedge words for stronger, clearer statement"
                },
                {
                    "wrong": "It seems like this could potentially help users.",
                    "right": "This will help users.",
                    "explanation": "Be direct and confident in your statements"
                }
            ],
            "category": "clarity",
            "severity": "low",
            "keywords": ["hedge words", "think", "might", "possibly", "somewhat", "seems", "potentially"]
        }
    ]
}
