#!/usr/bin/env bash
# Check a packaged 2 Ship 2 Harkinian title folder (PPSA99621) for completeness.
#
# Run this after tools/build.sh or tools/build-profile.sh if a build looks wrong,
# or before copying a build to the console. Exits non-zero on any problem.
#
# Usage:
#   tools/check-build.sh                      # newest build under $PS5SDK_ROOT/build
#   tools/check-build.sh --dir /path/PPSA99621
#   tools/check-build.sh --json               # machine-readable summary
#   tools/check-build.sh --release --dir /path/PPSA99621  # must omit mm.o2r
#   tools/check-build.sh --update --variant camera-controls --dir /path/PPSA99621
#   tools/check-build.sh --self-test          # check the checker on synthetic folders
set -uo pipefail

REPO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck source=/dev/null
source "$REPO/tools/env.sh" 2>/dev/null || true
PS5SDK_ROOT=${PS5SDK_ROOT:-/opt/ps5sdk}

TITLE_ID=PPSA99621
CONCEPT_ID=99621
CONTENT_ID=UP9000-PPSA99621_00-2SHIP2HARKINIAN0

DIR=
JSON=0
RELEASE=0
UPDATE=0
VARIANT=
while [ $# -gt 0 ]; do
    case $1 in
        --dir) DIR=${2:?--dir needs a path}; shift 2 ;;
        --dir=*) DIR=${1#*=}; shift ;;
        --json) JSON=1; shift ;;
        --update) UPDATE=1; shift ;;
        --variant) VARIANT=${2:?--variant needs stock or camera-controls}; shift 2 ;;
        --release) RELEASE=1; shift ;;
        --self-test) SELF_TEST=1; shift ;;
        -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

case "$VARIANT" in ""|stock|camera-controls) ;; *) echo "Invalid controls variant: $VARIANT" >&2; exit 2 ;; esac
if [ "$UPDATE" = 1 ] && [ "$RELEASE" = 1 ]; then echo "--update and --release are separate package modes" >&2; exit 2; fi

# Build a synthetic title folder that passes, then break it one way at a time and
# confirm each break is caught. Needs no SDK, build or game data.
self_test() {
    local work self=${BASH_SOURCE[0]} passed=0 failed=0
    work=$(mktemp -d)
    trap 'rm -rf "$work"' RETURN

    make_fixture() {
        local d=$1
        mkdir -p "$d/sce_module" "$d/sce_sys" "$d/assets"
        pad() { { printf "$2"; head -c "$3" /dev/zero; } >"$d/$1"; }
        pad eboot.bin '\x4f\x15\x3d\x1d' 1100000
        pad sce_module/libc.prx '\x54\x14\xf5\xee' 110000
        pad sce_sys/icon0.png '\x89PNG\r\n\x1a\n' 2048
        pad sce_sys/pic0.dds 'DDS ' 2048
        pad sce_sys/pic1.dds 'DDS ' 2048
        head -c 2048 /dev/zero | tr '\0' '#' >"$d/assets/gamecontrollerdb.txt"
        python3 - "$d" "$TITLE_ID" "$CONCEPT_ID" "$CONTENT_ID" <<'PY'
import json, os, sys, zipfile
d, title, concept, content = sys.argv[1:5]
for name, size in (("mm.o2r", 1_200_000), ("2ship.o2r", 150_000)):
    with zipfile.ZipFile(os.path.join(d, "assets", name), "w", zipfile.ZIP_STORED) as z:
        z.writestr("blob", os.urandom(size))
json.dump({"titleId": title, "conceptId": concept, "contentId": content,
           "localizedParameters": {"defaultLanguage": "en-US",
                                   "en-US": {"titleName": "2 Ship 2 Harkinian"}},
           "padding": "x" * 64},
          open(os.path.join(d, "sce_sys", "param.json"), "w"))
PY
    }

    expect() {
        local want=$1 name=$2 dir=$3 rc
        shift 3
        bash "$self" --dir "$dir" "$@" >"$work/out" 2>&1
        rc=$?
        if [ "$rc" = "$want" ]; then
            echo "  ok    $name"
            passed=$((passed + 1))
        else
            echo "  FAIL  $name (exit $rc, expected $want)"
            sed 's/^/        /' "$work/out"
            failed=$((failed + 1))
        fi
    }

    case_dir() { rm -rf "$work/case"; cp -a "$work/good" "$work/case"; echo "$work/case"; }

    make_fixture "$work/good"
    echo "Self-test"
    expect 0 "valid folder passes" "$work/good"
    local c
    c=$(case_dir); rm "$c/eboot.bin"; expect 1 "missing eboot.bin" "$c"
    c=$(case_dir); rm "$c/assets/mm.o2r"; expect 1 "missing mm.o2r" "$c"
    c=$(case_dir); rm "$c/assets/2ship.o2r"; expect 1 "missing 2ship.o2r" "$c"
    c=$(case_dir); head -c 1 "$work/good/eboot.bin" >"$c/eboot.bin"; expect 1 "1-byte eboot.bin" "$c"
    c=$(case_dir); printf 'XXXX' | dd of="$c/eboot.bin" conv=notrunc 2>/dev/null; expect 1 "wrong eboot.bin magic" "$c"
    c=$(case_dir); head -c 1100000 "$work/good/assets/mm.o2r" >"$c/assets/mm.o2r"; expect 1 "truncated mm.o2r" "$c"
    c=$(case_dir); sed -i 's/"PPSA99621"/"PPSA00000"/' "$c/sce_sys/param.json"; expect 1 "wrong titleId" "$c"
    c=$(case_dir); echo '{' >"$c/sce_sys/param.json"; head -c 200 /dev/zero | tr '\0' ' ' >>"$c/sce_sys/param.json"
    expect 1 "invalid param.json" "$c"
    c=$(case_dir); touch "$c/perf.txt"; expect 1 "stray perf.txt" "$c"
    c=$(case_dir); : >"$c/sce_sys/snd0.at9"; expect 1 "stray snd0.at9" "$c"
    c=$(case_dir); echo '{' >"$c/build-profile.json"; expect 1 "invalid build-profile.json" "$c"
    c=$(case_dir); echo '{}' >"$c/build-profile.json"; expect 1 "missing display profile" "$c"
    c=$(case_dir); echo '{"display_profile":{"width":3840,"height":2160,"fps":120}}' >"$c/build-profile.json"; expect 0 "valid display profile" "$c"
    c=$(case_dir); echo '{"display_profile":{"width":3840,"height":1080,"fps":120}}' >"$c/build-profile.json"; expect 1 "mismatched display dimensions" "$c"
    c=$(case_dir); echo '[]' >"$c/build-profile.json"; expect 1 "non-object profile" "$c"
    c=$(case_dir)
    python3 - "$c" <<'PYCHECKSUM'
import json,hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]);json.dump({'display_profile':{'width':3840,'height':2160,'fps':120},'eboot_sha256':hashlib.sha256((p/'eboot.bin').read_bytes()).hexdigest()},open(p/'build-profile.json','w'))
PYCHECKSUM
    expect 0 "matching executable checksum" "$c"
    printf 'tamper' >>"$c/eboot.bin"; expect 1 "executable checksum mismatch" "$c"

    c=$(case_dir); rm "$c/assets/mm.o2r"; expect 0 "release without private data" "$c" --release
    expect 1 "release rejects private game archive" "$work/good" --release
    c=$(case_dir); mkdir -p "$c/assets/mods"; cp "$c/assets/2ship.o2r" "$c/assets/mods/HD.o2r"
    expect 1 "HD archive requires manifest" "$c"
    echo HD.o2r >"$c/assets/mods/mods.txt"; expect 0 "indexed HD archive" "$c"
    echo missing.o2r >"$c/assets/mods/mods.txt"; expect 1 "missing indexed archive" "$c"
    echo ../2ship.o2r >"$c/assets/mods/mods.txt"; expect 1 "manifest path traversal" "$c"
    c=$(case_dir); rm -rf "$c/assets" "$c/sce_sys"
    python3 - "$c" <<'PYUPDATE'
import json,hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]); (p/'build-profile.json').write_text(json.dumps({'display_profile':{'width':3840,'height':2160,'fps':120},'game_assets_included':False,'controls_variant':'camera-controls','eboot_sha256':hashlib.sha256((p/'eboot.bin').read_bytes()).hexdigest()}))
PYUPDATE
    expect 0 "camera executable update" "$c" --update --variant camera-controls
    expect 1 "camera rejected as stock" "$c" --update --variant stock
    expect 1 "update rejected as full installation" "$c"
    printf tamper >>"$c/eboot.bin"; expect 1 "update executable tamper" "$c" --update
    rm "$c/build-profile.json"; expect 1 "update requires receipt" "$c" --update
    bash "$self" --dir "$work/good" --json >"$work/result.json"
    if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert not d["failures"]' "$work/result.json"; then
        echo "  ok    JSON output parses"; passed=$((passed + 1))
    else
        echo "  FAIL  JSON output parses"; failed=$((failed + 1))
    fi
    expect 1 "nonexistent directory" "$work/missing"

    echo
    if [ "$failed" = 0 ]; then
        echo "SELF-TEST PASS: $passed case(s)"
        return 0
    fi
    echo "SELF-TEST FAIL: $failed of $((passed + failed)) case(s)"
    return 1
}

if [ "${SELF_TEST:-0}" = 1 ]; then
    self_test
    exit $?
fi

FAIL=()
WARN=()
OK=()

human() { numfmt --to=iec --suffix=B "$1" 2>/dev/null || echo "$1"; }
magic() { head -c "$2" "$1" 2>/dev/null | od -An -tx1 | tr -d ' \n'; }
json_escape() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

find_default() {
    local found
    found=$(find "$PS5SDK_ROOT/build" -maxdepth 4 -type d -name "$TITLE_ID" -printf '%T@ %p\n' 2>/dev/null |
        sort -rn | head -1 | cut -d' ' -f2-)
    if [ -n "$found" ]; then printf '%s\n' "$found"; return 0; fi
    if [ -d "$REPO/dist/$TITLE_ID" ]; then printf '%s\n' "$REPO/dist/$TITLE_ID"; return 0; fi
    return 1
}

if [ -z "$DIR" ]; then
    if ! DIR=$(find_default); then
        DIR="$REPO/dist/$TITLE_ID"
    fi
fi
if [ ! -d "$DIR" ]; then
    if [ "$JSON" = 1 ]; then
        python3 - "$DIR" <<'PYJSON'
import json,sys
print(json.dumps({"dir": sys.argv[1], "ok": [], "warnings": [], "failures": ["directory not found"]}))
PYJSON
    else
        echo "no such directory: $DIR" >&2
    fi
    exit 1
fi
DIR=$(cd -- "$DIR" && pwd)

check_file() {
    local rel=$1 min=$2 want=${3:-} label=${4:-$1} size got
    local p=$DIR/$rel
    if [ ! -e "$p" ]; then FAIL+=("missing file: $label"); return; fi
    if [ ! -f "$p" ]; then FAIL+=("not a regular file: $label"); return; fi
    size=$(stat -c%s "$p" 2>/dev/null || echo 0)
    if [ "$size" -lt "$min" ]; then
        FAIL+=("incomplete file: $label is $size bytes, expected at least $min")
        return
    fi
    if [ -n "$want" ]; then
        got=$(magic "$p" "$((${#want} / 2))")
        if [ "$got" != "$want" ]; then
            FAIL+=("corrupt file: $label header is ${got:-empty}, expected $want")
            return
        fi
    fi
    OK+=("$label ($(human "$size"))")
}

check_absent() {
    if [ -e "$DIR/$1" ]; then
        FAIL+=("unexpected file present: $1")
    else
        OK+=("$1 absent (expected)")
    fi
}

check_zip() {
    local rel=$1 label=${2:-$1} out rc
    # A missing file is already reported by check_file.
    [ -f "$DIR/$rel" ] || return
    out=$(python3 - "$DIR/$rel" <<'PY'
import sys, zipfile
try:
    bad = zipfile.ZipFile(sys.argv[1]).testzip()
except Exception as e:
    print(e)
    raise SystemExit(1)
if bad is not None:
    print(f"corrupt entry: {bad}")
    raise SystemExit(1)
PY
    )
    rc=$?
    if [ $rc -eq 0 ]; then
        OK+=("$label archive integrity")
    else
        FAIL+=("$label archive failed integrity: $out")
    fi
}

check_param() {
    local out rc
    out=$(python3 - "$DIR/sce_sys/param.json" "$TITLE_ID" "$CONCEPT_ID" "$CONTENT_ID" 2>&1 <<'PY'
import json, sys
path, title, concept, content = sys.argv[1:5]
try:
    p = json.load(open(path, encoding="utf-8"))
except Exception as e:
    print(f"sce_sys/param.json is not valid JSON: {e}")
    raise SystemExit(1)
errors = []
if p.get("titleId") != title:
    errors.append(f"sce_sys/param.json titleId={p.get('titleId')!r}, expected {title!r}")
if p.get("conceptId") != concept:
    errors.append(f"sce_sys/param.json conceptId={p.get('conceptId')!r}, expected {concept!r}")
if p.get("contentId") != content:
    errors.append(f"sce_sys/param.json contentId={p.get('contentId')!r}, expected {content!r}")
localized = p.get("localizedParameters") or {}
language = localized.get("defaultLanguage")
name = (localized.get(language) or {}).get("titleName")
if not name:
    errors.append("sce_sys/param.json has no titleName for its default language")
for e in errors:
    print(e)
raise SystemExit(1 if errors else 0)
PY
    )
    rc=$?
    if [ $rc -eq 0 ]; then
        OK+=("sce_sys/param.json metadata")
    else
        while IFS= read -r line; do
            [ -n "$line" ] && FAIL+=("$line")
        done <<<"$out"
    fi
}

check_file eboot.bin 1000000 4f153d1d "eboot.bin"
check_file sce_module/libc.prx 100000 5414f5ee "sce_module/libc.prx"
if [ "$UPDATE" = 0 ]; then
if [ "$RELEASE" = 1 ]; then
    check_absent assets/mm.o2r
else
    check_file assets/mm.o2r 1000000 504b0304 "assets/mm.o2r"
fi
check_file assets/2ship.o2r 100000 504b0304 "assets/2ship.o2r"
check_file assets/gamecontrollerdb.txt 1024 "" "assets/gamecontrollerdb.txt"
check_file sce_sys/param.json 100 "" "sce_sys/param.json"
check_file sce_sys/icon0.png 1024 89504e470d0a1a0a "sce_sys/icon0.png"
check_file sce_sys/pic0.dds 1024 44445320 "sce_sys/pic0.dds"
check_file sce_sys/pic1.dds 1024 44445320 "sce_sys/pic1.dds"
check_zip assets/mm.o2r
check_zip assets/2ship.o2r
check_param
else
    WARN+=("executable update only; preserve installed game assets, metadata and saves")
fi
check_absent sce_sys/snd0.at9
check_absent perf.txt
mods_result=$(python3 "$REPO/tools/check-mods.py" "$DIR" 2>&1)
if [ $? = 0 ]; then OK+=("$mods_result"); else FAIL+=("mod manifest validation: $mods_result"); fi

if [ -f "$DIR/build-profile.json" ]; then
    profile_error=$(python3 - "$DIR/build-profile.json" "$VARIANT" "$UPDATE" <<'PYPROFILE'
import json,sys,hashlib
from pathlib import Path
try:
    path=Path(sys.argv[1]); p=json.loads(path.read_text())
    if not isinstance(p, dict): raise ValueError('profile must be an object')
    variant=p.get('controls_variant', 'stock')
    if variant not in ('stock', 'camera-controls'): raise ValueError('unknown controls variant')
    if sys.argv[2] and variant != sys.argv[2]: raise ValueError('controls variant mismatch')
    if sys.argv[3] == '1' and p.get('game_assets_included') is not False: raise ValueError('update requires game_assets_included=false')
    if (sys.argv[3] == '1' or variant == 'camera-controls') and not p.get('eboot_sha256'): raise ValueError('missing executable checksum')
    d=p['display_profile']
    if (d['width'],d['height']) not in ((1920,1080),(2560,1440),(3840,2160)) or d['fps'] not in (60,120):
        raise ValueError('unsupported or inconsistent display profile')
    if 'eboot_sha256' in p and p['eboot_sha256'] != hashlib.sha256((path.parent/'eboot.bin').read_bytes()).hexdigest():
        raise ValueError('eboot.bin does not match recorded checksum')
except (ValueError,KeyError,TypeError,OSError) as e:
    print(str(e)); sys.exit(1)
PYPROFILE
    )
    if [ $? = 0 ]; then
        OK+=("build-profile.json display profile and executable checksum (if present)")
    else
        FAIL+=("build-profile.json: $profile_error")
    fi
else
    if [ "$UPDATE" = 1 ] || [ "$VARIANT" = camera-controls ]; then FAIL+=("build-profile.json required for update/camera variant"); else WARN+=("no build-profile.json (stock 0.3.0 driver profile)"); fi
fi

if [ "$JSON" = 1 ]; then
    printf '{"dir": %s, "ok": [' "$(json_escape "$DIR")"
    sep=
    for x in "${OK[@]}"; do printf '%s%s' "$sep" "$(json_escape "$x")"; sep=,; done
    printf '], "warnings": ['
    sep=
    for x in "${WARN[@]}"; do printf '%s%s' "$sep" "$(json_escape "$x")"; sep=,; done
    printf '], "failures": ['
    sep=
    for x in "${FAIL[@]}"; do printf '%s%s' "$sep" "$(json_escape "$x")"; sep=,; done
    printf ']}\n'
else
    echo "Checking: $DIR"
    for x in "${OK[@]}"; do echo "  OK    $x"; done
    for x in "${WARN[@]}"; do echo "  WARN  $x"; done
    for x in "${FAIL[@]}"; do echo "  FAIL  $x"; done
    echo
fi

if [ ${#FAIL[@]} -eq 0 ]; then
    [ "$JSON" = 1 ] || echo "PASS: ${#OK[@]} checks passed, ${#WARN[@]} warning(s)"
    exit 0
fi
[ "$JSON" = 1 ] || echo "FAIL: ${#FAIL[@]} problem(s) found in $DIR"
exit 1
