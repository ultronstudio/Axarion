
# -*- mode: python ; coding: utf-8 -*-
import os

a = Analysis(
    ['axarion_studio.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('engine', 'engine'),
        ('utils', 'utils'), 
        ('assets', 'assets'),
        ('DOCS', 'DOCS')
    ],
    hiddenimports=[
        'tkinter',
        'pygame',
        'json',
        'threading',
        'subprocess',
        'pathlib',
        'typing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AxarionStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
