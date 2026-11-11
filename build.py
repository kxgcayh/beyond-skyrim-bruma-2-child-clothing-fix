#!/usr/bin/env python3
"""Build "Beyond Skyrim - Bruma 2 - Child Clothing Fix.esp".

Beyond Skyrim - Bruma 2.0.0 binds CYRMaintenanceScript.ChildMaleMiscs and .ChildFemaleMiscs (MiscObject[]) on the quest
CYRMaintenance (001961:BSHeartland.esm) as None. SetupChildClothing() then fails with "Cannot access an element of a None
array" and the three child outfits are never registered with the adoption script. This plugin overrides that one quest and
binds the arrays to the boy and girl MISC items of the same colour as each outfit in `childClothing` (same order).

Usage: python3 build.py          dry run: serializes inputs/BSHeartland.esm, prints the YAML change, writes no plugin
       python3 build.py --write  also writes dist/, round-trips it and checks the result
Needs the toolkit's tools/spriggit-cli.sh (SKYRIM_TOOLKIT overrides its path) and inputs/ (see README.md).
"""
import difflib, hashlib, os, pathlib, re, shutil, struct, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
INPUTS, BUILD, DIST = HERE / 'inputs', HERE / 'build', HERE / 'dist'
TOOLKIT = pathlib.Path(os.environ.get('SKYRIM_TOOLKIT', '/Volumes/S512/Projects/ETC/skyrim-ai-toolkit'))
NAME = 'Beyond Skyrim - Bruma 2 - Child Clothing Fix'
DESC = 'Binds the child clothing gift items that Beyond Skyrim - Bruma 2.0.0 leaves unset on CYRMaintenance.'
QUEST = 'Quests/CYRMaintenance - 001961_BSHeartland.esm.yaml'

# childClothing order in the 2.0.0 plugin: Blue 1BD173, Purple 1F1541, Turquoise 1BD172
MALE = ['1D99E9', '1D99E8', '1D99EA']    # CYRClothesChild{Blue,Purple,Turquoise}Male
FEMALE = ['1D99E7', '1D99E6', '1D99E5']  # CYRClothesChild{Blue,Purple,Turquoise}Female


def lst(name, ids):
    return ('    - MutagenObjectType: ScriptObjectListProperty\n'
            f'      Name: {name}\n      Objects:\n'
            + ''.join(f"      - Name: ''\n        Object: {i}:BSHeartland.esm\n" for i in ids))


def run(*cmd):
    r = subprocess.run(['bash', str(TOOLKIT / 'tools/spriggit-cli.sh'), *cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-1500:] + r.stderr[-1500:])


def check_inputs():
    for line in (HERE / 'inputs.sha256').read_text().splitlines():
        want, name = line.split(None, 1)
        f = INPUTS / name.strip()
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != want:
            sys.exit(f'inputs/{name.strip()} is missing or not the version this was written against (README.md)')


def edited(text):
    old_f = '    - MutagenObjectType: ScriptProperty\n      Name: ChildFemaleMiscs\n'
    old_m = '    - MutagenObjectType: ScriptProperty\n      Name: ChildMaleMiscs\n'
    assert text.count(old_f) == 1 and text.count(old_m) == 1, 'the quest no longer has the two empty properties'
    return text.replace(old_f, lst('ChildFemaleMiscs', FEMALE)).replace(old_m, lst('ChildMaleMiscs', MALE))


def main():
    write = '--write' in sys.argv
    check_inputs()
    yaml = BUILD / 'yaml-BSHeartland'
    if not (yaml / QUEST).is_file():
        shutil.rmtree(yaml, ignore_errors=True)
        BUILD.mkdir(exist_ok=True)
        run('serialize', '--InputPath', str(INPUTS / 'BSHeartland.esm'), '--OutputPath', str(yaml), '--GameRelease', 'SkyrimSE',
            '--PackageName', 'Spriggit.Yaml.Skyrim', '--PackageVersion', '0.41.0', '-u')
    src = (yaml / QUEST).read_text()
    new = edited(src)
    diff = ''.join(difflib.unified_diff(src.splitlines(True), new.splitlines(True), 'BSHeartland.esm 2.0.0', NAME, n=1))
    print(diff)
    (BUILD / 'review.diff').write_text(diff)
    masters = sorted({m for m in re.findall(r':([^\s:]+\.es[mpl])\b', new)}, key=lambda m: m.lower())
    order = ['Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm', 'BSAssets.esm', 'BSHeartland.esm']
    masters = [m for m in order if m in masters] + [m for m in masters if m not in order]
    print('masters:', masters)
    if not write:
        print('dry run: nothing written')
        return
    out = BUILD / 'out' / NAME
    shutil.rmtree(out, ignore_errors=True)
    (out / QUEST).parent.mkdir(parents=True)
    (out / QUEST).write_text(new)
    refs = ''.join(f'  - Master: {m}\n    FileSize: 0\n' for m in masters)
    (out / 'RecordData.yaml').write_text(
        'SpriggitSource:\n  PackageName: Spriggit.Yaml.Skyrim\n  Version: 0.41.0\n'
        f'ModKey: {NAME}.esp\nGameRelease: SkyrimSE\nModHeader:\n  Flags:\n  - Small\n'
        '  Stats:\n    Version: 1.7\n    NextFormID: 2048\n  Author: kxgcayh\n'
        f'  Description: {DESC}\n  MasterReferences:\n{refs}  INTV: 1\n')
    shutil.copy(yaml / 'spriggit-meta.json', out / 'spriggit-meta.json')  # the wrapper needs it beside RecordData.yaml
    DIST.mkdir(exist_ok=True)
    esp = DIST / f'{NAME}.esp'
    run('deserialize', '--InputPath', str(out), '--OutputPath', str(esp))
    rt = BUILD / 'rt'
    shutil.rmtree(rt, ignore_errors=True)
    run('serialize', '--InputPath', str(esp), '--OutputPath', str(rt), '--GameRelease', 'SkyrimSE',
        '--PackageName', 'Spriggit.Yaml.Skyrim', '--PackageVersion', '0.41.0', '-u')
    a = sorted(new.lower().splitlines())
    b = sorted((rt / QUEST).read_text().lower().splitlines())
    assert a == b, 'round trip differs'
    verify(esp)
    print('wrote', esp)


def verify(esp):
    d = esp.read_bytes()
    sz = struct.unpack_from('<I', d, 4)[0]
    flags = struct.unpack_from('<I', d, 8)[0]
    i, masters = 24, []
    while i < 24 + sz:
        t, ln = d[i:i + 4], struct.unpack_from('<H', d, i + 4)[0]
        if t == b'MAST':
            masters.append(d[i + 6:i + 6 + ln].rstrip(b'\0').decode())
        i += 6 + ln
    assert masters[-1] == 'BSHeartland.esm' and 'BSAssets.esm' in masters, masters
    n = d.count(b'QUST')
    print(f'header flags {flags:#x}, masters {masters}, QUST tags {n}, size {len(d)}')


if __name__ == '__main__':
    main()
