# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path(SPECPATH).resolve()

APPS = [
    ("lab_1", "lab_1/main.py", "lab_1"),
    ("lab_3_part_1", "lab_3_part_1/main.py", "lab_3_part_1"),
    ("lab_3_part_2", "lab_3_part_2/main.py", "lab_3_part_2"),
    ("lab_4", "lab_4/main.py", "lab_4"),
    ("lab_6", "lab_6/main.py", "lab_6"),
    ("lab_7", "lab_7/main.py", "lab_7"),
]


def unique_toc_entries(*tocs):
    seen = set()
    result = []
    for toc in tocs:
        for entry in toc:
            destination, source, typecode = entry[:3]
            if destination in seen:
                continue
            seen.add(destination)
            result.append((destination, source, typecode))
    return result


analyses = []
executables = []

for app_name, script, import_dir in APPS:
    analysis = Analysis(
        [str(ROOT / script)],
        pathex=[str(ROOT / import_dir)],
        binaries=[],
        datas=[],
        hiddenimports=[],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        noarchive=False,
        optimize=0,
    )
    pyz = PYZ(analysis.pure)
    exe = EXE(
        pyz,
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        contents_directory="_internal",
    )
    analyses.append(analysis)
    executables.append(exe)


shared_files = unique_toc_entries(
    *(analysis.binaries for analysis in analyses),
    *(analysis.datas for analysis in analyses),
)

coll = COLLECT(
    *executables,
    shared_files,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="uust_oop_gui",
)
