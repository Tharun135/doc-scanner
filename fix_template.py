"""
Surgical fix for index.html: restore the broken JS section.
"""
import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The file currently has the fetchSmartModeSuggestions try block un-closed,
# and socket = io({ directly after hint.textContent line.
# We need to:
# 1. Close fetchSmartModeSuggestions properly
# 2. Insert switchTab, escHtml, renderDocumentIntelligence
# 3. Add socket variable declarations
# 4. Keep the rest of the WebSocket init

FIND = "                if (hint) hint.textContent = `Detected: ${data.detected_type} \u2014 Suggested: ${suggested.join(', ')}`;\n\n            socket = io({"

if FIND not in content:
    # try with \r\n
    FIND = "                if (hint) hint.textContent = `Detected: ${data.detected_type} \u2014 Suggested: ${suggested.join(', ')}`;\r\n\r\n            socket = io({"

if FIND not in content:
    print("ERROR: Pattern not found. Showing chars around 'socket = io':")
    idx = content.find("socket = io({")
    print(repr(content[idx-400:idx+50]))
    exit(1)

print("Pattern found! Replacing...")

REPLACE = """                if (hint) hint.textContent = `Detected: ${data.detected_type} \u2014 Suggested: ${suggested.join(', ')}`;
            } catch (e) { /* non-fatal */ }
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.tab-button').forEach(function(b) { b.classList.remove('active'); });
            var cmap = {'feedback':'feedbackContent','doc-intel':'docIntelContent','ai-feedback':'aiFeedbackContent'};
            var bmap = {'feedback':'tabBtnSentence','doc-intel':'tabBtnDocIntel','ai-feedback':'tabBtnAI'};
            var c = document.getElementById(cmap[tabName]);
            var btn2 = document.getElementById(bmap[tabName]);
            if (c) c.classList.add('active');
            if (btn2) btn2.classList.add('active');
        }

        function escHtml(str) {
            var d = document.createElement('div');
            d.textContent = String(str || '');
            return d.innerHTML;
        }

        function renderDocumentIntelligence(di) {
            if (!di) return;
            var panel = document.getElementById('docIntelPanel');
            var empty = document.getElementById('docIntelEmpty');
            if (!panel) return;
            if (empty) empty.style.display = 'none';
            var totalIssues = di.total_issues || 0;
            var badge = document.getElementById('docIntelBadge');
            if (badge) { badge.textContent = totalIssues; badge.style.display = totalIssues > 0 ? 'inline' : 'none'; }
            var hs = di.health_score;
            var modesHtml = (di.review_modes_active || []).map(function(m) {
                return '<span class="badge me-1" style="background:#2A9BAA;font-size:0.7rem;">'+escHtml(m)+'</span>';
            }).join('');
            var dimsHtml = '';
            if (hs) {
                [['Structure',hs.structure],['Consistency',hs.consistency],['Completeness',hs.completeness],
                 ['Readability',hs.readability],['Flow',hs.flow],['Cross-Refs',hs.cross_references],['Redundancy',hs.redundancy]
                ].forEach(function(d) {
                    dimsHtml += '<div class="dim-bar-row"><div class="dim-bar-label">'+d[0]+'</div>'
                        +'<div class="dim-bar-track"><div class="dim-bar-fill" style="width:'+(d[1]||0)+'%"></div></div>'
                        +'<div class="dim-bar-score">'+(d[1]||0)+'</div></div>';
                });
            }
            var cats = [
                {key:'section_issues',label:'Section Analysis',icon:'fa-sitemap'},
                {key:'cross_reference_issues',label:'Cross-References',icon:'fa-link'},
                {key:'consistency_issues',label:'Consistency',icon:'fa-equals'},
                {key:'ia_issues',label:'Information Architecture',icon:'fa-project-diagram'},
                {key:'flow_issues',label:'Narrative Flow',icon:'fa-water'},
                {key:'completeness_issues',label:'Completeness',icon:'fa-tasks'}
            ];
            function buildCat(cat) {
                var issues = di[cat.key] || [];
                var zc = issues.length === 0 ? 'zero' : '';
                var body = '';
                issues.slice(0,5).forEach(function(issue) {
                    var sev = issue.severity||'minor';
                    body += '<div class="di-issue-item"><span class="rule-id">'+escHtml(issue.rule_id||'')+'</span> '
                        +'<span class="severity-'+sev+'">['+sev+']</span> '+escHtml(issue.message||'');
                    if (issue.suggestion) body += '<div class="text-muted mt-1" style="font-size:0.75rem;"><i class="fas fa-lightbulb me-1"></i>'+escHtml(issue.suggestion)+'</div>';
                    body += '</div>';
                });
                if (issues.length>5) body += '<div class="text-muted" style="font-size:0.75rem;padding:0.3rem 0.5rem;">+'+(issues.length-5)+' more</div>';
                return '<div class="di-category" onclick="this.classList.toggle(\'expanded\')">'
                    +'<div class="di-category-header"><span><i class="fas '+cat.icon+' me-1"></i>'+cat.label+'</span>'
                    +'<span class="di-issue-count '+zc+'">'+issues.length+'</span></div>'
                    +'<div class="di-issue-list">'+body+'</div></div>';
            }
            var sections = di.sections || [];
            var secTree = '';
            sections.slice(0,20).forEach(function(s) {
                var indent = ((s.level||1)-1)*12+8;
                var zc2 = s.issue_count===0?'zero':'';
                secTree += '<div class="di-section-item" style="padding-left:'+indent+'px">'
                    +'<span class="section-title"><span class="section-level-badge">H'+(s.level||'?')+'</span>'+escHtml(s.title||'')+'</span>'
                    +'<span class="di-issue-count '+zc2+'">'+(s.issue_count||0)+'</span></div>';
            });
            var html = '<div class="mb-2 d-flex align-items-center gap-2 flex-wrap"><span class="fw-bold" style="font-size:0.85rem;"><i class="fas fa-layer-group me-1"></i> Document Intelligence</span>'
                +modesHtml+'<span class="text-muted" style="font-size:0.75rem;">Doc type: <strong>'+escHtml(di.doc_type||'unknown')+'</strong></span></div>';
            if (hs) html += '<div class="di-category mb-2" style="border-left-color:#FFD700;"><div class="di-category-header mb-1"><span><i class="fas fa-heartbeat me-1"></i> Document Health</span><span class="health-total-badge">'+(hs.total||0)+'/100</span></div>'+dimsHtml+'</div>';
            if (secTree) html += '<div class="di-category" onclick="this.classList.toggle(\'expanded\')"><div class="di-category-header"><span><i class="fas fa-list-ul me-1"></i> Section Overview</span><span class="di-issue-count">'+sections.length+'</span></div><div class="di-issue-list di-section-tree">'+secTree+'</div></div>';
            cats.forEach(function(cat) { html += buildCat(cat); });
            panel.innerHTML = html;
        }

        let socket = null;
        let socketConnected = false;
        let currentRoomId = null;
        let isRealTimeProgress = false;

        // Initialize WebSocket with error handling
        try {
            socket = io({"""

new_content = content.replace(FIND, REPLACE, 1)

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

verify = open('app/templates/index.html', encoding='utf-8').read()
print("switchTab present:", 'function switchTab' in verify)
print("renderDocumentIntelligence present:", 'function renderDocumentIntelligence' in verify)
print("escHtml present:", 'function escHtml' in verify)
print("socket = null present:", 'let socket = null;' in verify)
print("fetchSmartModeSuggestions closed:", "} catch (e) { /* non-fatal */ }" in verify)
print("DONE. New file size:", len(verify))
