"""Item generation pools."""

import random


WEAPON_NAMES = [
    "Rusty Sword", "Iron Dagger", "Steel Blade", "War Hammer", "Battle Axe",
    "Hunting Bow", "Magic Staff", "Spear", "Mace", "Longsword",
]

ARMOR_NAMES = [
    "Leather Armor", "Chain Mail", "Plate Armor", "Wooden Shield", "Iron Shield",
    "Cloak", "Helmet", "Gauntlets",
]

CONSUMABLE_NAMES = [
    "Health Potion", "Antidote", "Rations", "Stamina Tonic", "Elixir",
    "Bandages", "Magic Scroll",
]

MISC_NAMES = [
    "Old Map", "Strange Key", "Gemstone", "Gold Coins", "Silver Ring",
    "Ancient Tome", "Herb Bundle",
]


def generate_item(rng: random.Random, item_type: str | None = None) -> "Item":
    """Generate a random item."""
    from rpg.models.core import Item

    if item_type is None:
        item_type = rng.choice(["weapon", "armor", "consumable", "misc"])

    name_pools = {
        "weapon": WEAPON_NAMES,
        "armor": ARMOR_NAMES,
        "consumable": CONSUMABLE_NAMES,
        "misc": MISC_NAMES,
    }

    name = rng.choice(name_pools.get(item_type, MISC_NAMES))
    value = rng.randint(5, 50)

    stats = {}
    if item_type == "weapon":
        stats["attack"] = rng.randint(2, 10)
    elif item_type == "armor":
        stats["defense"] = rng.randint(1, 8)

    return Item(name=name, item_type=item_type, value=value, stats=stats)
