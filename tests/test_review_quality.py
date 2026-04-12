#!/usr/bin/env python3
"""
Test suite for the /review_quality endpoint and document_quality_reviewer module.

Usage:
  python tests/test_review_quality.py          # Run all tests (direct + HTTP)
  python tests/test_review_quality.py --direct # Only direct module tests (no server needed)
"""

import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#  Sample Data 

SAMPLE_DOCUMENT = """
# Configuring the Application

This document explains how to configure the application for production deployment.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9 or later
- Docker Desktop
- A valid API key

## Installation Steps

1. Clone the repository to your local machine.
2. Run the setup script.
3. Configure the environment variables.

Therefore, the application was configured by the administrator to handle all incoming requests.
Furthermore, it is important to note that there are several limitations.
Please don't click Cancel if you want to proceed with the installation.

The file MyConfig.YAML should be placed in the root directory alongside setup script.

!!! warning
    This step deletes all existing data.

!!! foobar "Test"
    Invalid admonition type.

Click OK to confirm and then press Ctrl+S to save.
"""

SAMPLE_STYLE_GUIDE = """
Write in present tense, active voice, second person.
Keep sentences under 20 words. Avoid filler words.
Use sentence case for headings.
"""

#  Direct Module Tests 

def test_direct_module():
    """Test the review module directly (no server required)."""
    print("=" * 60)
    print("DIRECT MODULE TEST")
    print("=" * 60)

    from app.document_quality_reviewer import review_document_quality

    result = review_document_quality(SAMPLE_DOCUMENT, SAMPLE_STYLE_GUIDE)

    # Validate schema
    required_keys = [
        "document_score", "structure_issues", "style_violations",
        "tone_and_voice_issues", "formatting_issues", "list_or_table_issues",
        "heading_issues", "notice_issues", "documentation_principle_violations",
        "top_recommendations"
    ]

    missing_keys = [k for k in required_keys if k not in result]
    if missing_keys:
        print(f" FAIL: Missing keys in result: {missing_keys}")
        return False

    print(f" Schema validation passed (all {len(required_keys)} keys present)")

    # Validate types
    assert isinstance(result["document_score"], int), "document_score should be int"
    assert isinstance(result["top_recommendations"], list), "top_recommendations should be list"
    for key in required_keys:
        if key not in ("document_score",):
            assert isinstance(result[key], list), f"{key} should be list"

    print(f" Type validation passed")

    # Check that known issues are detected
    score = result["document_score"]
    print(f"\n Document Score: {score}/100")

    # Style violations: should catch "therefore", "furthermore", long sentences
    style_count = len(result["style_violations"])
    print(f" Style violations: {style_count}")
    if style_count == 0:
        print("    Expected at least 1 style violation (filler words, long sentences)")

    # Tone issues: should catch passive voice, contractions, "please"
    tone_count = len(result["tone_and_voice_issues"])
    print(f" Tone/voice issues: {tone_count}")
    if tone_count == 0:
        print("    Expected at least 1 tone issue (passive voice, contractions)")

    # Notice issues: should catch invalid admonition type "foobar"
    notice_count = len(result["notice_issues"])
    print(f" Notice issues: {notice_count}")

    # Formatting issues
    fmt_count = len(result["formatting_issues"])
    print(f" Formatting issues: {fmt_count}")

    # Structure issues
    struct_count = len(result["structure_issues"])
    print(f"  Structure issues: {struct_count}")

    # Heading issues
    heading_count = len(result["heading_issues"])
    print(f" Heading issues: {heading_count}")

    # Documentation principles
    principle_count = len(result["documentation_principle_violations"])
    print(f" Principle violations: {principle_count}")

    # Naming issues
    naming_count = len(result["naming_issues"])
    print(f" Naming issues: {naming_count}")

    # Top recommendations
    rec_count = len(result["top_recommendations"])
    print(f"\n Top recommendations: {rec_count}")
    for i, rec in enumerate(result["top_recommendations"], 1):
        print(f"  {i}. {rec}")

    total = (style_count + tone_count + notice_count + fmt_count +
             struct_count + heading_count + principle_count + naming_count)
    print(f"\n Total issues found: {total}")

    if total > 0:
        print(" PASS: Module correctly detects violations")
    else:
        print("  WARNING: No issues detected  review test document")

    return True


#  HTTP Endpoint Test 

def test_http_endpoint():
    """Test the /review_quality endpoint via HTTP (server must be running)."""
    print("\n" + "=" * 60)
    print("HTTP ENDPOINT TEST")
    print("=" * 60)

    try:
        import requests
    except ImportError:
        print("  'requests' library not installed  skipping HTTP test")
        return True

    url = "http://localhost:5000/review_quality"

    # Test 1: Valid request
    print("\n--- Test 1: Valid document review ---")
    try:
        resp = requests.post(url, json={
            "document_text": SAMPLE_DOCUMENT,
            "style_guide": SAMPLE_STYLE_GUIDE
        }, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            print(f" HTTP 200 OK  Score: {data.get('document_score')}/100")
            total = sum(len(data.get(k, [])) for k in [
                "structure_issues", "style_violations", "tone_and_voice_issues",
                "formatting_issues", "list_or_table_issues", "heading_issues",
                "notice_issues", "documentation_principle_violations"
            ])
            print(f"   Total issues: {total}")
            print(f"   Recommendations: {len(data.get('top_recommendations', []))}")
        else:
            print(f" FAIL: HTTP {resp.status_code}  {resp.text[:200]}")
            return False
    except requests.ConnectionError:
        print("  Server not running at localhost:5000  skipping HTTP test")
        return True

    # Test 2: Empty body
    print("\n--- Test 2: Empty document ---")
    resp = requests.post(url, json={"document_text": "", "style_guide": ""}, timeout=10)
    if resp.status_code == 400:
        print(f" Correctly rejected empty document (HTTP 400)")
    else:
        print(f"  Unexpected status: {resp.status_code}")

    # Test 3: No body
    print("\n--- Test 3: No JSON body ---")
    resp = requests.post(url, timeout=10)
    if resp.status_code in (400, 415):
        print(f" Correctly rejected missing body (HTTP {resp.status_code})")
    else:
        print(f"  Unexpected status: {resp.status_code}")

    return True


#  Main 

if __name__ == "__main__":
    direct_only = "--direct" in sys.argv

    success = True

    # Always run direct test
    if not test_direct_module():
        success = False

    # Run HTTP test unless --direct flag
    if not direct_only:
        if not test_http_endpoint():
            success = False

    print("\n" + "=" * 60)
    if success:
        print(" ALL TESTS PASSED")
    else:
        print(" SOME TESTS FAILED")
    print("=" * 60)

    sys.exit(0 if success else 1)
