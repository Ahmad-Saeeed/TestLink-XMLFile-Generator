# -*- mode: python ; coding: utf-8 -*-
# Reliable onedir PyInstaller spec for TestLinkCRXMLGen
# Compatible with PyInstaller 6.x on Windows

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
    noarchive=False,
)

# Collect python-docx data files if available
try:
    from PyInstaller.utils.hooks import collect_data_files
    a.datas += collect_data_files('docx')
except Exception:
    pass

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # onedir mode
    name='TestLinkCRXMLGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,              # pure GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TestLinkCRXMLGen',
)
