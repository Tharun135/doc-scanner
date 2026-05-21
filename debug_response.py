"""
Quick diagnostic: simulate what the browser JS does with the actual API response.
Run after uploading the user's document (credentials-for-databus-common-configurator.md).
"""
from core.structural_analyzer import run_document_intelligence
import json

# Simulate the same document type and modes from the screenshot
sample_html = """
<h1>Connection to Databus (Common Configurator)</h1>

<h2>Description</h2>
<p>To publish the Ethernet IP data in Databus, you must enter the credentials appropriately in Common Configurator.</p>

<h2>Procedure</h2>
<p>To enter the credentials, follow these steps:</p>
<ol>
  <li>Open the Settings > Databus Credentials tab.</li>
  <li>Enter the Databus service name, e.g. ie-databus.999.</li>
  <li>In the Data Publisher Settings tab, enter the corresponding credentials:</li>
</ol>
"""

result = run_document_intelligence(
    html_content=sample_html,
    filename='credentials-for-databus-common-configurator.md',
    doc_type='procedure',
    review_modes=['Style', 'UX', 'Release'],
)

print("=== API response structure ===")
print(json.dumps(result, indent=2, default=str))
