# Settings, language and camera controls

These controls apply to source builds containing the touchpad change. The existing v1.0.0 download predates it. New menu/camera changes require PS5 testing before a binary release.

## Open the port settings

Press the DualSense **touchpad button** to open or close the 2Ship menu. It also enables controller navigation. Navigate with the D-pad/left stick, Cross to select and Circle to go back. **Options** remains N64 Start: it opens the game's pause menu, where Circle opens saving when allowed. The desktop controller-configuration window is a separate port window; it is not the pause/save menu.

PS5 interpolation is fixed at **60 FPS**, shown in Settings → Graphics. There is no 30 FPS selection or match-refresh option on PS5. Display output may request 120 Hz with 60 Hz fallback; this does not prove sustained gameplay performance.

## Language support

This pinned 2Ship 5.0.1 port supports NTSC-US assets and runs in **English**. It has no equivalent of SoH's Language selector. German and Spanish are not provided by these assets; changing a SoH language key in this title's JSON cannot add their text. A compatible translation mod would need separate testing. Do not replace `mm.o2r` with unsupported PAL assets.

For Ocarina's English/German configuration, use the companion [SoH settings guide](https://github.com/mshivam019/oot64-ps5/blob/main/docs/SETTINGS.md).

## Find the active configuration

Settings → General displays the **Config folder**. The filename is `2ship2harkinian.json`:

- Writable title folder: `/app0/UserData/2ship2harkinian.json`, normally accessed by FTP as `/mnt/ext1/etaHEN/games/PPSA99621/UserData/2ship2harkinian.json`.
- Otherwise: `/download0/2ship2harkinian.json` in this title's save sandbox. Your FTP server's mounted sandbox path can differ; use the game's displayed folder and your existing sandbox workflow.

A JSON beside `eboot.bin` is not the active configuration. Close the game before downloading or editing it; keep a backup and upload to the same path. Settings changed in the menu are saved by the port. Never overwrite a live title's configuration.

To restore menu navigation or enable installed HD textures in an existing downloaded config:

```sh
python3 tools/configure-settings.py /path/to/2ship2harkinian.json --hd-textures on
```

The helper makes a backup and preserves unrelated settings/controller bindings. Windows users can use `py` instead of `python3`. It writes `CVars.gSettings.ControlNav=1`, `CVars.gInterpolationFPS=60`, `CVars.gMatchRefreshRate=0`, and `CVars.gEnhancements.Mods.AlternateAssets=1`. It does not install texture archives; follow [MODS.md](MODS.md).

## Camera controls and HD defaults

New PS5 source builds include both toggles, enabled by default. Open **Settings → Mod Menu** (in 2Ship, select **Popout Mod Menu Window**) and change **Right-stick camera controls** or **Enable HD textures / mods**. They work independently and saved off settings remain off after restarting. HD still requires the archive and `mods.txt`; see [MODS.md](MODS.md).

Camera mode uses right stick for Free Look and D-pad for C buttons. Cross=A, Circle=B and Options=Start retain their bindings. Turning camera mode off restores the controller bindings saved when it was enabled. Changes to other controller ports are preserved. An older camera build without that backup falls back to the standard right-stick C buttons and D-pad directions; keep a config backup if you previously customized those mappings.

Every normal source build includes this feature; no camera patch or build environment flag is needed. `CVars.gSettings.PS5CameraControls` is `1` for on and `0` for off. For a downloaded active config, use `tools/configure-settings.py` with `--camera-controls on` or `off`. Close the title before editing it. The helper also accepts `--hd-textures on` or `off` and preserves unrelated settings.

## Menu size on a TV

PS5 source builds scale the port UI with output resolution (twice the native UI size at 4K), with Large as the default. Settings → General → Menu Size lets you choose Small, Normal, Large or X-Large. Existing size preferences remain saved. This changes the port menu, not game HUD or texture resolution.

To change a downloaded config before uploading it, add `--menu-size large` (or `x-large`) to `tools/configure-settings.py`. Close the title first.

Controller menu navigation: **L1/R1** change the top-level tab; **L2/R2** change its sidebar section. Use D-pad/left stick to focus controls, Cross to activate, and Circle to cancel a selector or popup. Custom tabs/sections show a focus outline. Shoulder shortcuts pause while a control is being edited or a popup is open. Touchpad closes the menu.

Select a sidebar section with **Cross** (or press **D-pad Right** while it is focused) to enter its first enabled control. **Circle** returns to the selected sidebar section when no selector/popup is open. **Triangle** focuses the power/reset/close action row; use D-pad left/right and Cross there. Circle cancels open selectors and confirmation prompts before returning to the sidebar.
