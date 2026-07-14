# Code Quality Audit

1. **Player active location and quests lost on save/load** (Real Bug)
   - **Files:** `src/rpg/models/core.py` (lines ~86-97, `Player.to_dict`)
   - **Problem:** The `Player.to_dict()` method entirely omits the `location` and `quests` fields from the returned dictionary.
   - **Why it matters:** Loading a saved game wipes the player's active quests and spawns them with `location = None`, breaking movement and region-specific interactions.
   - **Proposed Fix:** Add `"location_id": self.location.id if self.location and hasattr(self.location, 'id') else None` and `"quests": [q.to_dict() for q in self.quests]` to the returned dictionary.
   - **Overlap:** Impacts `Player.from_dict` as well (needs to read these keys).

2. **Player combat stats incorrectly scale infinitely with inventory size** (Real Bug)
   - **Files:** `src/rpg/models/core.py` (lines ~43, 53, `Player.attack`, `Player.defense`)
   - **Problem:** The `attack` and `defense` properties use `sum()` to combine the stats of every single weapon and armor piece in the player's inventory.
   - **Why it matters:** A player carrying 20 unequipped "Rusty Swords" will have the combined attack power of all 20 swords, mathematically breaking and trivializing combat.
   - **Proposed Fix:** Change `sum(...)` to `max(..., default=0)` so the player only benefits from the single strongest weapon and armor piece they are carrying.

3. **Level-up logic fails on massive XP gains** (Real Bug)
   - **Files:** `src/rpg/models/core.py` (lines ~69-79, `Player.add_xp`)
   - **Problem:** `add_xp` uses a single `if self.xp >= self.xp_to_next_level:` block to handle leveling up.
   - **Why it matters:** If an event or combat grants enough XP to level up multiple times at once, the player only levels up once. Their XP remains inflated above the threshold, halting further progression until the next exact XP gain.
   - **Proposed Fix:** Change the `if` statement to a `while self.xp >= self.xp_to_next_level:` loop, keeping a boolean flag to track if at least one level-up occurred to return `True`.

4. **Combat timeout incorrectly rewards player with victory** (Real Bug)
   - **Files:** `src/rpg/systems/combat.py` (lines ~31-50, `resolve_combat`)
   - **Problem:** The combat `while` loop has a safety limit of `turn < 50`. If the loop exits due to this timeout, the code falls through to the "Player won" block because `player.hp <= 0` is false.
   - **Why it matters:** A combat stalemate (e.g. low damage, high HP combatants) rewards the player with free XP and loot even though the enemy is still alive.
   - **Proposed Fix:** After the loop, add an explicit check `if enemy_hp > 0:`. If true, treat it as a draw/flee, returning `CombatResult(player_won=False, ...)` with a "Combat timed out" message.

5. **Navigation teleportation glitch on map edges** (Real Bug)
   - **Files:** `src/rpg/ui/app.py` (lines ~61-75, `move_player`)
   - **Problem:** When determining the target region, `next((n for n in neighbors if n.y < current.y), neighbors[0])` defaults to the first available neighbor if no region exists in the chosen direction.
   - **Why it matters:** Pressing 'north' at the top edge of the map will randomly move the player south, east, or west rather than blocking the invalid movement.
   - **Proposed Fix:** Change the default fallback in `next()` to `None`. Check `if target is None:`, and if so, abort the move and log "You cannot go that way."

6. **Inventory removal silently fails to check sufficient quantity** (Real Bug)
   - **Files:** `src/rpg/systems/inventory.py` (lines ~18-28, `remove_item`)
   - **Problem:** If `item.quantity <= quantity`, the item is completely popped from the inventory and returned as-is, without verifying if the requested quantity was actually fulfilled.
   - **Why it matters:** A caller asking to remove 5 items will succeed even if the player only has 1, tricking quests or shops into accepting partial payments as full payments.
   - **Proposed Fix:** Add a guard clause inside the name match: `if item.quantity < quantity: return None` before modifying or popping the item.

7. **Dead dialogue system skips intended gameplay** (Dead Code)
   - **Files:** `src/rpg/ui/app.py` (lines ~90-96, `interact`)
   - **Problem:** `interact()` entirely ignores the robust dialogue state machine built in `src/rpg/systems/dialogue.py`, and manually prints only the first line of the NPC's dialogue array.
   - **Why it matters:** Players can never trade, accept quests, or read dynamic dialogue responses because the logic chain linking the UI to the dialogue system is fully disconnected.
   - **Proposed Fix:** Import `start_dialogue` and `advance_dialogue`. Call `state = start_dialogue(npc)` and implement a short input loop checking `state.choices` until `state.finished` is true.

8. **Uncompletable quests due to unset target IDs** (Dead Code / Correctness)
   - **Files:** `src/rpg/generation/quest_gen.py` (lines ~107, `generate_quests`)
   - **Problem:** Quests are generated with `target_id=""`. The comment notes "Set during gameplay", but there is no logic in the codebase that ever assigns these IDs.
   - **Why it matters:** The `Quest.advance_objective` method requires an exact non-empty `target_id` match. Since targets are empty, no generated quests can ever progress or be completed.
   - **Proposed Fix:** Populate `target_id` during generation by injecting the selected `ITEM_TARGETS` or `ENEMY_TYPES` variable directly into the `Objective` constructor.

9. **Path traversal vulnerability in save loading** (Resilience)
   - **Files:** `src/rpg/systems/save_load.py` (lines ~29-31, `load_game`)
   - **Problem:** The path security check `str(filepath).startswith(str(SAVE_DIR.resolve()))` allows sibling directory traversal (e.g., `/saves2/` starts with `/saves`).
   - **Why it matters:** A maliciously crafted save filename can allow the app to read arbitrary `.json` files outside the intended save directory.
   - **Proposed Fix:** Use the robust `Path` method: `if not filepath.is_relative_to(SAVE_DIR.resolve()):` (available in Python 3.9+).

10. **Dual source-of-truth for player reputation** (Correctness Risk)
    - **Files:** `src/rpg/models/faction.py` (line 33) & `src/rpg/models/core.py` (line 37)
    - **Problem:** Reputation is tracked redundantly in both `Faction.player_reputation` and `Player.faction_reputations`. Calling `faction.change_player_reputation` only updates the Faction model.
    - **Why it matters:** The state easily desyncs, meaning UI screens reading from the Player model will show different reputation values than the Faction logic calculates.
    - **Proposed Fix:** Remove `faction_reputations` from the `Player` model entirely, and rely solely on iterating `Faction.player_reputation` when checking standings.
    - **Overlap:** Touches `core.py` Player class.

11. **Negative damage heals the player instead of failing safely** (Resilience)
    - **Files:** `src/rpg/models/core.py` (lines ~58-61, `take_damage`)
    - **Problem:** `actual = max(1, amount - self.defense // 2)` forces negative incoming damage to resolve as exactly 1 damage instead of 0.
    - **Why it matters:** If an intended debuff or mathematical edge case applies negative damage, it will bypass intended behavior and whittle away 1 HP per tick.
    - **Proposed Fix:** Wrap the logic to clamp strictly: `actual = max(0, amount - self.defense // 2) if amount > 0 else 0`.

12. **Negative healing actively harms the player** (Resilience)
    - **Files:** `src/rpg/models/core.py` (lines ~63-67, `heal`)
    - **Problem:** `actual = min(amount, self.max_hp - self.hp)` allows negative amounts to resolve to negative numbers, which are then added to `self.hp`.
    - **Why it matters:** A bugged consumable or cursed item attempting to heal for a negative amount will silently act as unmitigable true damage.
    - **Proposed Fix:** Add a guard clause at the start of the method: `if amount <= 0: return 0`.

13. **O(N^3) redundant global territory recalculations** (Redundant Work)
    - **Files:** `src/rpg/generation/faction_gen.py` (lines ~71-88, `_assign_territories`)
    - **Problem:** The helper `_all_territories(factions)` is called repeatedly inside the inner BFS loop for every single neighboring region.
    - **Why it matters:** Recalculates the exact same global territory sets exponentially during generation, causing massive pipeline slowdowns if map dimensions or faction counts increase.
    - **Proposed Fix:** Replace the inline call with a `global_visited = set()` maintained outside the loop, and update it via `global_visited.add(neighbor_id)` when a territory is claimed.

14. **Inventory bloat from unstacked miscellaneous items** (Redundant Work)
    - **Files:** `src/rpg/systems/inventory.py` (lines ~10-14, `add_item`)
    - **Problem:** `add_item` only checks for existing stacks if `item.item_type == "consumable"`.
    - **Why it matters:** Looting 100 "Gold Coins" creates 100 distinct `Item` objects in the inventory array, breaking UI rendering and wasting memory.
    - **Proposed Fix:** Broaden the stacking condition to group all stackable items: `if item.item_type not in ("weapon", "armor"):`.

15. **Event log memory allocation churn** (Redundant Work)
    - **Files:** `src/rpg/models/core.py` (lines ~102-106, `GameState.log_event`)
    - **Problem:** Truncating the log uses `self.event_log = self.event_log[-100:]`, which creates a brand new list and shallow-copies up to 100 strings into it every single time a message is logged beyond the limit.
    - **Why it matters:** Causes continuous garbage collection pressure and memory churn during extended gameplay.
    - **Proposed Fix:** Modify the list in place using `del self.event_log[:-100]`, or change the field type to `collections.deque(maxlen=100)`.

16. **In-place mutation of deserialization dictionaries** (Correctness Risk)
    - **Files:** `src/rpg/models/npc.py` (lines ~48) & `src/rpg/models/world.py` (line ~55)
    - **Problem:** `from_dict` methods directly modify the passed `data` dictionary (e.g., `data["inventory"] = ...`) before instantiating the class.
    - **Why it matters:** Mutating the input dictionary in-place corrupts the original payload. If the caller loops over or caches the raw JSON data, it will unpredictably contain mutated object instances instead of primitives.
    - **Proposed Fix:** Create a shallow copy via `data = data.copy()` at the start of the method, or explicitly pop/extract the keys without altering the original dict.
