import os

file_path = 'd:/doc-scanner/app/templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'Get AI-powered suggestions': 'Get rule-based guidance',
    'AI Smart Correction': 'Rule Guidance',
    'Apply & Teach AI': 'Apply Correction',
    'AI-Powered Suggestions': 'Rule-Based Guidance',
    'Click the AI icon next to any issue to get intelligent suggestions': 'Click the guidance icon next to any issue to get rule details',
    'AI Writing Assistant': 'Rule Guidance Assistant',
    '>AI Assistance<': '>Rule Guidance<',
    'Processing with AI... this may take a few minutes.': 'Processing with Rule Engine...',
    'Analyzing with AI...': 'Analyzing with Rules...',
    'Querying AI Assistant': 'Querying Knowledge Base',
    'Processing your document with AI-powered insights': 'Processing your document with rule-based insights',
    'Intelligent AI Analysis': 'Intelligent Rule Analysis',
    'The AI analysis found your writing to be clear': 'The rule engine found your writing to be clear',
    'Context-aware suggestions using advanced AI': 'Context-aware guidance using advanced rules',
    'Initializing Intelligent AI Analysis': 'Initializing Rule Analysis',
    'Getting AI suggestions...': 'Getting guidance...',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
