# HD textures and other mods

Use packs made for **2 Ship 2 Harkinian**, with an `.o2r` or compatible `.otr` archive. Texture packs for SoH/Ocarina, GLideN64, Recomp/RT64 or PNG folders cannot be installed with this process.

## MM Reloaded HD

1. Download [mm-reloaded-v11.0.3-2ship-o2r-hd.7z](https://github.com/GhostlyDark/MM-Reloaded/releases/download/v11.0.2/mm-reloaded-v11.0.3-2ship-o2r-hd.7z) from [GhostlyDark's release page](https://github.com/GhostlyDark/MM-Reloaded/releases/tag/v11.0.2). The release tag and 2Ship pack version differ. Choose the single **2Ship O2R HD** download; the split 4K and PNG/emulator downloads are different formats or memory requirements.
2. Extract the `.7z` with 7-Zip or another compatible extractor. Copy the resulting `.o2r` into `output/PPSA99621/assets/mods/`. Do not upload the compressed `.7z` itself.
3. Generate the required index on your computer:

   ```sh
   python3 tools/index-mods.py output/PPSA99621/assets/mods
   ```

   Or make a UTF-8 `mods.txt` manually in that folder. Put the **exact extracted filename**, including case and `.o2r`, on one line. List each additional archive on its own line, retaining any existing save-label archive. No quotes, absolute paths or Windows backslashes.
4. Close the PS5 game. Using FileZilla, upload both the archive and `mods.txt` to `/mnt/ext1/etaHEN/games/PPSA99621/assets/mods/` (adjust if installed elsewhere). Restart the title.
5. Press touchpad and enable **Settings → Mod Menu**, open **Popout Mod Menu Window** if needed, and enable **Enable HD textures / mods**. It is enabled by default for fresh PS5 configs; existing disabled settings are preserved. If your binary predates touchpad support, edit its active JSON using the [settings helper](SETTINGS.md#find-the-active-configuration).

## Troubleshooting

- If `UserData/mods/mods.txt` exists, it takes precedence over `assets/mods/mods.txt`. Its entries refer to archives relative to **UserData/mods**. Update that manifest or back it up and remove the stale override so the installed assets manifest is used.
- A filename mismatch, omitted manifest or missing archive prevents loading. Check the title on your computer with `python3 tools/check-mods.py output/PPSA99621`. It checks ZIP CRCs or legacy MPQ headers, not full MPQ integrity or mod gameplay compatibility.
- If the game looks unchanged, confirm alternate assets are enabled, the correct active JSON was edited, and the game was restarted.
- If it fails to launch after a mod change, back up and remove the new mod/index entries, then restart. Keep original `mm.o2r`, `2ship.o2r`, saves and config intact.

Native 2Ship mods may work; compatibility on PS5 is not guaranteed. No texture packs, ROMs or ROM-derived archives are bundled. The optional [OOT Save label](CONSOLE-SETUP.md#matching-oot-save-label) uses the same manifest and should be retained when adding HD packs.
