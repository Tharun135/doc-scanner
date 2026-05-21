import re

content = open('app/templates/index.html', encoding='utf-8').read()

start = content.find('function renderDocumentIntelligence')
end = content.find('function escHtml', start)
snippet = content[start:end]

jinja_vars = re.findall(r'\{\{[^}]*\}\}', snippet)
print('Jinja vars found in DI renderer:', jinja_vars)

# Count backticks - must be even (each template literal opens and closes)
bt = snippet.count('`')
print('Backtick count:', bt, '- even:', bt % 2 == 0)

# Find panel.innerHTML
idx = snippet.find('panel.innerHTML')
print('panel.innerHTML present:', idx > 0)

# Print the full panel.innerHTML assignment section
pi = snippet.find('panel.innerHTML =')
print('\npanel.innerHTML assignment (first 500 chars):')
print(snippet[pi:pi+500])
