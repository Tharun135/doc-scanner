#!/usr/bin/env python3
"""
Test script for the LLM-enhanced passive voice detection and rewriting.
This script tests both the LLM-based and fallback mechanisms.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from rules.passive_voice import check, generate_active_voice_with_llm, convert_with_llm_api, convert_with_offline_logic

def test_llm_passive_voice_conversion():
    """Test LLM-based passive voice conversion."""
    print("=" * 60)
    print("TESTING LLM-ENHANCED PASSIVE VOICE CONVERSION")
    print("=" * 60)
    
    test_cases = [
        "This tool is needed to complete the task.",
        "The report was completed by the team.",
        "Settings are configured in the admin panel.",
        "The file was created by the system automatically.",
        "Data is processed using advanced algorithms.",
        "The application was developed over several months.",
        "Passwords are required to access the system.",
        "The document was exported to PDF format.",
        "Changes were made to improve performance.",
        "The code is tested before deployment.",
        "New features are being implemented.",
        "The system has been updated with security patches.",
        "Files can be uploaded through the web interface.",
        "The database is backed up nightly."
    ]
    
    print("\n1. Testing LLM API Conversion:")
    print("-" * 40)
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n{i}. Original: {sentence}")
        
        # Test LLM conversion
        llm_result = convert_with_llm_api(sentence)
        if llm_result:
            print(f"   LLM Rewrite: {llm_result}")
        else:
            print(f"   LLM Rewrite: [LLM not available or failed]")
        
        # Test offline fallback
        offline_result = convert_with_offline_logic(sentence)
        if offline_result:
            print(f"   Offline Rewrite: {offline_result}")
        else:
            print(f"   Offline Rewrite: [No pattern match]")

def test_full_passive_voice_check():
    """Test the complete passive voice check function."""
    print("\n" + "=" * 60)
    print("TESTING FULL PASSIVE VOICE CHECK FUNCTION")
    print("=" * 60)
    
    test_documents = [
        "This tool is needed to complete the task. The report was finished by our team.",
        "Settings are configured in the admin panel. The system processes data automatically.",
        "The file was created by the application. New features are being implemented daily.",
        "Passwords are required for access. The database is backed up every night.",
        "The code is tested before deployment. Changes were made to improve performance."
    ]
    
    for i, document in enumerate(test_documents, 1):
        print(f"\nDocument {i}:")
        print(f"Text: {document}")
        print("Suggestions:")
        
        suggestions = check(document)
        if suggestions:
            for j, suggestion in enumerate(suggestions, 1):
                print(f"  {j}. {suggestion}")
        else:
            print("  No passive voice detected.")

def test_edge_cases():
    """Test edge cases and complex passive constructions."""
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES AND COMPLEX CONSTRUCTIONS")
    print("=" * 60)
    
    edge_cases = [
        "The system has been completely redesigned to improve usability.",
        "Data can be exported in multiple formats including CSV and JSON.",
        "The application is being tested by our quality assurance team.",
        "Security measures were implemented to protect user information.",
        "The interface has been optimized for mobile devices.",
        "Reports are generated automatically at the end of each month.",
        "The software will be updated to the latest version tomorrow.",
        "User accounts are created when registration is completed."
    ]
    
    for i, sentence in enumerate(edge_cases, 1):
        print(f"\n{i}. Testing: {sentence}")
        
        # Test complete check function
        suggestions = check(sentence)
        if suggestions:
            print(f"   Result: {suggestions[0]}")
        else:
            print(f"   Result: No passive voice detected")

def test_performance_comparison():
    """Compare performance between LLM and offline methods."""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE COMPARISON")
    print("=" * 60)
    
    import time
    
    test_sentence = "The report was completed by the development team yesterday."
    num_iterations = 5
    
    # Test LLM performance
    print(f"\nTesting LLM conversion ({num_iterations} iterations):")
    start_time = time.time()
    llm_results = []
    
    for _ in range(num_iterations):
        result = convert_with_llm_api(test_sentence)
        llm_results.append(result)
    
    llm_time = time.time() - start_time
    print(f"LLM Average Time: {llm_time/num_iterations:.3f} seconds per conversion")
    print(f"LLM Results: {set(filter(None, llm_results))}")
    
    # Test offline performance
    print(f"\nTesting Offline conversion ({num_iterations} iterations):")
    start_time = time.time()
    offline_results = []
    
    for _ in range(num_iterations):
        result = convert_with_offline_logic(test_sentence)
        offline_results.append(result)
    
    offline_time = time.time() - start_time
    print(f"Offline Average Time: {offline_time/num_iterations:.3f} seconds per conversion")
    print(f"Offline Results: {set(filter(None, offline_results))}")

if __name__ == "__main__":
    try:
        test_llm_passive_voice_conversion()
        test_full_passive_voice_check()
        test_edge_cases()
        test_performance_comparison()
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)
        print("\nThe LLM-enhanced passive voice detection is now ready!")
        print("It will use LLM for natural rewrites when available,")
        print("and fall back to pattern-based logic when needed.")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        print("Make sure you have:")
        print("1. spaCy English model installed: python -m spacy download en_core_web_sm")
        print("2. Ollama installed and running (optional, for LLM features)")
        print("3. Required dependencies: pip install ollama spacy beautifulsoup4")
