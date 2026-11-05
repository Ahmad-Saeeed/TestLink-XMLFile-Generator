# -*- mode: python ; coding: utf-8 -*-
# Simplified, reliable PyInstaller spec for TestLinkCRXMLGen
#
# Changes that reduce VirusTotal false positives:
#   - onedir layout (no self-extracting one-file bootloader)
#   - upx=False
#   - console=False (clean GUI)

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.oxml.parser',
        'docx.oxml.table',
        'docx.oxml.text.paragraph',
        'docx.oxml.text.run',
        'docx.opc',
        'docx.opc.constants',
        'docx.opc.package',
        'docx.opc.part',
        'docx.package',
        'docx.parts',
        'docx.parts.document',
        'docx.table',
        'docx.text',
        'docx.text.paragraph',
        'docx.text.run',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'lxml.builder',
        'extract_isd',
        'build_xml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'PIL', 'Pillow',
        'cv2', 'pandas', 'sqlalchemy', 'django', 'flask',
        'IPython', 'jupyter', 'notebook', 'pytest',
        'tkinter.test', 'unittest', 'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect python-docx data files (templates etc.)
try:
    from PyInstaller.utils.hooks import collect_data_files
    a.datas += collect_data_files('docx')
except Exception:
    pass

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onedir layout – much fewer AV false positives than onefile
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # <-- required for onedir
    name='TestLinkCRXMLGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                      # never use UPX – AV trigger
    console=False,                  # pure GUI, no black console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TestLinkCRXMLGen',
)
