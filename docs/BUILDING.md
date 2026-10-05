# Building

This repository carries patches and build tooling. Exact upstream revisions are in `sources.lock.json`; upstream source trees are fetched separately. A Linux host with Clang/LLVM 18, CMake, Ninja, Git, Python 3, Meson, Mako, PyYAML, bison, flex and byacc is expected. Allow substantial disk space and RAM; compilation defaults to four jobs (`BUILD_JOBS` overrides this).

Prepare the pinned native-app boilerplate and its PS5 payload SDK using its upstream bootstrap instructions. Extract PS5 OpenGL SDK 0.3.0 under `$PS5SDK_ROOT/extracted/ps5-opengl-sdk-0.3.0`, and its matching source bundle under `$PS5SDK_ROOT/ps5-opengl-030/ps5-opengl`. The graphics build expects the SDK’s bundled Mesa and opengnm source archives alongside `sdk/` in `sources/`.

```sh
export PS5SDK_ROOT=/opt/ps5sdk
bash tools/setup-toolchain.sh
bash tools/build-deps.sh
bash tools/fetch-mm.sh
# Generate your private game assets using a supported ROM:
bash tools/generate-assets.sh /path/to/your/mm.z64
# Configure/compile the game objects:
bash tools/build.sh
# Rebuild matched graphics/SDL and package the 4K profile:
bash tools/build-profile.sh 2160p120
```

`setup-toolchain.sh` applies the native writer’s RELRO alignment correction. The fetch script applies the game and libultraship patches; the graphics scripts apply the runtime and SDL patches. The game uses 64-bit audio message storage, sample-end guards, PS5 frame pacing, and saving/alternate-assets defaults.

The final game link is intentionally performed by `pack-mm.py`, not the upstream CMake executable target. `compile-mm.py` builds the required objects and libraries. Set `PS5_COMPILER_RT` to your compatible `libclang_rt.builtins-x86_64.a` if Clang’s automatic resource lookup cannot locate it. Set `PS5_OPENGL_SDK` and `PS5_SDL2_PREFIX` together when using an already-built display profile.

The shipped binary was built with Clang 18 game objects, PS5 payload SDK v0.42, the SDK 0.3.0 libraries and the patched 2160p120 runtime. Toolchain bootstrap remains dependent on the upstream projects; a clean-machine end-to-end rebuild has not been verified.

Checks:
```sh
bash tools/check-build.sh --self-test
bash tools/check-build.sh --dir /path/to/PPSA99621
bash tools/check-build.sh --dir /path/to/release/PPSA99621 --release --json
python3 tools/test-audio-playback.py "$MM_SOURCE"
python3 tools/test-audio-messages.py "$MM_SOURCE"
python3 tools/test-audio-sample-end.py "$MM_SOURCE"
python3 tools/test-hud-defaults.py "$MM_SOURCE"
```

Package an existing native title without redistributing private game data:
```sh
python3 tools/release.py --from-dir /path/to/dist/PPSA99621 --version v1.1.0 --variant camera-controls
```

New builds use the default `camera-controls` feature profile; users switch camera mode off in the Mod Menu. The recorded source variant must match. This produces matching Windows/Linux archives and SHA-256 files under `dist/releases/`. It includes only an explicit list of runtime files, support assets and documentation; `mm.o2r`, mods, saves and logs are excluded.

The validator checks native executable/runtime signatures and minimum sizes, support-file presence, ZIP/O2R integrity, title metadata, display-profile consistency, optional executable checksums, and unwanted packaging leftovers. Normal mode requires your `mm.o2r`; `--release` requires it to be absent. JSON output is a single object, with exit status 1 on failure. These structural checks cannot establish gameplay stability or frame rate. Release packaging runs the validator automatically before creating each ZIP.

## Controller variants and executable updates

All new builds include camera controls and default to enabled, with HD textures / mods also enabled. Users can disable either independently in the Mod Menu, and saved choices persist. No optional patch or environment flag is needed. See [SETTINGS.md](SETTINGS.md) for binding restoration and menu navigation.

To package an executable update without copying game archives, use `python3 tools/pack-mm.py --without-game-assets --out /path/to/update`. Check its PPSA99621 folder with `bash tools/check-build.sh --update --variant camera-controls --dir /path/to/update/dist/PPSA99621`. This mode requires the recorded executable checksum and `game_assets_included=false`; normal validation still requires a complete installation.

Close the console title, keep rollback copies, and transfer the new `eboot.bin`, matching `sce_module/libc.prx` and `build-profile.json`. Preserve installed assets, title metadata, mods, UserData and saves. Compilation and archive checks are not console gameplay proof.
