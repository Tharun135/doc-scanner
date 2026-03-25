import re
from bs4 import BeautifulSoup

def check(sentence_text):
    """
    Siemens Style Guide rule checker for a single sentence.
    Flags words/phrases from the Siemens IX Design-based style guide.
    Returns issues in the standard DocScanner rich-dict format.
    """
    issues = []
    
    # Each rule is a tuple of:
    #   (regex_pattern, message, guidance, decision_type)
    banned_phrases = [
        (
            r"\b(master/slave)\b",
            "Siemens Style: Avoid 'master/slave'",
            "Do not use 'master/slave'. It is not appropriate due to misinterpretation risks. Rewrite using inclusive alternatives such as 'primary/replica', 'controller/worker', or 'source/target'.",
            "guide"
        ),
        (
            r"\b(e\.g\.|e\. g\.)\b",
            "Siemens Style: Avoid abbreviation 'e.g.'",
            "Do not use 'e.g.' Spell out 'for example', 'such as', or 'including' instead. Siemens style prohibits unexpanded abbreviations.",
            "guide"
        ),
        (
            r"\b(simply|it's very easy)\b",
            "Siemens Style: Avoid 'simply' or 'it's very easy'",
            "Avoid using 'simply' or 'it's very easy' outside of the 'Getting Started' section. They are too colloquial and may frustrate users who are struggling. Remove the word or rewrite the sentence without minimizing the task.",
            "guide"
        ),
        (
            r"\b(for that reason)\b",
            "Siemens Style: Avoid filler expression 'for that reason'",
            "Remove 'for that reason'. It is a filler expression. Replace it with a concise cause-and-effect sentence or combine the two ideas into one.",
            "guide"
        ),
        (
            r"\b(therefore)\b",
            "Siemens Style: Avoid filler word 'therefore'",
            "Remove 'therefore'. It is a filler word. Rewrite the sentence so the consequence is stated directly without a linking adverb.",
            "guide"
        ),
        (
            r"\b(furthermore)\b",
            "Siemens Style: Avoid filler word 'furthermore'",
            "Remove 'furthermore'. It is a filler word. Break the sentence into two independent sentences or restructure the list of points.",
            "guide"
        ),
        (
            r"\b(should)\b",
            "Siemens Style: Avoid 'should' — it is ambiguous",
            "Replace 'should' with a direct imperative or a definitive statement. 'Should' provides room for interpretation. Example: 'You should click Save' → 'Click Save'.",
            "guide"
        ),
        (
            r"\b(could)\b",
            "Siemens Style: Avoid 'could' — it is ambiguous",
            "Replace 'could' with a definitive statement if describing a required action. 'Could' provides room for interpretation. Use 'can' for capability statements, or rewrite as a direct instruction.",
            "guide"
        ),
        (
            r"\b(it is)\b",
            "Siemens Style: Avoid weak expression 'it is'",
            "Rewrite to remove 'it is'. Weak expletive constructions dilute clarity. Example: 'It is important to save the file' → 'Save the file'.",
            "guide"
        ),
        (
            r"\b(there is|there are)\b",
            "Siemens Style: Avoid weak expressions 'there is' / 'there are'",
            "Rewrite to replace 'there is' or 'there are' with a direct subject-verb statement. Example: 'There are three options' → 'Three options are available'.",
            "guide"
        ),
        (
            r"\b(can't|won't)\b",
            "Siemens Style: Avoid negative contractions ('can't', 'won't')",
            "Replace negative contractions with their full forms: 'can't' → 'cannot', 'won't' → 'will not'. Negative contractions can appear too informal in technical documentation.",
            "guide"
        ),
        (
            r"\b(you'll|we've|you'd)\b",
            "Siemens Style: Avoid positive contractions ('you'll', 'we've', etc.)",
            "Replace positive contractions with their full forms: 'you'll' → 'you will', 'we've' → 'we have'. Use full forms to maintain a professional but approachable tone.",
            "guide"
        ),
        (
            r"\b(his|hers|him|salesman)\b",
            "Siemens Style: Use gender-neutral language",
            "Replace gendered words with neutral alternatives: 'his/hers' → 'their', 'him' → 'them', 'salesman' → 'salesperson'. Siemens style requires inclusive, gender-neutral language.",
            "guide"
        ),
        (
            r"\b(hey there)\b",
            "Siemens Style: Avoid overly casual greetings",
            "Replace casual greetings like 'Hey there!' with professional alternatives such as 'Welcome to this application'. The tone should be natural but not colloquial.",
            "guide"
        ),
        (
            r"\b(last update|last version)\b",
            "Siemens Style: 'Last' implies finality — use 'Latest' or 'Previous'",
            "Replace 'last update/version' with the correct term: 'latest update' (most recent, more may follow) or 'previous version' (the one before current). 'Last' implies nothing else will follow.",
            "guide"
        ),
        (
            r"\b(please)\b",
            "Siemens Style: Avoid unnecessary 'please'",
            "Remove 'please' unless the request is genuinely inconvenient or unplanned. In standard instructions, 'please' adds no value. Example: 'Please click OK' → 'Click OK'.",
            "guide"
        ),
        (
            r"\b(e\.g\.|i\.e\.)\b",
            "Siemens Style: Avoid Latin abbreviations (e.g., i.e.)",
            "Do not use Latin abbreviations. Replace 'e.g.' with 'for example', 'such as', or 'including'. Replace 'i.e.' with 'that is' or 'in other words'.",
            "guide"
        ),
    ]

    sentence_lower = sentence_text.lower()
    for pattern, message, guidance, decision_type in banned_phrases:
        if re.search(pattern, sentence_lower, re.IGNORECASE):
            issues.append({
                'text': sentence_text,
                'start': 0,
                'end': len(sentence_text),
                'message': message,
                'decision_type': decision_type,
                'rule': 'siemens_style',
                'reviewer_rationale': guidance
            })
            # We don't break here to allow multiple matches per sentence if needed
            # but usually Siemens style prefers one clear message.
            # Keeping it as is to see multiple if they exist.

    return issues
