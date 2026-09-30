#!/usr/bin/env python3
"""Copy the Save label from your OOT archives into an optional Majora's Mask mod."""
import argparse
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oot', required=True, type=Path, help='Your extracted oot.o2r')
    parser.add_argument('--hd', type=Path, help='Optional OoT Reloaded O2R archive')
    parser.add_argument('--title', type=Path, default=Path('output/PPSA99621'))
    args = parser.parse_args()
    with zipfile.ZipFile(args.oot) as archive:
        base = archive.read('textures/do_action_static/gSaveDoActionENGTex')
    hd = None
    if args.hd:
        with zipfile.ZipFile(args.hd) as archive:
            hd = archive.read('alt/textures/do_action_static/gSaveDoActionENGTex')
    mods = args.title / 'assets/mods'
    mods.mkdir(parents=True, exist_ok=True)
    target = mods / 'MM_OOT_Save_Label.o2r'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('do_action_static/gDoActionSaveENGTex', base)
        if hd is not None:
            archive.writestr('alt/do_action_static/gDoActionSaveENGTex', hd)
    manifest = mods / 'mods.txt'
    lines = manifest.read_text().splitlines() if manifest.exists() else []
    if target.name not in lines:
        lines.append(target.name)
    manifest.write_text('\n'.join(lines) + '\n')
    print(f'Created {target}; upload it and mods.txt with the game closed.')


if __name__ == '__main__':
    main()
