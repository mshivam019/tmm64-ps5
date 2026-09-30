# v1.0.0

Native PS5 port of 2 Ship 2 Harkinian 5.0.1.

**Audio update:** these v1.0.0 downloads replace the earlier files. Re-download if your copy has missing voices or effects. The PS5 build now bypasses an N64 address cutoff that incorrectly skipped valid audio notes. Audio improved in an on-console check; full music/effect coverage remains unverified. Preserve your existing saves, configuration and mods when updating.

- 3840×2160 output; requests 120 Hz with automatic 60 Hz display fallback.
- 60 FPS interpolation default, matched OpenGL/SDL performance patches, and DualSense controls.
- Pause saving, gamepad navigation and alternate assets enabled by default without overriding existing settings.
- Optional MM Reloaded HD texture support.
- OOT64-style build validator with self-tests, JSON output and release-package checks; packaging runs it automatically.
- Windows/Linux installation commands in the README and INSTALL.txt.
- Final OOT Save-label support with correct resource-based HD scaling; the included importer builds the optional label mod from your own OOT archives. Without it, the original Return label remains.
- Playback-address regression test reproduces the old skipped-note behavior and verifies the correction.
- 64-bit audio message fixes, sample-end guards and native executable alignment correction.

Choose the Windows or Linux ZIP; both contain the same PS5 executable. SHA-256 checksums are provided. Generate `mm.o2r` from your own supported ROM with official 2Ship 5.0.1, then place it in `output/PPSA99621/assets/`. ROM-derived game data and texture packs are not included.

Install to `/mnt/ext1/etaHEN/games/PPSA99621` and register/mount with ShadowMountPlus. The directory name does not require etaHEN. Close the game before updating and preserve sandbox saves/configuration.

Pause with Options, then press Circle to open the save prompt where saving is permitted. Opening areas before Clock Town and certain cutscenes/minigames prohibit saving.

Verified on PS5 firmware 9.00: executable startup, HD archive loading and saving configuration; the user confirmed the save action works. The final OOT label appearance still awaits visual confirmation. Audio regression checks pass. A full playthrough and sustained frame-rate performance have not been verified; the display profile is not a game-FPS guarantee.
