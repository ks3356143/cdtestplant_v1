# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=['E:\\PycharmProject\\cdtestplant_v1'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.staticfiles',
        'ninja',
        'ninja_extra',
        'ninja_jwt',
        'tinymce',
        'celery',
        'apps.user',
        'apps.dict',
        'apps.project',
        'apps.createDocument',
        'apps.createDocument.controllers',
        'apps.createDocument.extensions',
        'apps.createDocument.schema',
        'apps.createSeiTaiDocument',
        'apps.project.controllers',
        'apps.project.schemas',
        'apps.project.tools',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    upx=True,
    upx_exclude=[],
    name='run',
)