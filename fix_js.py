"""
Fix the broken secTree JS section in index.html.
Replace the deeply-nested escaped inline handlers with clean data-attribute versions.
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'app/templates/index.html'
content = open(path, encoding='utf-8').read()

# The broken block spans lines 1655-1665 in the file.
# We search for the secTree forEach block and replace it.
old = (
    "            sections.slice(0,20).forEach(function(s) {\r\n"
    "                var indent = ((s.level||1)-1)*12+8;\r\n"
    "                var zc2 = s.issue_count===0?'zero':'';\r\n"
    "                var sTitle = s.title || '';\r\n"
    "                secTree += '<div class=\"di-section-item\" style=\"padding-left:'+indent+'px;cursor:pointer;\"'\r\n"
    "                    +' onclick=\"highlightDITerm(\\''+escHtml(sTitle).replace(/'/g,\"\\\\'\")+'\\')\"\r\n"
    "                    +' onmouseenter=\"highlightDIHoverTerm(\\''+escHtml(sTitle).replace(/'/g,\"\\\\'\")+'\\')\"\r\n"
    "                    +' onmouseleave=\"restoreDIActiveHighlightGlobal()\">'\r\n"
    "                    +'<span class=\"section-title\"><span class=\"section-level-badge\">H'+(s.level||'?')+'</span>'+escHtml(sTitle)+'</span>'\r\n"
    "                    +'<span class=\"di-issue-count '+zc2+'\">'+( s.issue_count||0)+'</span></div>';\r\n"
    "            });\r\n"
)

new = (
    "            sections.slice(0,20).forEach(function(s) {\r\n"
    "                var indent = ((s.level||1)-1)*12+8;\r\n"
    "                var zc2 = s.issue_count===0?'zero':'';\r\n"
    "                var sTitle = s.title || '';\r\n"
    "                var secDiv = document.createElement('div');\r\n"
    "                secDiv.className = 'di-section-item';\r\n"
    "                secDiv.style.paddingLeft = indent+'px';\r\n"
    "                secDiv.style.cursor = 'pointer';\r\n"
    "                secDiv.setAttribute('data-di-term', sTitle);\r\n"
    "                secDiv.innerHTML = '<span class=\"section-title\"><span class=\"section-level-badge\">H'+(s.level||'?')+'</span>'+escHtml(sTitle)+'</span>'\r\n"
    "                    +'<span class=\"di-issue-count '+zc2+'\">'+(s.issue_count||0)+'</span>';\r\n"
    "                secDiv.onclick = function(){ highlightDITerm(this.getAttribute('data-di-term')); };\r\n"
    "                secDiv.onmouseenter = function(){ highlightDIHoverTerm(this.getAttribute('data-di-term')); };\r\n"
    "                secDiv.onmouseleave = restoreDIActiveHighlightGlobal;\r\n"
    "                secTree += secDiv.outerHTML;\r\n"
    "            });\r\n"
)

# Check if old is present — may differ in whitespace/encoding
if old in content:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print('SUCCESS: replaced secTree block')
else:
    print('ERROR: old block not found, trying line-based approach')
    # Fall back: find by unique anchor strings
    anchor_start = "sections.slice(0,20).forEach(function(s) {"
    anchor_end = "            });"  # line after the secTree loop closes
    
    # Find positions
    idx_start = content.find(anchor_start)
    if idx_start == -1:
        print('anchor_start not found')
        sys.exit(1)
    # Find the closing }) after this
    idx_end = content.find(anchor_end, idx_start)
    if idx_end == -1:
        print('anchor_end not found')
        sys.exit(1)
    idx_end += len(anchor_end)
    
    print(f'Found block at chars {idx_start}-{idx_end}')
    print('Existing block:')
    print(repr(content[idx_start:idx_end]))
