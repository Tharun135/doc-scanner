import re, sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/templates/index.html', encoding='utf-8').read()
scripts = list(re.finditer(r'<script\b[^>]*>([\s\S]*?)</script>', content))
big = scripts[3].group(1)
lines = big.split('\n')

# Print exact repr of lines 147-155 (0-indexed 146-154)
for i in range(146, 157):
    print(f'{i+1}: {repr(lines[i])}')
