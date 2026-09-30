#!/usr/bin/env bash
# Check out 2 Ship 2 Harkinian 5.0.1 with submodules and apply the PS5 patches.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ ! -d "$MM_SOURCE/.git" ]; then
    git clone -q "$(lock "['2ship2harkinian']['url']")" "$MM_SOURCE"
fi
cd "$MM_SOURCE"
git -c advice.detachedHead=false checkout -q "$(lock "['2ship2harkinian']['revision']")"
git submodule update --init --recursive -q
git -C libultraship -c advice.detachedHead=false checkout -q "$(lock "['libultraship']['revision']")"

apply_patch() {
    local directory=$1 patchfile=$2
    if git -C "$directory" apply --check "$patchfile" 2>/dev/null; then
        git -C "$directory" apply "$patchfile"
    else
        git -C "$directory" apply --reverse --check "$patchfile"
    fi
}
apply_patch "$MM_SOURCE" "$REPO/patches/2ship2harkinian-ps5.patch"
apply_patch "$MM_SOURCE/libultraship" "$REPO/patches/libultraship-ps5.patch"
echo "2 Ship 2 Harkinian ready at $MM_SOURCE"
