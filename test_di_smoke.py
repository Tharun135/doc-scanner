from core.structural_analyzer import run_document_intelligence

sample_html = '''
<h1>Installation Guide</h1>
<p>This guide walks you through installing the OPC UA connector.</p>

<h2>Configuration</h2>
<p>Click the enable button. Select the connector. Configure the settings. Enter the host. Press apply.</p>
<ol><li>Open the UI.</li><li>Navigate to Settings.</li><li>Enable the connector.</li></ol>

<h2>Troubleshooting</h2>
<p>If the connector fails, check the error log. Delete the cache if needed.</p>

<h2>Overview</h2>
<p>OPC UA is used throughout. The dashboard and UI may vary.</p>
'''

result = run_document_intelligence(
    html_content=sample_html,
    filename='Installation_Guide.md',
    doc_type='procedure',
    review_modes=['Style', 'UX', 'Release'],
)

hs = result.get('health_score', {})
print("Health Score:")
print("  Total:", hs.get("total"), "/ 100")
print("  Structure:", hs.get("structure"))
print("  Completeness:", hs.get("completeness"))
print("  Consistency:", hs.get("consistency"))
print("  Flow:", hs.get("flow"))
print("Total issues:", result.get("total_issues"))
print("Sections found:", len(result.get("sections", [])))

print("\nSection issues:")
for i in result.get('section_issues', []):
    print(" ", i["rule_id"], i["severity"], "-", i["message"][:80])

print("\nConsistency issues:")
for i in result.get('consistency_issues', []):
    print(" ", i["rule_id"], "-", i["message"][:80])

print("\nIA issues:")
for i in result.get('ia_issues', []):
    print(" ", i["rule_id"], "-", i["message"][:80])

print("\nCompleteness issues:")
for i in result.get('completeness_issues', []):
    print(" ", i["rule_id"], i["severity"], "-", i["message"][:80])
