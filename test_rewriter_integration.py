"""
Test script for the integrated rewriter functionality
Run this to verify that the rewriter integration is working properly
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"

def test_rewriter_status():
    """Test if the rewriter service is available."""
    try:
        response = requests.get(f"{BASE_URL}/api/rewriter/status")
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Rewriter status check passed")
            logger.info(f"Models available: {result.get('models', {})}")
            return True
        else:
            logger.error(f"❌ Rewriter status check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Rewriter status check failed: {e}")
        return False

def test_rewrite_suggestion():
    """Test the integrated rewrite suggestion endpoint."""
    try:
        test_data = {
            "text": "The utilization of this methodology enables the facilitation of improved outcomes.",
            "mode": "simplicity",
            "feedback": "This sentence is too complex and hard to read"
        }
        
        response = requests.post(f"{BASE_URL}/rewrite-suggestion", json=test_data)
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Rewrite suggestion test passed")
            logger.info(f"Original: {test_data['text']}")
            logger.info(f"Rewritten: {result.get('suggestion', 'No suggestion')}")
            return True
        else:
            logger.error(f"❌ Rewrite suggestion test failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Rewrite suggestion test failed: {e}")
        return False

def test_readability_analysis():
    """Test the readability analysis endpoint."""
    try:
        test_data = {
            "text": "This is a simple sentence that should be easy to read and understand for most people."
        }
        
        response = requests.post(f"{BASE_URL}/readability-analysis", json=test_data)
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Readability analysis test passed")
            scores = result.get('scores', {})
            logger.info(f"Flesch Reading Ease: {scores.get('flesch_reading_ease', 'N/A')}")
            logger.info(f"Difficulty Level: {scores.get('difficulty_level', 'N/A')}")
            return True
        else:
            logger.error(f"❌ Readability analysis test failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Readability analysis test failed: {e}")
        return False

def test_document_rewrite():
    """Test the full document rewrite endpoint."""
    try:
        test_data = {
            "content": "The methodology that was implemented by the team resulted in significant improvements. The utilization of advanced techniques facilitated better outcomes. This approach is recommended for future projects.",
            "mode": "clarity"
        }
        
        response = requests.post(f"{BASE_URL}/document-rewrite", json=test_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info("✅ Document rewrite test passed")
                logger.info(f"Original length: {len(test_data['content'])} characters")
                rewritten = result.get('rewritten_content', '')
                logger.info(f"Rewritten length: {len(rewritten)} characters")
                improvements = result.get('improvements', {})
                logger.info(f"Readability improvement: {improvements.get('readability_change', 0)} points")
                return True
            else:
                logger.error(f"❌ Document rewrite failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Document rewrite test failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Document rewrite test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting rewriter integration tests...")
    
    tests = [
        ("Rewriter Status", test_rewriter_status),
        ("Rewrite Suggestion", test_rewrite_suggestion), 
        ("Readability Analysis", test_readability_analysis),
        ("Document Rewrite", test_document_rewrite)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            logger.warning(f"Test '{test_name}' failed but continuing...")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All integration tests passed! The rewriter is working correctly.")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
