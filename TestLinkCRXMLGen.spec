# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for TestLinkCRXMLGen
#
# Key choices that reduce VirusTotal flags:
#   - onedir (not onefile)  → no self-extracting bootloader
#   - upx=False             → UPX packing is a known AV trigger
#   - VERSIONINFO resource  → legitimate looking metadata
#   - explicit excludes     → strips unused large packages
#   - collect python-docx / lxml properly

import sys
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct
)

# Version info shown by Windows Explorer / VirusTotal
version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 1, 0),
        prodvers=(1, 0, 1, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,          # VOS_NT_WINDOWS32
        fileType=0x1,        # VFT_APP
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable(
                "040904B0",  # US English, Unicode
                [
                    StringStruct("CompanyName", "Telecom Egypt / WE"),
                    StringStruct("FileDescription", "TestLink CR XML Generator"),
                    StringStruct("FileVersion", "1.0.1"),
                    StringStruct("InternalName", "TestLinkCRXMLGen"),
                    StringStruct("LegalCopyright", "Copyright (c) 2025"),
                    StringStruct("OriginalFilename", "TestLinkCRXMLGen.exe"),
                    StringStruct("ProductName", "TestLink CR XML Generator"),
                    StringStruct("ProductVersion", "1.0.1"),
                ],
            )
        ]),
        VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
    ],
)

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
    optimize=1,
)

# Make sure python-docx data files (templates, etc.) are collected
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
a.datas += collect_data_files('docx')
a.binaries += collect_dynamic_libs('lxml')

pyz = PYZ(a.pure)

# onedir layout – far fewer AV false positives than onefile
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # <-- onedir
    name='TestLinkCRXMLGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                  # GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_info,           # <-- VERSIONINFO resource
    icon=None,
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
