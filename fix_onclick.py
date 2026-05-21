"""
Fix the unescaped single quotes in onclick attributes inside JS string literals.
"""
with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The broken patterns: single quotes around 'expanded' inside a JS string
# Replace with properly escaped versions
# Find the buildCat function and fix its return statements

BROKEN1 = """return '<div class="di-category" onclick="this.classList.toggle('expanded')">'"""
FIXED1  = """return '<div class="di-category" onclick="this.classList.toggle(\\\'expanded\\\')">'"""

# Actually let's just use a different approach: use double-quoted outer strings
# and avoid the escaping problem entirely by switching to different quote styles

# Pattern 1: buildCat return
OLD1 = "return '<div class=\"di-category\" onclick=\"this.classList.toggle(\\'expanded\\')\">'"
NEW1 = 'return "<div class=\\"di-category\\" onclick=\\"this.classList.toggle(\'expanded\')\\">"'

# Actually the simplest fix: use HTML entities or different attribute quotes
# Let's just find the two broken occurrences and fix them

count = content.count("this.classList.toggle('expanded')")
print(f"Found {count} occurrences of toggle('expanded')")

# Fix: replace onclick with a data attribute approach or just use double-quotes for onclick value
# Simplest: use &apos; won't work in HTML either. 
# Best: use double quotes for the HTML attribute, single quotes for the JS
# onclick='this.classList.toggle("expanded")' -- this works!

OLD = """this.classList.toggle('expanded')"""
NEW = """this.classList.toggle(&quot;expanded&quot;)"""

# Wait, that's not right either. Let me think...
# The JS string is single-quoted. Inside it, we have HTML.
# The HTML has onclick="" (double quoted). Inside onclick we want JS.
# Solution: use event handler with no quotes needed, or use a function call
# 
# Actually simplest fix: just change single quote strings to double quote strings for those lines
# OR: separate the onclick into a named function

# Replace all toggle('expanded') in the JS strings with a version that works
# Use: onclick="toggleExpand(this)"  -- and define that function once

# First, add the helper function
HELPER = """
        function toggleExpand(el) { el.classList.toggle('expanded'); }

        // ── Document Intelligence Panel Renderer"""

if 'function toggleExpand' not in content:
    content = content.replace(
        '        // ── Document Intelligence Panel Renderer',
        HELPER,
        1
    )
    print("Added toggleExpand helper")

# Now replace all the broken onclick patterns
content = content.replace(
    """'<div class="di-category" onclick="this.classList.toggle(\'expanded\')">'""",
    """'<div class="di-category" onclick="toggleExpand(this)">'"""
)
content = content.replace(
    """'<div class="di-category" onclick="this.classList.toggle(\'expanded\')"><div class="di-cat""",
    """'<div class="di-category" onclick="toggleExpand(this)"><div class="di-cat"""
)

# Also fix secTree versions
content = content.replace(
    "html += '<div class=\"di-category\" onclick=\"this.classList.toggle(\\'expanded\\')\">",
    "html += '<div class=\"di-category\" onclick=\"toggleExpand(this)\">",
)

# Check what we have now
broken = content.count("toggle('expanded')")
print(f"Remaining broken patterns: {broken}")

# Direct string search
import re
# Find all JS onclick patterns that might be broken
matches = list(re.finditer(r"toggle\('expanded'\)", content))
print(f"Regex matches for toggle('expanded'): {len(matches)}")
for m in matches:
    ctx = content[max(0,m.start()-100):m.end()+20]
    print("  Context:", repr(ctx[-60:]))

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("File written.")

# Final syntax check
import subprocess
result = subprocess.run(
    ['node', '-e', '''
var fs = require('fs');
var html = fs.readFileSync('app/templates/index.html', 'utf8');
var start = html.indexOf('<script>');
var end = html.indexOf('</script>', start);
var js = html.substring(start+8, end);
try { new Function(js); console.log("SYNTAX OK"); }
catch(e) { console.log("SYNTAX ERROR:", e.message); }
'''],
    capture_output=True, text=True, cwd='.'
)
print(result.stdout)
print(result.stderr)
