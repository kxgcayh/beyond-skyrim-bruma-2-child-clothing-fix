# Beyond Skyrim - Bruma 2 - Child Clothing Fix

Private release (v0.1.1), untested on a new game. One override of the quest `CYRMaintenance` (`001961:BSHeartland.esm`) for Beyond
Skyrim - Bruma 2.0.0 (Nexus 10917).

## Requirements

| Required | Source | Why |
|---|---|---|
| Beyond Skyrim - Bruma SE 2.0.0 | Nexus 10917 (`BSHeartland.esm`) | the plugin overrides its quest `CYRMaintenance`; 1.6.4 has no such properties, so it does not apply |
| Beyond Skyrim - Assets SE | Nexus 198585 (`BSAssets.esm`) | master of `BSHeartland.esm` 2.0.0; the copied record references it, and `BSKAdoptionScript` lives there |
| Skyrim.esm, Update.esm, Dragonborn.esm, HearthFires.esm | base game and DLC | the record's other masters |

Masters in the plugin header: `Skyrim.esm`, `Update.esm`, `HearthFires.esm`, `Dragonborn.esm`, `BSAssets.esm`,
`BSHeartland.esm`. Tested only with Bruma 2.0.0 and Assets SE 2026.11.11. Not for new content from Bruma updates that
change `CYRMaintenance`: the plugin copies the 2.0.0 record, so a later Bruma change to that quest would be overridden.

## Problem

`BSHeartland.esm` 2.0.0 binds `CYRMaintenanceScript.ChildMaleMiscs` and `ChildFemaleMiscs` (`MiscObject[]`) as None. At
new-game start `SetupChildClothing()` loops over the three entries of `childClothing` and indexes both arrays, so the log
shows `Cannot access an element of a None array` three times and `RegisterChildOutfit` never runs: the outfits are not
registered with `BSKAdoptionScript` (Assets SE) and its Bring Your Own Hearthfire gift lists. Version 1.6.4 has no such
feature (43 properties on the script, none of these).

## Change

The two arrays are bound to the gift items of the same colour, in the order of `childClothing`:

| childClothing | ChildMaleMiscs | ChildFemaleMiscs |
|---|---|---|
| `CYRClothesChildBlue` (`1BD173`) | `CYRClothesChildBlueMale` (`1D99E9`) | `CYRClothesChildBlueFemale` (`1D99E7`) |
| `CYRClothesChildPurple` (`1F1541`) | `CYRClothesChildPurpleMale` (`1D99E8`) | `CYRClothesChildPurpleFemale` (`1D99E6`) |
| `CYRClothesChildTurquoise` (`1BD172`) | `CYRClothesChildTurquoiseMale` (`1D99EA`) | `CYRClothesChildTurquoiseFemale` (`1D99E5`) |

The pairing by colour and gender is an inference: the author left the arrays empty. Nothing else in the quest changes
(`build/review.diff` after a build).

## Test status

NOT yet tested on a new game. The fix only takes effect when `CYRMaintenanceScript.Init()` runs, at new-game start; a
loaded save keeps the property values it stored. A 2026-11-12 check on loaded saves (both `Papyrus.N.log` sessions show
"loaded from save" lines) proved nothing either way. On that save `CYRStatsQuest` (1607CADF) is running and
`SurvivalModeInitialized` is True, and `ChildMaleMiscs` / `ChildFemaleMiscs` print as `[]` in `sqv`, which is expected
for a save that predates the fix. Pending: a new game with this plugin, then `quest 0x1607CADF` and `sqv CYRMaintenance`.

## Limits

- A quest's script properties are stored in the save. On an existing save the arrays keep the values they had; the fix is
  for a new game. The function runs once, at start-up.
- Whether the error also stopped the rest of `Init()` (currency conversion, survival-mode setup, `CYRStatsQuest`) is not
  established; check `CYRStatsQuest` `IsRunning` live with and without this plugin.
- If a Bruma hotfix binds the arrays itself, remove this plugin.
- Not fixed here: the three stale `CYR_QF_CYRHousePurchase` properties (warnings only), the `BSKInit` `SendStoryEvent`
  start-up error, and three BSK script classes that nothing installed ships.

## Build

    python3 build.py          # dry run: serializes inputs/BSHeartland.esm (once, about 256 MB in build/), prints the change
    python3 build.py --write  # writes dist/, round-trips it, checks header, masters and the YAML

`inputs/BSHeartland.esm` is Bruma 2.0.0's plugin, pinned by `inputs.sha256`, not committed. Needs the Skyrim AI toolkit's
`tools/spriggit-cli.sh` (`SKYRIM_TOOLKIT` overrides its path).

## Install

Copy `dist/Beyond Skyrim - Bruma 2 - Child Clothing Fix.esp` into a mod of its own in MO2, for example `Beyond Skyrim - Bruma 2 - Child Clothing Fix`. The
plugin masters `BSHeartland.esm`, so LOOT sorts it after Bruma. It is ESL-flagged (it adds no new record).
