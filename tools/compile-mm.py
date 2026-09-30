#!/usr/bin/env python3
"""Build 2 Ship 2 Harkinian's objects and libraries without CMake's unsupported PS5 final link."""
import argparse
import os
import subprocess
from pathlib import Path


def link_dependencies(query):
    dependencies = []
    in_inputs = False
    for line in query.splitlines():
        if line.startswith("  input:"):
            in_inputs = True
        elif line.startswith("  outputs:"):
            break
        elif in_inputs and line.startswith("    "):
            path = line.strip().lstrip("| ")
            if path.endswith((".o", ".a")):
                dependencies.append(path)
    if not dependencies:
        raise ValueError("No objects or archives in 2ship's Ninja link dependencies")
    return list(dict.fromkeys(dependencies))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    query = subprocess.check_output(["ninja", "-C", str(args.build), "-t", "query", "mm/2ship"], text=True)
    dependencies = link_dependencies(query)
    command = ["ninja", "-C", str(args.build), "-j", os.environ.get("BUILD_JOBS", "4")]
    if args.dry_run:
        command.append("-n")
    print(f"Building {len(dependencies)} 2Ship link dependencies", flush=True)
    subprocess.run(command + dependencies, check=True)


if __name__ == "__main__":
    main()
