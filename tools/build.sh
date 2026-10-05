#!/usr/bin/env bash
# Configure, compile and package 2 Ship 2 Harkinian for PS5.
# Output: $PS5SDK_ROOT/build/mm-pkg/dist/PPSA99621
set -euo pipefail
source "$(dirname "$0")/env.sh"

bash "$REPO/tools/apply-camera-controls.sh"

cmake -S "$MM_SOURCE" -B "$MM_BUILD" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN" \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_CROWD_CONTROL=OFF -DENABLE_SCRIPTING=OFF \
    -DDISABLE_DLL_LOADER=ON

# ImGui is fetched by CMake; patch its OpenGL3 backend for the PS5 scanout format.
imgui=$MM_BUILD/_deps/imgui-src
if ! grep -q "Out_Color.bgra" "$imgui/backends/imgui_impl_opengl3.cpp"; then
    patch -d "$imgui" -p1 < "$REPO/patches/imgui-ps5.patch"
fi

# Compile failures must stop packaging, even when stale objects exist.
python3 "$REPO/tools/compile-mm.py" "$MM_BUILD"
python3 "$REPO/tools/pack-mm.py"
