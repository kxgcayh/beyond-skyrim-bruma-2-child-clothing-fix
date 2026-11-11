# Bruma 2 Child Clothing Fix

Private pre-release (v0.1.0). One override of the quest `CYRMaintenance` (`001961:BSHeartland.esm`) for Beyond
Skyrim - Bruma 2.0.0 (Nexus 10917).

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

Tested 2026-11-12 on a new game (Bruma 2.0.0, Assets SE): the 3 `Cannot access an element of a None array` lines are
gone and no new CYR or Bruma errors appeared in `Papyrus.0.log`. `CYRStatsQuest` `IsRunning` and full `Init()`
completion are not verified (DevBench was down).

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

Copy `dist/Bruma 2 - Child Clothing Fix.esp` into a mod of its own in MO2, for example `Bruma 2 Child Clothing Fix`. The
plugin masters `BSHeartland.esm`, so LOOT sorts it after Bruma. It is ESL-flagged (it adds no new record).
