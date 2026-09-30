#!/usr/bin/env python3
"""Check the actual PS5 HUD default guard against 2Ship's widescreen preset."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    root = args.source
    port = (root / 'mm/2s2h/BenPort.cpp').read_text()
    hud = (root / 'mm/2s2h/BenGui/HudEditor.cpp').read_text()
    element_names = dict(re.findall(
        r'HUD_EDITOR_ELEMENT\(HUD_EDITOR_ELEMENT_(\w+),\s*"[^"]+",\s*"([^"]+)"', hud))
    preset = hud.split('case HudEditor::Presets::WIDESCREEN: {', 1)[1].split('break;', 1)[0]
    mode_values = {'MOVABLE_43': 2, 'MOVABLE_LEFT': 3, 'MOVABLE_RIGHT': 4}
    expected = {'gHudEditor.' + element_names[element] + '.Mode': mode_values[mode]
                for element, mode in re.findall(
                    r'CVarSetInteger\(hudEditorElements\[HUD_EDITOR_ELEMENT_(\w+)\]\.modeCvar,\s*'
                    r'HUD_EDITOR_ELEMENT_MODE_(\w+)\)', preset)}
    assert len(expected) == 19, 'Incomplete upstream widescreen preset'
    block = port.split('// PS5 widescreen HUD defaults.', 1)[1].split('\n', 1)[1].split(
        'if (defaultsAdded) context->GetConsoleVariables()->Save();', 1)[0]
    actual = {name: int(mode) for name, mode in re.findall(r'\{"(gHudEditor\.[^"]+)", (\d+)\}', block)}
    assert actual == expected, 'PS5 HUD defaults differ from upstream widescreen modes'
    assignments = '\n'.join(f'assert(values.at("{name}") == {mode});' for name, mode in expected.items())
    program = '''#include <cassert>
#include <map>
#include <string>
std::map<std::string, int> values;
int CVarGetInteger(const char* name, int fallback) {
    auto found = values.find(name);
    return found == values.end() ? fallback : found->second;
}
void CVarSetInteger(const char* name, int value) { values[name] = value; }
void apply() { bool defaultsAdded = false;
''' + block + '''
}
int main() {
    apply();
''' + assignments + '''
    assert(values.size() == 19);
    auto first = values;
    apply();
    assert(values == first);
    values = {{"gHudEditor.Hearts.Mode", 0}, {"gHudEditor.Minimap.Mode", 1},
              {"gHudEditor.Hearts.Position.X", 42}, {"gSettings.Controllers.Port1.HasConfig", 1},
              {"gEnhancements.Mods.AlternateAssets", 1}, {"gEnhancements.Saving.PauseSave", 1}};
    apply();
    assert(values.at("gHudEditor.Hearts.Mode") == 0);
    assert(values.at("gHudEditor.Minimap.Mode") == 1);
    assert(values.at("gHudEditor.Hearts.Position.X") == 42);
    assert(values.at("gSettings.Controllers.Port1.HasConfig") == 1);
    assert(values.at("gEnhancements.Mods.AlternateAssets") == 1);
    assert(values.at("gEnhancements.Saving.PauseSave") == 1);
    assert(values.at("gHudEditor.Clock.Mode") == 2);
}
'''
    with tempfile.TemporaryDirectory(prefix='mm-hud-defaults-') as temporary:
        directory = Path(temporary)
        source = directory / 'check.cpp'
        binary = directory / 'check'
        source.write_text(program)
        subprocess.run(['c++', '-std=c++17', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print('HUD defaults passed: upstream preset match, fresh config, explicit layouts, preservation, idempotence')

if __name__ == '__main__':
    main()
