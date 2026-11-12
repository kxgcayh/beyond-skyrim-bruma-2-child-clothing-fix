# Beyond Skyrim - Bruma 2 - Child Clothing Fix

Release v0.1.2 (published 2026-11-12; v0.1.0 and v0.1.1 are older releases). One override of the quest `CYRMaintenance` (`001961:BSHeartland.esm`) for Beyond
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

A second property of the same quest is never set: `CYRMaintenanceScript.CYRAyleidUndeadFriendFaction`, although the
faction exists (`CYRAyleidUndeadFriendFaction`, `0B555D:BSHeartland.esm`, which already lists the Bruma Ayleid factions and
`BSKRatFaction` as friends). `SetupFactionRelationships()` calls `BSKRatFaction.SetAlly(CYRAyleidUndeadFriendFaction, ...)`,
so every new game logs `Cannot be an ally of a None faction` and the rat faction is never made an ally of it.

## Change

The two arrays are bound to the gift items of the same colour, in the order of `childClothing`:

| childClothing | ChildMaleMiscs | ChildFemaleMiscs |
|---|---|---|
| `CYRClothesChildBlue` (`1BD173`) | `CYRClothesChildBlueMale` (`1D99E9`) | `CYRClothesChildBlueFemale` (`1D99E7`) |
| `CYRClothesChildPurple` (`1F1541`) | `CYRClothesChildPurpleMale` (`1D99E8`) | `CYRClothesChildPurpleFemale` (`1D99E6`) |
| `CYRClothesChildTurquoise` (`1BD172`) | `CYRClothesChildTurquoiseMale` (`1D99EA`) | `CYRClothesChildTurquoiseFemale` (`1D99E5`) |

`CYRAyleidUndeadFriendFaction` is bound to `0B555D:BSHeartland.esm` (the faction of that name).

The pairing by colour and gender is an inference: the author left the arrays empty. Nothing else in the quest changes
(`build/review.diff` after a build).

## Test status

Tested 2026-11-12 on a new game (Bruma 2.0.0, Assets SE) through DevBench, v0.1.2. `sqv CYRMaintenance` shows
`ChildMaleMiscs = [161D99E9, 161D99E8, 161D99EA]`, `ChildFemaleMiscs = [161D99E7, 161D99E6, 161D99E5]` and
`CYRAyleidUndeadFriendFaction = 160B555D`; `CYRStatsQuest` (1607CADF) is running and `SurvivalModeInitialized` is True.
`Papyrus.0.log` has no `Cannot be an ally of a None faction` line and no `CYRMaintenanceScript` stack frame at all. The
`Cannot access an element of a None array` lines in that session come from SkyUI favourites and `PSDI_ScriptMcm`.
Before the fixes a loaded save shows both Misc arrays as `[]`, and the faction property as unset.

Left unset on purpose, because nothing exists to bind: `CYRCrowsWoodWorld` and `CYRTestWorld` (no worldspace record;
`SetupFormlists()` calls `AddForm(None)` on them) and `CYRLeyawiinRepublicGold001` (no record; `SetupCurrencyConversion()`
tests it for None first).

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

## Credits and Permissions

Checked on 2026-11-13 against each mod's Nexus permission block and author notes, not its description or readme. The plugin is derived from the mods below and stays under their authors' terms.

| Mod | Author | What the Nexus page says | Status |
|---|---|---|---|
| [Beyond Skyrim - Bruma SE](https://www.nexusmods.com/skyrimspecialedition/mods/10917) | The Beyond Skyrim - Cyrodiil Development Team | No permission block. Author notes: addons and compatibility patches may be distributed, and fixes should be shared with the team first; the full mod and resources made for Beyond Skyrim may not be redistributed. | allowed |
| [Beyond Skyrim - Assets SE](https://www.nexusmods.com/skyrimspecialedition/mods/198585) | BeyondSkyrimDC | No permission block. Author notes: as Beyond Skyrim - Bruma SE (compatibility patches allowed; the full mod and its resources may not be redistributed). | allowed |

Every source allows a patch like this with credit; credit the authors above when publishing. Beyond Skyrim asks that fixes be shared with its team first.
