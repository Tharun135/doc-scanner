"""
Utility functions for parsing structured AI suggestions.
"""

def parse_structured_suggestion(suggestion_text):
    """
    Parse a structured suggestion into its components.
    
    Expected format:
    Issue: [brief description]
    Original sentence: [sentence]
    AI suggestion: [recommendation]
    
    Args:
        suggestion_text (str): The structured suggestion string
    
    Returns:
        dict: Contains 'issue', 'original_sentence', and 'ai_suggestion' keys
    """
    if not suggestion_text:
        return {
            'issue': suggestion_text,
            'original_sentence': '',
            'ai_suggestion': ''
        }
    
    # Check if this is a structured suggestion
    if 'Issue:' in suggestion_text and 'Original sentence:' in suggestion_text and 'AI suggestion:' in suggestion_text:
        lines = suggestion_text.split('\n')
        
        issue = ''
        original_sentence = ''
        ai_suggestion = ''
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Issue:'):
                current_section = 'issue'
                issue = line.replace('Issue:', '').strip()
            elif line.startswith('Original sentence:'):
                current_section = 'original_sentence'
                original_sentence = line.replace('Original sentence:', '').strip()
            elif line.startswith('AI suggestion:'):
                current_section = 'ai_suggestion'
                ai_suggestion = line.replace('AI suggestion:', '').strip()
            elif current_section and line:
                # Continue reading multi-line content
                if current_section == 'issue':
                    issue += ' ' + line
                elif current_section == 'original_sentence':
                    original_sentence += ' ' + line
                elif current_section == 'ai_suggestion':
                    ai_suggestion += ' ' + line
        
        return {
            'issue': issue,
            'original_sentence': original_sentence,
            'ai_suggestion': ai_suggestion
        }
    else:
        # Legacy format - treat entire text as issue
        return {
            'issue': suggestion_text,
            'original_sentence': '',
            'ai_suggestion': ''
        }

def format_for_display(suggestion_dict):
    """
    Format parsed suggestion for display in different contexts.
    
    Args:
        suggestion_dict (dict): Parsed suggestion components
    
    Returns:
        dict: Contains 'brief' for issue list and 'detailed' for full view
    """
    return {
        'brief': suggestion_dict['issue'],
        'detailed': f"Issue: {suggestion_dict['issue']}\nOriginal sentence: {suggestion_dict['original_sentence']}\nAI suggestion: {suggestion_dict['ai_suggestion']}"
    }
