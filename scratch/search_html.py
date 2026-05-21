import re

with open('app/templates/index.html', encoding='utf-8') as f:
    content = f.read()
    lines = content.splitlines()

# Find where the renderDocumentIntelligence function ends (line 1600)
# and where other nearby JS functions are
for func_name in ['function switchTab', 'function escHtml', 'function renderChart', 'function renderContent']:
    idx = content.find(func_name)
    if idx != -1:
        ln = content[:idx].count('\n') + 1
        print(f"'{func_name}' at line {ln}: {lines[ln-1][:80]}")

# Check around line 1600 (after renderDocumentIntelligence)
print(f"\nLines 1598-1615:")
for i, line in enumerate(lines[1597:1615], start=1598):
    try:
        print(f"{i}: {line}")
    except:
        print(f"{i}: [unicode]")
