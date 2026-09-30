#!/usr/bin/env python3
"""Package a native title as Windows/Linux releases, excluding private game data."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import shutil
import zipfile
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-dir', required=True, type=Path)
    p.add_argument('--version', default='v1.0.0')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    if not a.version or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_' for c in a.version):
        p.error('Version must be a filename-safe tag')
    repo = Path(__file__).resolve().parents[1]
    out = a.out or repo / 'dist/releases'
    out.mkdir(parents=True, exist_ok=True)
    required = ['eboot.bin', 'sce_module/libc.prx', 'sce_sys/param.json',
                'sce_sys/icon0.png', 'sce_sys/pic0.dds', 'sce_sys/pic1.dds',
                'assets/2ship.o2r', 'assets/gamecontrollerdb.txt']
    for name in required:
        if not (a.from_dir/name).is_file():
            p.error('Missing required file: '+name)
    profile = json.loads((a.from_dir/'build-profile.json').read_text())
    if profile['display_profile'] != {'width':3840,'height':2160,'fps':120}:
        p.error('Expected 2160p120 display profile')
    for platform, ext in [('windows','ps1'), ('linux','sh')]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            title = root/'output/PPSA99621'
            for name in required:
                dest = title/name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(a.from_dir/name, dest)
            # Preserve useful provenance without embedding the build host's paths.
            receipt = {k:profile[k] for k in ['display_profile','runtime_sha256']}
            receipt['default_interpolation_fps'] = 60
            receipt['eboot_sha256'] = hashlib.sha256((title/'eboot.bin').read_bytes()).hexdigest()
            (title/'build-profile.json').write_text(json.dumps(receipt,indent=2)+'\n')
            subprocess.run(['bash', str(repo/'tools/check-build.sh'), '--dir', str(title), '--release'], check=True)
            (root/'tools').mkdir()
            shutil.copy2(repo/'tools/check-build.sh', root/'tools/check-build.sh')
            shutil.copy2(repo/f'tools/install.{ext}',root/f'tools/install.{ext}')
            shutil.copy2(repo/'tools/import-save-label.py', root/'tools/import-save-label.py')
            for name in ['README.md','LICENSE','THIRD-PARTY-NOTICES.md','sources.lock.json']:
                shutil.copy2(repo/name,root/name)
            shutil.copytree(repo/'docs',root/'docs')
            (root/'INSTALL.txt').write_text((repo/'docs/CONSOLE-SETUP.md').read_text())
            archive = out/f'tmm-ps5-2160p120-{a.version}-{platform}.zip'
            with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
                for file in sorted(root.rglob('*')):
                    if file.is_file():z.write(file,file.relative_to(root))
            with zipfile.ZipFile(archive) as z:
                assert z.testzip() is None
                assert not any(Path(n).name == 'mm.o2r' or '/mods/' in n for n in z.namelist())
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            archive.with_suffix(archive.suffix+'.sha256').write_text(f'{digest}  {archive.name}\n')
            print(archive)


if __name__ == '__main__':
    main()
