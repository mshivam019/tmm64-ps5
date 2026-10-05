#!/usr/bin/env python3
"""Update a downloaded PS5 2Ship config; close the game before downloading/uploading it."""
import argparse
import json
import time
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="existing 2ship2harkinian.json from the active UserData/sandbox")
    parser.add_argument("--hd-textures", choices=("on", "off"))
    parser.add_argument("--menu-size", choices=("small", "normal", "large", "x-large"))
    args = parser.parse_args()
    try:
        data = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("config root must be an object")
        cvars = data.setdefault("CVars", {})
        if not isinstance(cvars, dict):
            raise ValueError("CVars must be an object")
        settings = cvars.setdefault("gSettings", {})
        if not isinstance(settings, dict):
            raise ValueError("CVars.gSettings must be an object")
        settings["ControlNav"] = 1
        cvars.update(gInterpolationFPS=60, gMatchRefreshRate=0)
        if args.hd_textures:
            enhancements = cvars.setdefault("gEnhancements", {})
            if not isinstance(enhancements, dict):
                raise ValueError("CVars.gEnhancements must be an object")
            mods = enhancements.setdefault("Mods", {})
            if not isinstance(mods, dict):
                raise ValueError("CVars.gEnhancements.Mods must be an object")
            mods["AlternateAssets"] = int(args.hd_textures == "on")
        if args.menu_size:
            settings["ImGuiScale"] = {"small": 0, "normal": 1, "large": 2, "x-large": 3}[args.menu_size]
        output = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        backup = args.config.with_name(args.config.name + f".backup-{time.time_ns()}")
        shutil.copy2(args.config, backup)
        args.config.write_text(output, encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Updated {args.config}; backup: {backup}")
    print("Upload to the same active config path while the game is closed.")
    if args.hd_textures == "on":
        print("HD textures also require the archive and mods.txt; see MODS.md.")


if __name__ == "__main__":
    main()
