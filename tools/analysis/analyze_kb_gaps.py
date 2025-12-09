#!/usr/bin/env python3
"""
Analyze extraction failures and identify KB gaps for passive voice handling.
"""

import requests
import json

def analyze_extraction_failures():
    """Analyze what patterns are causing extraction failures."""
    
    print("🔍 ANALYZING EXTRACTION FAILURE PATTERNS")
    print("=" * 45)
    
    # Test cases that are still failing
    failing_cases = [
        {
            "name": "File Upload Passive",
            "feedback": "passive voice detected by rule", 
            "sentence": "The file was uploaded by the user.",
            "expected_active": "The user uploaded the file."
        },
        {
            "name": "Document Creation",
            "feedback": "passive voice detected by rule",
            "sentence": "The document was created by the system.",
            "expected_active": "The system created the document."
        },
        {
            "name": "Data Processing",
            "feedback": "passive voice detected by rule",
            "sentence": "The data is processed by the algorithm.", 
            "expected_active": "The algorithm processes the data."
        }
    ]
    
    extraction_patterns = {}
    
    for test_case in failing_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Sentence: '{test_case['sentence']}'")
        print(f"   Expected: '{test_case['expected_active']}'")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                
                print(f"   AI Answer: \"{ai_answer}\"")
                print(f"   Suggestion: \"{suggestion}\"")
                
                # Analyze patterns in the AI response
                patterns = []
                if '[' in ai_answer and ']' in ai_answer:
                    patterns.append("bracket_pattern")
                if '"' in ai_answer:
                    patterns.append("quoted_content")
                if 'rewrite:' in ai_answer.lower():
                    patterns.append("rewrite_marker")
                if any(word in ai_answer.lower() for word in ['uploaded', 'created', 'processes']):
                    patterns.append("contains_active_verbs")
                    
                extraction_patterns[test_case['name']] = {
                    'ai_response': ai_answer,
                    'suggestion': suggestion,
                    'patterns': patterns,
                    'extraction_success': suggestion != test_case['sentence'] and len(suggestion) > len(test_case['sentence'])
                }
                
                # Check if extraction worked
                if suggestion == test_case['sentence']:
                    print(f"   ❌ EXTRACTION FAILED: Using original sentence")
                elif 'uploadeds' in suggestion or 'createds' in suggestion:
                    print(f"   ❌ DETERMINISTIC FALLBACK: Using broken grammar")
                else:
                    print(f"   ✅ EXTRACTION SUCCESS: Meaningful rewrite")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summarize findings
    print(f"\n📊 PATTERN ANALYSIS SUMMARY")
    print("=" * 30)
    
    for name, data in extraction_patterns.items():
        print(f"\n{name}:")
        print(f"  Patterns found: {data['patterns']}")
        print(f"  Extraction success: {data['extraction_success']}")
        if not data['extraction_success']:
            print(f"  Issue: AI response contains good content but extraction failed")
    
    return extraction_patterns

def identify_kb_gaps():
    """Identify what KB resources would help with extraction."""
    
    print(f"\n🎯 IDENTIFYING KB GAPS FOR PASSIVE VOICE")
    print("=" * 40)
    
    # Current KB query for passive voice
    from app.services.enrichment import _get_collection, _cached_vector_query
    
    col = _get_collection()
    if col:
        # Test what we currently have for passive voice
        query_results = _cached_vector_query("passive voice convert active voice", n_results=5)
        
        if query_results and query_results.get('documents'):
            print(f"✅ Current KB entries for passive voice: {len(query_results['documents'][0])}")
            
            for i, (doc, meta) in enumerate(zip(
                query_results['documents'][0][:3],
                query_results['metadatas'][0][:3] if query_results.get('metadatas') else [{}]*3
            )):
                rule_id = meta.get('rule_id', f'unknown_{i}')
                title = meta.get('title', 'Unknown Rule')
                print(f"  {i+1}. {rule_id}: {title}")
                print(f"     Content: {doc[:100]}...")
        else:
            print(f"❌ No KB entries found for passive voice")
    
    # Gaps we need to fill
    needed_resources = [
        {
            "type": "Extraction Patterns",
            "purpose": "Help AI provide structured responses",
            "content": "Template formats for passive-to-active conversion responses"
        },
        {
            "type": "Common Passive Constructions", 
            "purpose": "Comprehensive pattern coverage",
            "content": "was/were + past participle, is/are + past participle, can be + past participle"
        },
        {
            "type": "Active Voice Templates",
            "purpose": "Guide AI toward consistent output formats", 
            "content": "Subject + active verb + object patterns"
        },
        {
            "type": "Response Format Guidelines",
            "purpose": "Ensure extractable AI responses",
            "content": "How to structure passive voice conversion responses"
        }
    ]
    
    print(f"\n📋 RECOMMENDED KB ADDITIONS:")
    for i, resource in enumerate(needed_resources, 1):
        print(f"{i}. {resource['type']}")
        print(f"   Purpose: {resource['purpose']}")
        print(f"   Content: {resource['content']}")
        print()
    
    return needed_resources

if __name__ == "__main__":
    # Analyze current failures
    patterns = analyze_extraction_failures()
    
    # Identify what KB resources we need
    gaps = identify_kb_gaps()
    
    print(f"\n💡 SOLUTION STRATEGY:")
    print(f"1. Add comprehensive passive voice conversion patterns to KB")
    print(f"2. Include response format templates for consistent AI output")
    print(f"3. Add extraction guidance for common passive constructions")  
    print(f"4. Create specific rules for AI response structuring")
    print(f"5. Test extraction improvement with enhanced KB")
