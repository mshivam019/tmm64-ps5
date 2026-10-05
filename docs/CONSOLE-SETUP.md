# Console setup

Use a homebrew-capable PS5 with kstuff, ShadowMountPlus and an active FTP server. This installation uses `/mnt/ext1` for M.2 storage. The `etaHEN/games` directory name is historical; loading etaHEN is not required for this setup.

1. Extract the release for your computer’s operating system.
2. Run official 2Ship 5.0.1 on your computer with your own supported ROM and finish its extraction. Close it, then copy the generated `mm.o2r` into `output/PPSA99621/assets/`.
3. Close Majora’s Mask on the console. Start your FTP server and note its IP and port.
4. Upload the complete `PPSA99621` directory with your FTP client, or use:

Linux:
```sh
bash tools/install.sh --src output/PPSA99621 --console YOUR_PS5_IP --ftp-port 2121
```

Windows PowerShell:
```powershell
./tools/install.ps1 -Src output/PPSA99621 -Console YOUR_PS5_IP -FtpPort 2121
```

5. Register/mount the folder with ShadowMountPlus using your existing console workflow, then launch the game tile. The upload scripts transfer files; they do not remotely close games or launch the title.

For updates, preserve your UserData and sandbox saves/configuration. See [settings and camera controls](SETTINGS.md) and [HD texture setup](MODS.md). Optional texture packs go in `assets/mods/`; list each archive’s filename in `assets/mods/mods.txt`. Restart after changing assets.

Pause with Options, then press Circle to open saving where permitted. Opening areas before Clock Town and certain gameplay states intentionally prohibit saving.

## Matching OOT Save label

The pause-save button supports OOT’s original Save lettering and its Reloaded HD replacement, using the resource loader’s native texture scaling. It displays Save only when pause saving is available; Start/Options retains Return. Without the optional label archive, it falls back to the game’s original Return text; the saving action still works.

Use Python 3 and the included helper to copy the label from your own OOT assets:

```sh
python tools/import-save-label.py --oot /path/to/oot.o2r --hd /path/to/OoT_Reloaded_v11.0.0_HD.o2r --title output/PPSA99621
```

Omit `--hd` to use the original-resolution lettering. On Windows, use `py` instead of `python` if needed. The helper preserves existing `mods.txt` entries. Upload the generated `assets/mods/MM_OOT_Save_Label.o2r` and updated `mods.txt` with the game closed, then restart. The OOT assets and optional Reloaded texture are supplied separately and are not bundled in this release.
