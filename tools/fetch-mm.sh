#!/usr/bin/env bash
# Check out 2 Ship 2 Harkinian 5.0.1 with submodules and apply the PS5 patches.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if (( $# > 1 )); then echo "usage: $0 [--camera-controls]" >&2; exit 2; fi
case "${1:-}" in
    "") export MM_CAMERA_CONTROLS=0 ;;
    --camera-controls) export MM_CAMERA_CONTROLS=1 ;;
    *) echo "usage: $0 [--camera-controls]" >&2; exit 2 ;;
esac

if [ ! -d "$MM_SOURCE/.git" ]; then
    git clone -q "$(lock "['2ship2harkinian']['url']")" "$MM_SOURCE"
fi
cd "$MM_SOURCE"
# Remove the optional overlay before checking the base patch on repeated fetches.
if git apply --reverse --check "$REPO/patches/2ship2harkinian-camera-controls.patch" >/dev/null 2>&1; then
    git apply --reverse "$REPO/patches/2ship2harkinian-camera-controls.patch"
fi
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
bash "$REPO/tools/apply-camera-controls.sh"
echo "2 Ship 2 Harkinian ready at $MM_SOURCE"
