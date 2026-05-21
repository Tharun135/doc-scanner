"""
Quick test: run document intelligence on a sample doc and inspect the output
"""
import sys
sys.path.insert(0, '.')

# Minimal HTML doc for testing
html = """
<h1>Connection to Databus (Common Configurator)</h1>
<h2>Description</h2>
<p>To publish the Ethernet IP data in Databus, you must enter the credentials appropriately in Common Configurator.</p>
<h2>Procedure</h2>
<p>To enter the credentials, follow these steps:</p>
<ol>
<li>Open the Settings > Databus Credentials tab.</li>
<li>Enter the Databus service name, e.g. ie-databus:1883.</li>
<li>In the Data Publisher Settings tab, enter the corresponding credentials.</li>
</ol>
"""

from core.structural_analyzer import run_document_intelligence
result = run_document_intelligence(
    html_content=html,
    filename="credentials-for-databus-common-configurator.md",
    doc_type="procedure",
    review_modes=["Style", "UX", "Release"],
    sentence_data=[],
    use_llm=False,
)

print("=== Document Intelligence Result ===")
print(f"total_issues: {result['total_issues']}")
print(f"doc_type: {result['doc_type']}")
print(f"review_modes_active: {result['review_modes_active']}")
print(f"health_score: {result['health_score']}")
print(f"\nSections ({len(result['sections'])}):")
for s in result['sections']:
    print(f"  {s}")
print(f"\nsection_issues ({len(result['section_issues'])}):")
for i in result['section_issues']:
    print(f"  {i}")
print(f"\ncross_reference_issues ({len(result['cross_reference_issues'])}):")
for i in result['cross_reference_issues']:
    print(f"  {i}")
print(f"\nconsistency_issues ({len(result['consistency_issues'])}):")
for i in result['consistency_issues']:
    print(f"  {i}")
print(f"\nia_issues ({len(result['ia_issues'])}):")
for i in result['ia_issues']:
    print(f"  {i}")
print(f"\nflow_issues ({len(result['flow_issues'])}):")
for i in result['flow_issues']:
    print(f"  {i}")
print(f"\ncompleteness_issues ({len(result['completeness_issues'])}):")
for i in result['completeness_issues']:
    print(f"  {i}")
