# Majora’s Mask: PS5 native port

A native PS5 port of **2 Ship 2 Harkinian 5.0.1**, built on the PS5 OpenGL runtime. Companion project to [Ocarina of Time for PS5](https://github.com/mshivam019/oot64-ps5).

[Download the latest release](https://github.com/mshivam019/tmm64-ps5/releases/latest) · [Console setup](docs/CONSOLE-SETUP.md) · [Build from source](docs/BUILDING.md)

## Features

- 3840 × 2160 output, with a 120 Hz display request and automatic 60 Hz fallback.
- 60 FPS interpolation by default; display refresh is not a promise of game frame rate.
- Matched OpenGL/SDL performance improvements from the Ocarina port.
- DualSense controls and gamepad menu navigation.
- Widescreen HUD alignment by default, preserving existing custom HUD settings.
- PS5 audio playback fix for valid notes incorrectly silenced by an N64 memory-address check.
- Pause saving enabled by default, subject to the game’s safe-save restrictions.
- Optional alternate/HD assets, including MM Reloaded.
- Native title **PPSA99621**, installed on the M.2 drive with kstuff and ShadowMountPlus. etaHEN is not required for this setup.

## Requirements

- A homebrew-capable PS5 with kstuff, ShadowMountPlus and an active FTP server.
- Your own supported Majora’s Mask ROM, extracted with official 2Ship 5.0.1 on your PC.
- About 200 MB of free space for the base title; about 3 GB extra for the optional MM Reloaded HD pack.
- Windows PowerShell with `curl.exe`, or Linux with Bash and `curl`, for the optional upload helper. Any FTP client also works.

## Installation

From a [release](https://github.com/mshivam019/tmm64-ps5/releases), with no compiling:

1. Download the archive for your PC (`-windows.zip` or `-linux.zip`), extract it
   and open a terminal in the extracted folder.
2. Create `mm.o2r` from your own ROM with the official
   [2 Ship 2 Harkinian 5.0.1](https://github.com/HarbourMasters/2ship2harkinian/releases/tag/5.0.1)
   PC build and put it in `output/PPSA99621/assets/` (the archive already includes
   `2ship.o2r`). Close the desktop game after extraction finishes.
3. Get the `output/PPSA99621` folder onto the console, e.g. at
   `/mnt/ext1/etaHEN/games/PPSA99621`, and register/mount it with ShadowMountPlus.
   Use whatever you already use (any FTP client such as FileZilla or WinSCP,
   PS5Upload, …); the `install` helpers below are optional.
4. Start **2 Ship 2 Harkinian** from the home screen.

**Windows** (PowerShell; register/mount the folder afterwards):

```powershell
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Src .\output\PPSA99621 -Console <console-ip>
```

**Linux** (needs `curl`; register/mount the folder afterwards):

```sh
bash tools/install.sh --src output/PPSA99621 --console <console-ip>
```

The archive’s `INSTALL.txt` repeats these steps.

Building from source instead is covered in [docs/BUILDING.md](docs/BUILDING.md).
For HD textures and the optional OOT Save label, see [Console setup](docs/CONSOLE-SETUP.md).

**120 Hz:** the release is the `2160p120` build. It asks for 120 Hz output when the
display supports it and otherwise stays at 60 Hz. Keep **Interpolation FPS** at
**60**. Full-game frame-rate performance and 120 Hz output remain unverified.

ROMs, ROM-derived game archives, saves and texture packs are not included.

## Controls and saving

Cross is N64 A, Circle is N64 B, and Options opens pause. With pause saving enabled, press **Circle while paused** to open the save prompt. Saving is unavailable during certain cutscenes, dialogue, minigames and the opening areas before Clock Town. Existing user settings are preserved; the defaults apply only where a setting is absent.

The final label fix supports the original OOT Save lettering, including the matching HD replacement. See [Save-label setup](docs/CONSOLE-SETUP.md#matching-oot-save-label) to import it from your own OOT assets. Without that optional archive, the original Return label remains; saving still works.

## HD textures

Download the **2Ship O2R HD** edition of [GhostlyDark’s MM Reloaded](https://evilgames.eu/texture-packs/mm-reloaded.htm). Extract its `.o2r` into `assets/mods/`, then create `assets/mods/mods.txt` listing its filename, one archive per line. Alternate assets are enabled by default. The HD edition is the one used with this 4K build; higher-resolution packs can increase memory use and loading time.

## Validation and known limits

The packaged executable has booted on PS5 firmware 9.00. Startup, HD archive loading and the pause-save configuration were checked, and the user confirmed the pause-save action works; a full playthrough and every save location have not been verified. Audio improved in an on-console check after correcting the playback address filter. Regression checks cover low-address audio notes, 64-bit message storage and exhausted sample positions. Music quality and all individual effects have not been exhaustively verified. Defensive audio checks remain enabled. If an audio guard triggers, preserve the title’s `mm-adpcm-range.txt` diagnostic when reporting the problem.

Save/configuration files live in the title’s sandbox `/download0` area. Preserve that data when updating; it is separate from the installed assets folder. Do not overwrite a running title.

## Build validation

Run `bash tools/check-build.sh --self-test` to test the validator, or `bash tools/check-build.sh --dir /path/to/PPSA99621` to check a complete title. Add `--release` for packages without private game data, and `--json` for machine-readable results. Release packaging runs these checks automatically.

## Credits and license

Thanks to Harbour Masters, libultraship contributors, the PS5 SDK/OpenGL/SDL and native-app developers, and GhostlyDark for the optional texture pack. Audio sample-boundary work incorporates the approach documented in [upstream PR #1745](https://github.com/HarbourMasters/2ship2harkinian/pull/1745).

See [LICENSE](LICENSE), [third-party notices](THIRD-PARTY-NOTICES.md), and [pinned sources](sources.lock.json). This project is not affiliated with Nintendo.
