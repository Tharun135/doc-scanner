import os
import re

path = 'app/templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Specifically targeting the block that was breaking the JS parser
pattern = r"sections\.slice\(0,20\)\.forEach\(function\(s\) \{(?:.|\n|\r)*?secTree \+=.*?\}\);"

replacement = """sections.slice(0,20).forEach(function(s) {
                var indent = ((s.level||1)-1)*12+8;
                var zc2 = s.issue_count===0?'zero':'';
                var sTitle = s.title || '';
                var secDiv = document.createElement('div');
                secDiv.className = 'di-section-item';
                secDiv.style.paddingLeft = indent+'px';
                secDiv.style.cursor = 'pointer';
                secDiv.setAttribute('data-di-term', sTitle);
                secDiv.innerHTML = '<span class="section-title"><span class="section-level-badge">H'+(s.level||'?')+'</span>'+escHtml(sTitle)+'</span>'
                    +'<span class="di-issue-count '+zc2+'">'+(s.issue_count||0)+'</span>';
                secDiv.onclick = function(){ highlightDITerm(this.getAttribute('data-di-term')); };
                secDiv.onmouseenter = function(){ highlightDIHoverTerm(this.getAttribute('data-di-term')); };
                secDiv.onmouseleave = restoreDIActiveHighlightGlobal;
                secTree += secDiv.outerHTML;
            });"""

new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

if new_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: Fixed secTree syntax error.")
else:
    print("ERROR: Pattern not found.")
