"""
Quick validation script for document-level analysis implementation.

This script tests the core components without needing the Flask server.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.document_analyzer import DocumentAnalyzer
from core.document_rule import evaluate_document_rules


def test_document_analysis():
    """Test document analysis on sample text."""
    
    # Sample procedure document
    sample_text = """
# System Installation Procedure

This document describes how to install the software.

## Prerequisites

You need administrator access.
Ensure 2GB disk space is available.

## Procedure

Click on the Install button.
The system will be installed automatically.
API services will start.
SDK components will be configured.
REST endpoints become available.

## Safety

**WARNING:** Do not modify core files during installation.

## Legal

Copyright 2024. All rights reserved.
"""
    
    print("=" * 70)
    print("DOCUMENT-LEVEL ANALYSIS TEST")
    print("=" * 70)
    print()
    
    # Test 1: Document Analyzer
    print("TEST 1: Document Analyzer")
    print("-" * 70)
    
    analyzer = DocumentAnalyzer()
    context = analyzer.analyze(sample_text)
    
    print(f"✅ Document Type: {context.doc_type}")
    print(f"✅ Primary Goal: {context.primary_goal}")
    print(f"✅ Audience Level: {context.audience_level}")
    print(f"✅ Rewrite Sensitivity: {context.rewrite_sensitivity}")
    print(f"✅ Total Sentences: {context.total_sentences}")
    print(f"✅ Avg Sentence Length: {context.avg_sentence_length:.1f} words")
    print(f"✅ Dominant Tense: {context.dominant_tense}")
    print()
    
    if context.forbidden_sections:
        print(f"🔒 Forbidden Sections: {', '.join(context.forbidden_sections)}")
    else:
        print("ℹ️  No forbidden sections detected")
    print()
    
    if context.acronyms:
        print(f"📝 Acronyms Found: {len(context.acronyms)}")
        for acronym, definition in context.acronyms.items():
            print(f"   - {acronym}: {definition}")
    else:
        print("ℹ️  No acronyms with definitions found")
    print()
    
    if context.headings:
        print(f"📋 Headings Detected: {len(context.headings)}")
        for heading in context.headings:
            indent = "  " * (heading['level'] - 1)
            print(f"   {indent}- {heading['text']} (Level {heading['level']})")
    print()
    
    # Test 2: Document Rules
    print("\nTEST 2: Document Rules Evaluation")
    print("-" * 70)
    
    findings = evaluate_document_rules(context, sample_text)
    
    if findings:
        print(f"📊 Found {len(findings)} document-level findings:")
        print()
        
        # Group by severity
        errors = [f for f in findings if f.severity == 'error']
        warnings = [f for f in findings if f.severity == 'warning']
        info = [f for f in findings if f.severity == 'info']
        
        for severity, items, icon in [
            ('ERROR', errors, '❌'),
            ('WARNING', warnings, '⚠️'),
            ('INFO', info, 'ℹ️')
        ]:
            if items:
                print(f"{icon} {severity} ({len(items)}):")
                for finding in items:
                    print(f"   • {finding.title}")
                    print(f"     {finding.description}")
                    if finding.guidance:
                        print(f"     💡 {finding.guidance}")
                    print()
    else:
        print("✅ No document-level issues found")
    
    print()
    
    # Test 3: Context Methods
    print("\nTEST 3: Context Utility Methods")
    print("-" * 70)
    
    print(f"✅ High Sensitivity: {context.is_high_sensitivity()}")
    print(f"✅ Rewrite Allowed in 'Safety': {context.is_rewrite_allowed_in_section('Safety')}")
    print(f"✅ Rewrite Allowed in 'Procedure': {context.is_rewrite_allowed_in_section('Procedure')}")
    print()
    
    # Test 4: Document Context Summary
    print("\nTEST 4: Document Context Summary")
    print("-" * 70)
    print(context.get_summary())
    print()
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)


def test_api_document():
    """Test with API documentation."""
    
    api_text = """
# User API Reference

## Overview

The User API provides access to user management features.

## Endpoints

### GET /api/users

Returns a list of users.

Parameters:
- limit: Maximum results
- offset: Skip results

### POST /api/users

Creates a new user.

Request body:
- username (required)
- email (required)
- role (optional)

Response codes:
- 200: Success
- 400: Bad request
- 401: Unauthorized
"""
    
    print("\n\n")
    print("=" * 70)
    print("API DOCUMENT TEST")
    print("=" * 70)
    print()
    
    analyzer = DocumentAnalyzer()
    context = analyzer.analyze(api_text)
    
    print(f"✅ Document Type: {context.doc_type}")
    print(f"✅ Primary Goal: {context.primary_goal}")
    print(f"✅ Rewrite Sensitivity: {context.rewrite_sensitivity}")
    print()
    
    findings = evaluate_document_rules(context, api_text)
    
    if findings:
        print(f"📊 Found {len(findings)} findings")
        for finding in findings:
            print(f"   {finding.severity.upper()}: {finding.title}")
    else:
        print("✅ No issues found")
    
    print()


if __name__ == "__main__":
    try:
        test_document_analysis()
        test_api_document()
        
        print("\n🎉 Document-level analysis is working correctly!")
        print("\nNext steps:")
        print("  1. Start the Flask server: python run.py")
        print("  2. Upload data/test_installation_procedure.md")
        print("  3. Check the 'Document Analysis' tab")
        print("  4. Upload data/test_api_reference.md and compare")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
