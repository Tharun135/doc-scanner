from app.document_quality_reviewer import review_document_quality
import json

def test_semantic_validation():
    # A sentence that uses "login" instead of "log in" (a common technical drift)
    # or mentions a "Product X" which might not be in the knowledge base.
    document_text = """
# System Configuration
To access the dashboard, you must first login to the portal. 
The Industrial Edge Device (IED) must be connected to the DCS.
Make sure to use the TIA Portal for configuration.
    """
    
    print("🚀 Starting Review...")
    report = review_document_quality(document_text)
    
    # Check if contextual_accuracy is in the report
    if "contextual_accuracy" in report:
        print("\n✅ Contextual Accuracy check found!")
        print(f"Number of semantic issues: {len(report['contextual_accuracy'])}")
        
        for issue in report['contextual_accuracy']:
            print(f"\n--- Issue ---")
            print(f"Sentence: {issue['sentence']}")
            print(f"Problem: {issue['problem']}")
            print(f"Suggested Revision: {issue['suggested_revision']}")
    else:
        print("\n❌ Contextual Accuracy check MISSING in report.")

    print(f"\nOverall Score: {report.get('overall_score', 'N/A')}")
    print(f"Top Recommendations: {report.get('top_recommendations', [])}")

if __name__ == "__main__":
    test_semantic_validation()
