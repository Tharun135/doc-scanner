
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add all Python files
a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('agent', 'agent'),
        ('.env', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'spacy',
        'en_core_web_sm',
        'flask',
        'werkzeug',
        'jinja2',
        'google.generativeai',
        'langchain',
        'chromadb',
        'beautifulsoup4',
        'PyPDF2',
        'docx',
        'markdown',
        'textstat',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/favicon.ico'  # Add an icon if you have one
)
