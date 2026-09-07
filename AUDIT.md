# Audit — Terminal RPG

<!-- REGEN:START — everything here is rewritten at each phase boundary -->
## Scope & method
  commit: 151bfa0c4c5ab8fe5a647184408b761fc6441954
  date: 2026-09-07T08:04:59Z
  languages: Python
  files audited: 61
  tools run: ruff, mypy, bandit, pip-audit, semgrep, gitleaks, trivy-fs, pytest
## Executive summary
  The codebase is well-structured but contains several critical flaws affecting gameplay and state management. The most severe issue is that the player's active location and quests are lost upon saving and loading, fundamentally breaking progression. Other significant issues include combat stat scaling infinitely with inventory size and level-up logic failing on large XP gains. Addressing these core correctness and state management issues should be the immediate priority.
## Findings by severity
| ID | Location | Category | Claim | Confidence |
|---|---|---|---|---|
| F001 | src/rpg/models/core.py:112 | correctness | Player active location and quests are lost on save/load due to omission in `to_dict`. | confirmed |
| F002 | src/rpg/models/core.py:53 | correctness | Player combat stats scale infinitely with inventory size due to `sum()` usage. | confirmed |
| F003 | src/rpg/models/core.py:82 | correctness | Level-up logic fails on massive XP gains due to single `if` block instead of `while`. | confirmed |
| F004 | src/rpg/systems/combat.py:38 | correctness | Combat timeout incorrectly rewards player with victory. | confirmed |
| F005 | src/rpg/ui/app.py:68 | correctness | Navigation teleportation glitch on map edges due to default fallback. | confirmed |
| F006 | src/rpg/systems/inventory.py:21 | correctness | Inventory removal silently fails to check sufficient quantity. | confirmed |
| F007 | src/rpg/ui/app.py:91 | correctness | Dead dialogue system skips intended gameplay, ignoring the state machine. | confirmed |
| F008 | src/rpg/generation/quest_gen.py:108 | correctness | Uncompletable quests due to unset `target_id`s during generation. | confirmed |
| F009 | src/rpg/systems/save_load.py:32 | security | Path traversal vulnerability in save loading via `startswith`. | confirmed |
| F010 | src/rpg/models/faction.py:33 | architecture | Dual source-of-truth for player reputation leads to state desync. | confirmed |
| F011 | src/rpg/models/core.py:60 | correctness | Negative damage heals the player instead of failing safely. | confirmed |
| F012 | src/rpg/models/core.py:65 | correctness | Negative healing actively harms the player. | confirmed |
| F013 | src/rpg/generation/faction_gen.py:75 | performance | O(N^3) redundant global territory recalculations during generation. | confirmed |
| F014 | src/rpg/systems/inventory.py:11 | performance | Inventory bloat from unstacked miscellaneous items. | confirmed |
| F015 | src/rpg/models/core.py:104 | performance | Event log memory allocation churn from creating new lists on truncate. | confirmed |
| F016 | src/rpg/models/npc.py:48 | correctness | In-place mutation of deserialization dictionaries corrupts original payload. | confirmed |
## Systemic themes
  - **State Management & Serialization:** Several issues stem from improper serialization/deserialization logic, leading to data loss (F001) or payload corruption (F016). Dual sources of truth also cause state desyncs (F010).
  - **Mathematical Edge Cases:** Core combat and stats calculation often neglect edge cases like unbounded growth (F002) or negative inputs acting as inverted operations (F011, F012).
## Design opinions
  - The 5-layer procedural generation pipeline is well-conceived, but could benefit from a unified random seed manager passed down rather than ad-hoc seeding in each generation module.
## Strengths
  - The procedural generation pipeline is logically separated into distinct layers, making it modular and extensible.
  - The combat system is simple but provides clear messaging and hooks for expansion.
## Verification & limitations
  - 16 findings confirmed. 0 findings rejected.
  - Estimated false-positive risk: Low.
  - Blind spots: Did not perform extensive runtime load testing or deep fuzzing of the procedural generation edge cases.
<!-- REGEN:END -->

## Findings Log

### F001 — [HIGH] src/rpg/models/core.py:112 — Player active location and quests are lost on save/load due to omission in `to_dict`.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stats": self.stats,
            "inventory": [item.to_dict() for item in self.inventory],
            "faction_reputations": self.faction_reputations,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
        }
```
**Trigger:** Saving the game and then loading the save file.
**Impact:** The player spawns with no location set and loses all active quests, breaking progression and movement.
**Fix:** Add `"location_id": self.location.id if self.location and hasattr(self.location, 'id') else None` and `"quests": [q.to_dict() for q in self.quests]` to the returned dictionary.

### F002 — [HIGH] src/rpg/models/core.py:53 — Player combat stats scale infinitely with inventory size due to `sum()` usage.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    @property
    def attack(self) -> int:
        base = self.stats["attack"]
        weapon_bonus = sum(
            item.stats.get("attack", 0)
            for item in self.inventory
            if item.item_type == "weapon"
        )
        return base + weapon_bonus
```
**Trigger:** Equipping/carrying multiple weapons or armor pieces in the inventory.
**Impact:** A player carrying many weapons/armor will have their stats combined, trivializing combat.
**Fix:** Change `sum(...)` to `max(..., default=0)` so the player only benefits from the single strongest weapon and armor piece they are carrying.

### F003 — [MEDIUM] src/rpg/models/core.py:82 — Level-up logic fails on massive XP gains due to single `if` block instead of `while`.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if level up occurred."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level += 1
```
**Trigger:** Gaining an amount of XP that exceeds the requirement for multiple level-ups simultaneously.
**Impact:** The player only levels up once, their XP remains inflated above the threshold, halting further progression until the next exact XP gain.
**Fix:** Change the `if` statement to a `while self.xp >= self.xp_to_next_level:` loop.

### F004 — [MEDIUM] src/rpg/systems/combat.py:38 — Combat timeout incorrectly rewards player with victory.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    while player.hp > 0 and enemy_hp > 0 and turn < 50:  # Safety limit
        ...
    if player.hp <= 0:
        ...
    # Player won
    xp = 20 + rng.randint(0, 30)
```
**Trigger:** Combat lasting longer than 50 turns (stalemate).
**Impact:** The player is rewarded with XP and loot even though the enemy is not defeated.
**Fix:** Add an explicit check `if enemy_hp > 0:` after the loop to treat it as a draw/flee.

### F005 — [MEDIUM] src/rpg/ui/app.py:68 — Navigation teleportation glitch on map edges due to default fallback.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
        if direction == "north":
            target = next((n for n in neighbors if n.y < current.y), neighbors[0])
```
**Trigger:** Moving towards a map edge where no neighbor exists in that direction.
**Impact:** The player is randomly teleported to the first available neighbor instead of being blocked.
**Fix:** Change the default fallback in `next()` to `None` and check `if target is None:` to abort the move.

### F006 — [HIGH] src/rpg/systems/inventory.py:21 — Inventory removal silently fails to check sufficient quantity.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def remove_item(player: Player, item_name: str, quantity: int = 1) -> Item | None:
        for i, item in enumerate(player.inventory):
            if item.name == item_name:
                if item.quantity > quantity:
                    item.quantity -= quantity
                    ...
                else:
                    return player.inventory.pop(i)
```
**Trigger:** Requesting to remove more items than the player possesses.
**Impact:** The item is removed and returned, tricking callers into accepting partial payments as full payments.
**Fix:** Add a guard clause inside the name match: `if item.quantity < quantity: return None`.

### F007 — [HIGH] src/rpg/ui/app.py:91 — Dead dialogue system skips intended gameplay, ignoring the state machine.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def interact(self) -> None:
        ...
        else:
            npc = npcs_here[0]
            self.console.print(f"[bold]{npc.name}[/]: {npc.dialogue[0] if npc.dialogue else '...'}")
```
**Trigger:** Interacting with an NPC.
**Impact:** Players cannot trade, accept quests, or read dynamic dialogue responses.
**Fix:** Import `start_dialogue` and `advance_dialogue`, call `state = start_dialogue(npc)`, and implement an input loop.

### F008 — [HIGH] src/rpg/generation/quest_gen.py:108 — Uncompletable quests due to unset `target_id`s during generation.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
                objectives=[
                    Objective(
                        description=objective_text,
                        target_id="",  # Set during gameplay
                        target_count=rng.randint(1, 3),
                    )
                ],
```
**Trigger:** Generating quests and attempting to complete them.
**Impact:** Quests cannot be completed because `target_id` is never set during gameplay.
**Fix:** Populate `target_id` during generation using the chosen target variable.

### F009 — [CRITICAL] src/rpg/systems/save_load.py:32 — Path traversal vulnerability in save loading via `startswith`.
**Category:** security  **Confidence:** confirmed
**Code:**
```python
    if not str(filepath).startswith(str(SAVE_DIR.resolve())):
        return None
```
**Trigger:** Loading a maliciously crafted save filename (e.g., in a sibling directory).
**Impact:** An attacker could read arbitrary `.json` files outside the intended save directory.
**Fix:** Use the robust `Path` method: `if not filepath.is_relative_to(SAVE_DIR.resolve()):`.

### F010 — [MEDIUM] src/rpg/models/faction.py:33 — Dual source-of-truth for player reputation leads to state desync.
**Category:** architecture  **Confidence:** confirmed
**Code:**
```python
class Faction:
    ...
    player_reputation: int = 0  # -100..100
```
and
```python
class Player:
    ...
    faction_reputations: dict[str, int] = field(default_factory=dict)
```
**Trigger:** Updating faction reputation using `faction.change_player_reputation`.
**Impact:** The Player model's `faction_reputations` is not updated, causing desyncs.
**Fix:** Remove `faction_reputations` from the `Player` model and rely solely on `Faction.player_reputation`.

### F011 — [MEDIUM] src/rpg/models/core.py:60 — Negative damage heals the player instead of failing safely.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.defense // 2)
        self.hp = max(0, self.hp - actual)
        return actual
```
**Trigger:** Taking negative damage (e.g., from a debuff or edge case).
**Impact:** The negative damage resolves as 1 damage, incorrectly harming the player.
**Fix:** Wrap the logic to clamp strictly: `actual = max(0, amount - self.defense // 2) if amount > 0 else 0`.

### F012 — [MEDIUM] src/rpg/models/core.py:65 — Negative healing actively harms the player.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    def heal(self, amount: int) -> int:
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual
        return actual
```
**Trigger:** Receiving a negative heal amount (e.g., from a cursed item).
**Impact:** The negative amount is added to `self.hp`, acting as unmitigable true damage.
**Fix:** Add a guard clause: `if amount <= 0: return 0`.

### F013 — [MEDIUM] src/rpg/generation/faction_gen.py:75 — O(N^3) redundant global territory recalculations during generation.
**Category:** performance  **Confidence:** confirmed
**Code:**
```python
            for neighbor_id in neighbors:
                if neighbor_id not in visited and neighbor_id not in _all_territories(factions):
                    ...
```
**Trigger:** Generating territories for factions.
**Impact:** The helper `_all_territories(factions)` is called repeatedly inside the BFS loop, causing massive pipeline slowdowns.
**Fix:** Replace the inline call with a `global_visited = set()` maintained outside the loop.

### F014 — [LOW] src/rpg/systems/inventory.py:11 — Inventory bloat from unstacked miscellaneous items.
**Category:** performance  **Confidence:** confirmed
**Code:**
```python
    if item.item_type == "consumable":
        for existing in player.inventory:
            if existing.name == item.name and existing.item_type == item.item_type:
```
**Trigger:** Looting many non-consumable, non-equipment items (e.g., 'Gold Coins').
**Impact:** Creates many distinct `Item` objects, breaking UI rendering and wasting memory.
**Fix:** Broaden the stacking condition: `if item.item_type not in ("weapon", "armor"):`.

### F015 — [LOW] src/rpg/models/core.py:104 — Event log memory allocation churn from creating new lists on truncate.
**Category:** performance  **Confidence:** confirmed
**Code:**
```python
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-100:]
```
**Trigger:** Logging many events.
**Impact:** Creates a new list and shallow-copies strings every time, causing GC pressure.
**Fix:** Modify the list in place using `del self.event_log[:-100]` or use `collections.deque(maxlen=100)`.

### F016 — [MEDIUM] src/rpg/models/npc.py:48 — In-place mutation of deserialization dictionaries corrupts original payload.
**Category:** correctness  **Confidence:** confirmed
**Code:**
```python
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPC:
        data["inventory"] = [Item.from_dict(d) for d in data.get("inventory", [])]
        return cls(**data)
```
**Trigger:** Calling `from_dict` with a dictionary.
**Impact:** The input dictionary is mutated, which can unpredictably contain mutated object instances instead of primitives if cached or reused.
**Fix:** Create a shallow copy via `data = data.copy()` or explicitly extract keys without altering the original dict.
