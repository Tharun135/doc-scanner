import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import extract_sentences_with_html_preservation, analyze_sentence
from app.rules.passive_voice import check as check_passive_voice

def test_contextual_passive_voice():
    html_content = """
    <html>
        <body>
            <h1>Installation Guide</h1>
            
            <h2>Prerequisites</h2>
            <p>A project has been added as described in the documentation.</p>
            
            <h2>Steps</h2>
            <p>A project has been added as described in the documentation.</p>
        </body>
    </html>
    """
    
    print("Testing contextual passive voice detection...")
    
    # 1. Extract sentences with heading context
    sentences = extract_sentences_with_html_preservation(html_content)
    
    # Extract the two identical sentences
    prereq_sentence = None
    steps_sentence = None
    
    for s in sentences:
        if "A project has been added" in s.text:
            if "Prerequisites" in s.heading_context:
                prereq_sentence = s
            elif "Steps" in s.heading_context:
                steps_sentence = s
                
    assert prereq_sentence is not None, "Prerequisite sentence not found"
    assert steps_sentence is not None, "Steps sentence not found"
    
    print(f"Found sentence 1 with context: '{prereq_sentence.heading_context}'")
    print(f"Found sentence 2 with context: '{steps_sentence.heading_context}'")
    
    # 2. Analyze both sentences
    rules = [check_passive_voice]
    
    prereq_feedback, _, _ = analyze_sentence(
        prereq_sentence.text,
        rules,
        heading_context=prereq_sentence.heading_context
    )
    
    steps_feedback, _, _ = analyze_sentence(
        steps_sentence.text,
        rules,
        heading_context=steps_sentence.heading_context
    )
    
    # 3. Verify results
    
    # Check if prereq sentence has any feedback
    prereq_rewrite = len(prereq_feedback) > 0

    if not prereq_rewrite:
        print("SUCCESS: Passive voice in 'Prerequisites' was correctly NOT flagged.")
    else:
        print("FAILED: Passive voice in 'Prerequisites' was incorrectly flagged.")
        for f in prereq_feedback: print(f)
        
    # Check if steps sentence has rewrite decision or is flagged
    steps_rewrite = False
    for f in steps_feedback:
        if isinstance(f, dict):
            if f.get('decision_type') == 'rewrite':
                steps_rewrite = True
            elif 'Passive voice detected' in f.get('message', ''):
                steps_rewrite = True
    
    if steps_rewrite:
        print("SUCCESS: Passive voice in 'Steps' was correctly flagged.")
    else:
        print("FAILED: Passive voice in 'Steps' was NOT flagged.")
        for f in steps_feedback: print(f)
        
    # Assertions for CI/test runner
    assert not prereq_rewrite, "Sentence in Prerequisites should not be flagged"
    assert steps_rewrite, "Sentence in Steps should be flagged"
    
    print("All assertions passed!")

if __name__ == "__main__":
    test_contextual_passive_voice()
