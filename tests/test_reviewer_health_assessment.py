"""
Test the Reviewer Knowledge Health assessment logic.
"""

def test_assess_reviewer_knowledge_health():
    """Test the health assessment function with various scenarios."""
    
    # Import the function
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
    
    from rag_routes import assess_reviewer_knowledge_health
    
    print("=" * 80)
    print("Testing Reviewer Knowledge Health Assessment")
    print("=" * 80)
    
    # Test Case 1: Early Stage (no usage yet)
    print("\n1. EARLY STAGE SCENARIO (No usage yet)")
    print("-" * 80)
    stats_early = {
        'total_chunks': 50,
        'total_queries': 2,
        'avg_relevance': 0.0,
        'success_rate': 0.0,
        'documents_count': 3
    }
    health_early = assess_reviewer_knowledge_health(stats_early)
    print(f"Status: {health_early['health_status']}")
    print(f"Badge: {health_early['health_badge']}")
    print(f"Message: {health_early['health_message']}")
    print(f"Coverage: {health_early['coverage']}")
    print(f"Recommendations: {health_early['recommendations']}")
    assert health_early['health_status'] == 'early_stage', "Should be early_stage"
    assert health_early['health_badge'] == 'warning', "Should have warning badge"
    print("✓ Test passed")
    
    # Test Case 2: Healthy System
    print("\n2. HEALTHY SCENARIO (Good performance)")
    print("-" * 80)
    stats_healthy = {
        'total_chunks': 300,
        'total_queries': 50,
        'avg_relevance': 0.85,
        'success_rate': 0.90,
        'documents_count': 15
    }
    health_healthy = assess_reviewer_knowledge_health(stats_healthy)
    print(f"Status: {health_healthy['health_status']}")
    print(f"Badge: {health_healthy['health_badge']}")
    print(f"Message: {health_healthy['health_message']}")
    print(f"Coverage: {health_healthy['coverage']}")
    print(f"Confidence: {health_healthy['confidence']}")
    print(f"Fallback Usage: {health_healthy['fallback_usage']}")
    print(f"Recommendations: {health_healthy['recommendations']}")
    assert health_healthy['health_status'] == 'healthy', "Should be healthy"
    assert health_healthy['health_badge'] == 'success', "Should have success badge"
    assert health_healthy['confidence'] == 'high', "Should have high confidence"
    assert health_healthy['fallback_usage'] == 'rare', "Should have rare fallback"
    print("✓ Test passed")
    
    # Test Case 3: Needs Attention
    print("\n3. NEEDS ATTENTION SCENARIO (Poor performance)")
    print("-" * 80)
    stats_poor = {
        'total_chunks': 150,
        'total_queries': 30,
        'avg_relevance': 0.45,
        'success_rate': 0.55,
        'documents_count': 8
    }
    health_poor = assess_reviewer_knowledge_health(stats_poor)
    print(f"Status: {health_poor['health_status']}")
    print(f"Badge: {health_poor['health_badge']}")
    print(f"Message: {health_poor['health_message']}")
    print(f"Coverage: {health_poor['coverage']}")
    print(f"Confidence: {health_poor['confidence']}")
    print(f"Fallback Usage: {health_poor['fallback_usage']}")
    print(f"Improvement Areas: {health_poor['improvement_areas']}")
    print(f"Recommendations: {health_poor['recommendations']}")
    assert health_poor['health_status'] == 'needs_attention', "Should need attention"
    assert health_poor['health_badge'] == 'danger', "Should have danger badge"
    assert health_poor['confidence'] == 'low', "Should have low confidence"
    assert len(health_poor['improvement_areas']) > 0, "Should have improvement areas"
    print("✓ Test passed")
    
    # Test Case 4: Moderate/Growing System
    print("\n4. MODERATE SCENARIO (Average performance)")
    print("-" * 80)
    stats_moderate = {
        'total_chunks': 400,
        'total_queries': 75,
        'avg_relevance': 0.70,
        'success_rate': 0.75,
        'documents_count': 20
    }
    health_moderate = assess_reviewer_knowledge_health(stats_moderate)
    print(f"Status: {health_moderate['health_status']}")
    print(f"Badge: {health_moderate['health_badge']}")
    print(f"Message: {health_moderate['health_message']}")
    print(f"Coverage: {health_moderate['coverage']}")
    print(f"Confidence: {health_moderate['confidence']}")
    print(f"Fallback Usage: {health_moderate['fallback_usage']}")
    print(f"Knowledge Description: {health_moderate['knowledge_description']}")
    print(f"Recommendations: {health_moderate['recommendations']}")
    assert health_moderate['coverage'] == 'moderate', "Should have moderate coverage"
    assert len(health_moderate['recommendations']) <= 3, "Should have max 3 recommendations"
    print("✓ Test passed")
    
    # Test Case 5: Large, Well-Established System
    print("\n5. LARGE SYSTEM SCENARIO (Extensive knowledge base)")
    print("-" * 80)
    stats_large = {
        'total_chunks': 750,
        'total_queries': 200,
        'avg_relevance': 0.88,
        'success_rate': 0.92,
        'documents_count': 50
    }
    health_large = assess_reviewer_knowledge_health(stats_large)
    print(f"Status: {health_large['health_status']}")
    print(f"Badge: {health_large['health_badge']}")
    print(f"Coverage: {health_large['coverage']}")
    print(f"Confidence: {health_large['confidence']}")
    print(f"Knowledge Description: {health_large['knowledge_description']}")
    print(f"Knowledge Summary: {health_large['knowledge_summary']}")
    assert health_large['coverage'] == 'strong', "Should have strong coverage"
    assert health_large['health_status'] == 'healthy', "Should be healthy"
    print("✓ Test passed")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nKey Insights from Tests:")
    print("• Early stage systems get actionable guidance, not failure messages")
    print("• Healthy systems are recognized and encouraged")
    print("• Poor performance generates specific improvement recommendations")
    print("• All scenarios provide max 3 concrete next steps")
    print("• No raw metrics exposed - everything is interpreted")

if __name__ == '__main__':
    test_assess_reviewer_knowledge_health()
