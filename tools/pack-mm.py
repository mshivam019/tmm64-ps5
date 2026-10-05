#!/usr/bin/env python3
"""Link the PS5 2 Ship 2 Harkinian build into a native title folder.

Reuses the ps5-native-app-boilerplate pipeline the same way ps5-opengl's
integration/SDL2/folder.py does, but links every 2Ship object directly (2Ship relies on
static initialisers, which an archive link would drop) and ships the .o2r assets.

Run in WSL after `ninja mm/2ship` has compiled everything (the CMake link step itself is
expected to fail; the real link happens here).
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("PS5SDK_ROOT", "/opt/ps5sdk"))
TEMPLATE = Path(os.environ.get("PS5_NATIVE_APP_TEMPLATE", ROOT / "native-app-boilerplate"))
GL_ROOT = Path(os.environ.get("PS5_OPENGL_ROOT", ROOT / "ps5-opengl-030/ps5-opengl"))
GL_PREFIX = Path(os.environ.get("PS5_OPENGL_SDK", ROOT / "extracted/ps5-opengl-sdk-0.3.0/sdk"))
SDL_PREFIX = Path(os.environ.get("PS5_SDL2_PREFIX", GL_ROOT / "build/sdl2-native/sdk"))
BUILD = Path(os.environ.get("MM_BUILD", ROOT / "build/mm-ps5"))
SOURCE = Path(os.environ.get("MM_SOURCE", ROOT / "src/2ship2harkinian"))
ART = REPO / "ps5/art"

TITLE_ID = "PPSA99621"
TITLE_NAME = "2 Ship 2 Harkinian"
CONTENT_ID = f"UP9000-{TITLE_ID}_00-2SHIP2HARKINIAN0"
SYSTEM_IMPORTS = ("libScePad.so", "libSceUserService.so", "libSceSystemService.so",
                  "libSceAudioOut.so", "libSceVideoOut.so")


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def replace_once(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"template contract changed: {path}: {old!r}")
    path.write_text(text.replace(old, new))


def link_inputs():
    """Objects and libraries from the CMake link statement for the 2ship executable."""
    ninja = (BUILD / "build.ninja").read_text()
    match = re.search(r"^build (mm/2ship[^:]*): CXX_EXECUTABLE_LINKER__2ship_\w+ (.*?)(?: \|\| .*)?$"
                      r"((?:\n  .*)*)", ninja, re.M)
    if not match:
        raise SystemExit("2ship link statement not found in build.ninja")
    explicit = match.group(2).split(" | ")[0]
    objects = [BUILD / p.replace("$ ", " ") for p in explicit.split()]
    libs_line = re.search(r"^  LINK_LIBRARIES = (.*)$", match.group(3), re.M).group(1)
    libraries = []
    for token in shlex.split(libs_line):
        path = Path(token) if token.startswith("/") else BUILD / token
        # The GL runtime is linked explicitly from GL_PREFIX below.
        if path.name.startswith("libPS5OpenGL") or path.name == "libSDL2.a":
            continue
        if token.endswith((".a", ".o")) and path.is_file():
            libraries.append(path)
    return objects, libraries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/mm-pkg")
    parser.add_argument("--heap-mib", type=int, default=2048,
                        help="app heap reserved from direct memory (default 2048)")
    parser.add_argument("--without-game-assets", action="store_true", help="executable update; preserve installed assets")
    args = parser.parse_args()
    profile_path = GL_PREFIX / "share/soh-build-profile.json"
    profile = json.loads(profile_path.read_text()) if profile_path.exists() else None
    if profile:
        receipt = json.loads((SDL_PREFIX / "share/SDL2/receipt.json").read_text())
        if receipt.get("display_profile") != profile["display_profile"]:
            raise SystemExit("SDL and GL display profiles do not match")
    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for directory in ("runtime", "sce_sys", "tooling", "tools", ".deps/native"):
        shutil.copytree(TEMPLATE / directory, out / directory)
    sdk = out / ".deps/native/ps5-payload-sdk"
    for directory in ("src", "vendor", "assets"):
        (out / directory).mkdir(parents=True, exist_ok=True)

    # Runtime shims + heap wrapper from ps5-opengl, with a larger heap for 2Ship.
    shutil.copy2(GL_ROOT / "native-app/runtime_shims.c", out / "src/runtime_shims.c")
    shutil.copy2(REPO / "ps5/src/ps5_libc_shims.c", out / "src/ps5_libc_shims.c")
    heap = (GL_ROOT / "native-app/app_heap.c").read_text()
    old = "#define PS5_OPENGL_HEAP_SIZE (128u * 1024u * 1024u)"
    if heap.count(old) != 1:
        raise SystemExit("app_heap.c contract changed")
    heap = heap.replace(old, f"#define PS5_OPENGL_HEAP_SIZE ((size_t){args.heap_mib}u * 1024u * 1024u)")
    # Game titles get little flexible (mmap) memory; back the heap with direct memory,
    # the same way the GL runtime maps its own buffers (type 12, CPU+GPU RW).
    old_map = ("  void *base = mmap(NULL, PS5_OPENGL_HEAP_SIZE, PROT_READ | PROT_WRITE,\n"
               "                    MAP_PRIVATE | MAP_ANON, -1, 0);\n"
               "  if (base == MAP_FAILED) {\n")
    new_map = ("  void *base = ps5_heap_map_direct(PS5_OPENGL_HEAP_SIZE);\n"
               "  if (base == NULL) {\n")
    helper = ("int64_t sceKernelGetDirectMemorySize(void);\n"
              "int32_t sceKernelAllocateDirectMemory(int64_t, int64_t, size_t, size_t, int, int64_t *);\n"
              "int32_t sceKernelMapDirectMemory(void **, size_t, int, int, int64_t, size_t);\n\n"
              "static void *ps5_heap_map_direct(size_t size) {\n"
              "  int64_t start = 0;\n"
              "  void *base = NULL;\n"
              "  if (sceKernelAllocateDirectMemory(0, sceKernelGetDirectMemorySize(), size, 0x200000,\n"
              "                                    12, &start) != 0)\n"
              "    return NULL;\n"
              "  if (sceKernelMapDirectMemory(&base, size, 0x33, 0, start, 0x200000) != 0)\n"
              "    return NULL;\n"
              "  return base;\n"
              "}\n\n"
              "static int ps5_heap_ready(void) {\n")
    if heap.count(old_map) != 1 or heap.count("static int ps5_heap_ready(void) {\n") != 1:
        raise SystemExit("app_heap.c mapping contract changed")
    heap = heap.replace(old_map, new_map).replace("static int ps5_heap_ready(void) {\n", helper)
    (out / "src/app_heap.c").write_text(heap)
    shutil.copy2(out / "tooling/native/ps5-pie.ld", out / "tooling/native/ps5-pie-base.ld")
    for name in ("ps5-pie.ld", "app-symbols.map"):
        shutil.copy2(GL_ROOT / "native-app" / name, out / "tooling/native" / name)

    # Title metadata and launcher art.
    param = json.loads((GL_ROOT / "native-app/param.json").read_text())
    param.update(titleId=TITLE_ID, conceptId=TITLE_ID[4:], contentId=CONTENT_ID,
                 downloadDataSize=1024)
    language = param["localizedParameters"]["defaultLanguage"]
    param["localizedParameters"][language]["titleName"] = TITLE_NAME
    (out / "sce_sys/param.json").write_text(json.dumps(param, indent=2) + "\n")
    for name in ("icon0.png", "pic0.dds", "pic1.dds"):
        shutil.copy2(ART / name, out / "sce_sys" / name)
    # The template's home-screen preview sound is a test tone, not game audio.
    (out / "sce_sys/snd0.at9").unlink(missing_ok=True)

    # Game data (read-only, /app0/assets on the console).
    for name in (() if args.without_game_assets else ("mm.o2r", "2ship.o2r")):
        shutil.copy2(SOURCE / name, out / "assets" / name)
    shutil.copy2(BUILD / "gamecontrollerdb.txt", out / "assets/gamecontrollerdb.txt")

    replace_once(out / "tooling/native/sce_module_writer.cpp",
                 "write_u64(result.data, result.heap_size, std::numeric_limits<std::uint64_t>::max());",
                 "write_u64(result.data, result.heap_size, 0x10000000ULL);")
    script = out / "tools/build.sh"
    replace_once(script, 'bash "$root/tools/setup-native-dependencies.sh" >/dev/null',
                 'test -x "$root/.deps/native/ps5-payload-sdk/bin/prospero-lld"')
    replace_once(script, '[[ -f $root/runtime/libc.prx ]] || bash "$root/tools/rebuild-libc.sh"',
                 'test -f "$root/runtime/libc.prx"')
    replace_once(script, "--eh-frame-hdr \\",
                 "--eh-frame-hdr --error-limit=0 --wrap=malloc --wrap=calloc --wrap=realloc --wrap=free "
                 "--wrap=posix_memalign --wrap=malloc_usable_size \\")

    for name in ("libSceAgc.so", "libSceAgcDriver.so"):
        shutil.copy2(GL_PREFIX / "lib" / name, sdk / "target/lib" / name)
    # build.sh links every stub with --as-needed; the WebKit POSIX module is not loaded
    # for game titles, so anything bound to it would be null at runtime.
    (sdk / "target/lib/libScePosixForWebKit.so").unlink()
    compiler_rt = Path(os.environ["PS5_COMPILER_RT"]) if "PS5_COMPILER_RT" in os.environ else (
        Path(run("clang-18", "--print-resource-dir", capture_output=True,
                 text=True).stdout.strip()) / "lib/linux/libclang_rt.builtins-x86_64.a")

    objects, libraries = link_inputs()
    inputs = objects + libraries
    inputs += [SDL_PREFIX / "lib/libSDL2.a", GL_PREFIX / "lib/libPS5OpenGLCore33.a"]
    inputs += [sdk / "target/lib" / name for name in SYSTEM_IMPORTS]
    inputs += [sdk / f"target/lib/{name}" for name in ("libunwind.a", "libc++abi.a", "libc++.a")]
    inputs += [compiler_rt]
    missing = [p for p in inputs if not p.is_file()]
    if missing:
        raise SystemExit("missing link inputs:\n" + "\n".join(map(str, missing[:20])))
    print(f"link: {len(objects)} objects, {len(inputs) - len(objects)} libraries")
    group = (f'SEARCH_DIR("{sdk}/target/lib")\nSEARCH_DIR("{GL_PREFIX}/lib")\n'
             'EXTERN(ps5_agc_gate2_run)\nGROUP (\n' +
             "".join(f'  "{p}"\n' for p in inputs) + ')\n')
    (out / "vendor/lib2ship.a").write_text(group)

    env = os.environ.copy()
    env["PS5_PAYLOAD_SDK"] = str(sdk)
    env["APP_STATIC_ARCHIVES"] = "vendor/lib2ship.a"
    for key in ("APP_DEFINITIONS", "APP_INCLUDE_PATHS", "PACBREW_PACKAGES",
                "PACBREW_INCLUDE_PATHS", "PACBREW_STATIC_ARCHIVES", "APP_RUNTIME_MODULES"):
        env[key] = ""
    run("bash", script, "Folder", env=env, cwd=out)
    needed = run(shutil.which("llvm-readelf-18") or "llvm-readelf", "-d", out / "build/llvm-pie.elf",
                 capture_output=True, text=True).stdout
    if "PosixForWebKit" in needed:
        raise SystemExit("eboot still imports libScePosixForWebKit")
    app = out / "dist" / TITLE_ID
    profile = dict(profile or {})
    profile.update({"controls_variant": "camera-controls" if (SOURCE / "mm/2s2h/Enhancements/Camera/PS5CameraProfile.h").exists() else "stock",
                    "game_assets_included": not args.without_game_assets,
                    "eboot_sha256": hashlib.sha256((app / "eboot.bin").read_bytes()).hexdigest(),
                    "default_interpolation_fps": 60})
    if profile:
        (app / "build-profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    print(f"2 Ship 2 Harkinian title folder: {app}")


if __name__ == "__main__":
    main()
