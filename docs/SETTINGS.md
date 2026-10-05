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

## Optional right-stick camera build

The **stock** build keeps the original right-stick C buttons. The **camera-controls** build uses right stick for 2Ship's native FreeLook, and D-pad for C-Up/C-Down/C-Left/C-Right. Cross=A, Circle=B and Options=Start stay mapped. Touchpad opens the port menu in both builds.

The camera profile applies once on its first frame, retaining face-button, keyboard and other C-button alternatives. It removes the default D-pad N64 direction bindings to avoid duplicate actions. A marker `CVars.gSettings.PS5CameraProfileVersion=1` preserves subsequent user edits. FreeLook controls are under Enhancements → Camera and use `CVars.gEnhancements.Camera.FreeLook.Enable`.

Both variants use title ID PPSA99621 and share saves/configuration. **Switching back to stock does not reset the saved camera mappings.** Back up your config first; restore that backup or edit the controller mappings and disable FreeLook in the menu when reverting. Remove the profile marker only if you deliberately want the camera build to reapply its defaults.

Build selection:

```sh
bash tools/fetch-mm.sh --camera-controls
MM_CAMERA_CONTROLS=1 bash tools/build.sh
# Stock source/build selection:
MM_CAMERA_CONTROLS=0 bash tools/build.sh
```

With no build override, the fetch selection is retained. The camera build remains an untested console candidate until right-stick movement, C-button actions, menus and saving are checked on hardware.
