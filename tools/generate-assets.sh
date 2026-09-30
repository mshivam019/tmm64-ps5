#!/usr/bin/env bash
# Generate mm.o2r and 2ship.o2r from your own Majora's Mask ROM with a host (Linux) build of 2S2H.
# Usage: tools/generate-assets.sh /path/to/mm.z64
set -euo pipefail
source "$(dirname "$0")/env.sh"

rom=${1:?usage: generate-assets.sh /path/to/mm.z64}
host_build=$PS5SDK_ROOT/build/mm-host

destination=$MM_SOURCE/OTRExporter/mm.z64
# rom_chooser.py searches ../OTRExporter/*.z64 from mm/.
if [ -e "$destination" ]; then
    cmp -s "$rom" "$destination" || { echo "A different ROM already exists at $destination" >&2; exit 1; }
else
    cp "$rom" "$destination"
fi
sha1sum "$destination"
cmake -S "$MM_SOURCE" -B "$host_build" -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build "$host_build" --target ZAPD
cmake --build "$host_build" --target ExtractAssets
test -s "$MM_SOURCE/mm.o2r" && test -s "$MM_SOURCE/2ship.o2r"
ls -la "$MM_SOURCE"/*.o2r
