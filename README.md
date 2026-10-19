# Majora’s Mask: PS5 native port

**Installed from ProsperoStore?** [Use the game-specific setup](INSTALL.md#already-installed-from-prosperostore): choose your game files and an output location; it prepares and checks a ready-to-copy folder automatically. Download **PS5-Install-Helper-v1.2.0.zip** from this game's release. Python 3.9+ is required; game conversion/module preparation requirements are listed in the guide.

**[Start here: installation, USB/offline copying, Wi-Fi FTP and game-file locations](INSTALL.md).**
M.2, Ethernet and PS5 Upload are optional. The guide also explains recovery after
store updates; older packaged instructions may describe the developer's M.2 setup.

A native PS5 port of **2 Ship 2 Harkinian 5.0.1**, built on the PS5 OpenGL runtime. Companion project to [Ocarina of Time for PS5](https://github.com/mshivam019/oot64-ps5).

[Download the latest release](https://github.com/mshivam019/tmm64-ps5/releases/latest) · [Console setup](docs/CONSOLE-SETUP.md) · [Build from source](docs/BUILDING.md)

[Release v1.1.0](https://github.com/mshivam019/tmm64-ps5/releases/tag/v1.1.0) includes the tested controller menu fixes and independent camera/HD toggles, enabled by default. Saved off choices are preserved; HD archives must be installed separately. See [settings](docs/SETTINGS.md) and [mod installation](docs/MODS.md).

## Features

- 3840 × 2160 output, with a 120 Hz display request and automatic 60 Hz fallback.
- Fixed 60 FPS interpolation on PS5; display refresh is not a promise of game frame rate.
- Matched OpenGL/SDL performance improvements from the Ocarina port.
- DualSense controls and gamepad menu navigation.
- Widescreen HUD alignment by default, preserving existing custom HUD settings.
- PS5 audio playback fix for valid notes incorrectly silenced by an N64 memory-address check.
- Pause saving enabled by default, subject to the game’s safe-save restrictions.
- Optional alternate/HD assets, including MM Reloaded.
- Native title **PPSA99621**, tested on M.2 with kstuff and ShadowMountPlus; a loader-supported internal/USB location is also a deployment option. etaHEN is not required for this setup.

## Requirements

- A homebrew-capable PS5 with compatible native folder-title support and a file-copy method (USB/file manager or FTP).
- Your own supported Majora’s Mask ROM, extracted with official 2Ship 5.0.1 on your PC.
- About 200 MB of free space for the base title; about 3 GB extra for the optional MM Reloaded HD pack.
- Python 3.9+ only if using the optional file helper. Manual USB/file-manager copying or your own FTP client does not need Python.

## Installation

1. Install `PPSA99621.zip` from the release/ProsperoStore, or unpack the complete
   precompiled app folder for manual copying. No PS5 compilation is needed.
2. Let [desktop 2Ship 5.0.1](https://github.com/2ship2harkinian/2ship2harkinian/releases/tag/5.0.1) extract your supported ROM; close it and copy `mm.o2r`.
3. With the PS5 game closed, put `mm.o2r` in the installed title's `assets/`
   folder. Use USB plus your console file manager, Wi-Fi FTP, Ethernet FTP or
   your preferred copy method. Choose your loader's location; M.2 is optional.
4. For a new manual installation, refresh/mount/register the whole title folder
   with your existing loader. Start the home-screen tile.

[INSTALL.md](INSTALL.md) has exact file layouts, the optional separate prepare
and transfer helpers, storage choices and recovery after store updates.
The Windows/Linux archives contain the same PS5 application; their older
`INSTALL.txt` may describe the developer's M.2 setup. Current optional helpers
require Python 3.9+; direct copying requires neither Python nor PS5 Upload.
See [mods and controller prompts](docs/MODS.md) for optional texture packs and
[building](docs/BUILDING.md) only if you want to compile the port yourself.

**120 Hz:** the release is the `2160p120` build. It asks for 120 Hz output when the
display supports it and otherwise stays at 60 Hz. New source builds fix interpolation at **60 FPS**. Full-game frame-rate performance and 120 Hz output remain unverified.

ROMs, ROM-derived game archives, saves and texture packs are not included.

## Controls and saving

Cross is N64 A, Circle is N64 B, and Options opens pause. With pause saving enabled, press **Circle while paused** to open the save prompt. Saving is unavailable during certain cutscenes, dialogue, minigames and the opening areas before Clock Town. Existing user settings are preserved; the defaults apply only where a setting is absent.

The final label fix supports the original OOT Save lettering, including the matching HD replacement. See [Save-label setup](docs/CONSOLE-SETUP.md#matching-oot-save-label) to import it from your own OOT assets. Without that optional archive, the original Return label remains; saving still works.

## Settings and language changes

New source builds scale the port menu for TV resolution and default to Large; adjust **Settings → General → Menu Size**.

New source builds enable camera controls and HD textures / mods by default; saved off settings are preserved. HD archives still need separate installation. Press **touchpad** for the port menu; **Options** remains the game pause/save menu. New source builds show the active config folder and fix interpolation at 60 FPS. Existing v1.0.0 binaries predate the touchpad change. See [settings, language and right-stick camera controls](docs/SETTINGS.md).

2Ship 5.0.1 uses supported US assets and English text. German and Spanish are not selectable in this port. SoH’s language settings do not apply to Majora’s Mask.

## HD textures

Follow the [HD texture/mod setup guide](docs/MODS.md) for the exact **2Ship O2R HD** download, extraction, `mods.txt`, FileZilla paths, enabling alternate assets and troubleshooting. Upload both the archive and its manifest; a texture archive alone is insufficient.

## Validation and known limits

The packaged executable has booted on PS5 firmware 9.00. Startup, HD archive loading and the pause-save configuration were checked, and the user confirmed the pause-save action works; a full playthrough and every save location have not been verified. Audio improved in an on-console check after correcting the playback address filter. Regression checks cover low-address audio notes, 64-bit message storage and exhausted sample positions. Music quality and all individual effects have not been exhaustively verified. Defensive audio checks remain enabled. If an audio guard triggers, preserve the title’s `mm-adpcm-range.txt` diagnostic when reporting the problem.

On October 5, 2026, the user confirmed the updated 2Ship build was tested on PS5, including the requested controller menu navigation and camera toggle check. Both source builds and executable integrity checks passed. This confirmation does not establish performance in every scene. Earlier hardware results above refer to the released build. Save/configuration files use writable `/app0/UserData` where available, otherwise the title’s `/download0` sandbox. Preserve that data when updating; it is separate from the installed assets folder. Do not overwrite a running title.

## Build validation

Run `bash tools/check-build.sh --self-test` to test the validator, or `bash tools/check-build.sh --dir /path/to/PPSA99621` to check a complete title. Add `--release` for packages without private game data, `--update` for executable-only updates, `--variant stock` or `--variant camera-controls` to check controller provenance, and `--json` for machine-readable results. Release packaging runs these checks automatically.

## ROM used in this workspace

The retained test ROM is **Majora’s Mask (USA), NTSC-U 1.0**, 33,554,432 bytes, SHA-1 `d6133ace5afaa0882cf214cf88daba39e266c078`. It matches the pinned upstream supported hashes. This identifies the local test input; it does not establish new camera/menu gameplay validation. Extract your own supported ROM with official 2Ship 5.0.1.

## Credits and license

Thanks to Harbour Masters, libultraship contributors, the PS5 SDK/OpenGL/SDL and native-app developers, and GhostlyDark for the optional texture pack. Audio sample-boundary work incorporates the approach documented in [upstream PR #1745](https://github.com/HarbourMasters/2ship2harkinian/pull/1745).

See [LICENSE](LICENSE), [third-party notices](THIRD-PARTY-NOTICES.md), and [pinned sources](sources.lock.json). This project is not affiliated with Nintendo.
