# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('fondo_issfa.png', '.'), ('fondo_iess.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RenombradorPDF',
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
    icon=['C:\\Users\\USER\\Desktop\\PRUEBA\\ICAMP 1.0.5\\tu_icono.ico'],
)
