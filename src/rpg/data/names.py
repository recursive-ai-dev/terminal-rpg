"""Name generation pools."""

import random


FACTION_PREFIXES = [
    "Iron", "Silver", "Golden", "Crimson", "Shadow", "Storm",
    "Frost", "Ember", "Dark", "Bright", "Wild", "Ancient",
    "Shattered", "Ethereal", "Hallowed", "Obsidian", "Celestial", "Abyssal"
]

FACTION_SUFFIXES = [
    "Brotherhood", "Order", "Guild", "Circle", "Clan", "Legion",
    "Covenant", "Syndicate", "Alliance", "Watch", "Guard", "Hand",
    "Dominion", "Collective", "Pact", "Tribunal", "Ascendancy", "Inquisition"
]

NPC_FIRST_NAMES = [
    "Aldric", "Brenna", "Cedric", "Dahlia", "Eldrin", "Freya",
    "Gareth", "Helena", "Ivor", "Juno", "Kael", "Lyra",
    "Mira", "Nolan", "Orla", "Piers", "Quinn", "Rowan",
    "Sera", "Tobin", "Ulric", "Vera", "Wren", "Xander",
    "Yara", "Zane",
    "Valerius", "Zephyra", "Ignatius", "Seraphina", "Maelor", "Lyrienne"
]

NPC_LAST_NAMES = [
    "Ashford", "Blackwood", "Crowley", "Dunmore", "Everett",
    "Fairchild", "Graves", "Hawthorne", "Ironwood", "Kingsley",
    "Lancaster", "Morrow", "Nightingale", "Oakenshield", "Preston",
    "Ravenswood", "Stone", "Thorne", "Underhill", "Vaughn",
    "Whitmore", "York", "Zephyr",
    "Stormrider", "Voidwalker", "Starcaller", "Bloodborne", "Frostweaver"
]

NPC_TITLES = [
    "the Brave", "the Wise", "the Cunning", "the Grim",
    "the Gentle", "the Swift", "the Bold", "the Silent",
    "the Forsaken", "the Undying", "the Betrayer", "the Architect",
    "Voice of the Ancestors", "the Exile", "the Unseen",
    "", "", "",  # Reduced chance of no title to make world more colorful
]


def generate_faction_name(rng: random.Random) -> str:
    return f"{rng.choice(FACTION_PREFIXES)} {rng.choice(FACTION_SUFFIXES)}"


def generate_npc_name(rng: random.Random) -> str:
    first = rng.choice(NPC_FIRST_NAMES)
    last = rng.choice(NPC_LAST_NAMES)
    title = rng.choice(NPC_TITLES)
    if title:
        return f"{first} {last} {title}"
    return f"{first} {last}"
