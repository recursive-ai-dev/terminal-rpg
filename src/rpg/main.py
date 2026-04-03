"""Main entry point for Terminal RPG."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests
from rpg.generation.event_gen import generate_initial_events
from rpg.models.core import GameState, Player
from rpg.systems.save_load import load_game
from rpg.ui.app import GameApp


def generate_new_world(seed: str) -> GameState:
    """Generate a complete new world from seed."""
    world = generate_world_map(seed, width=8, height=6)
    factions = generate_factions(world, count=4)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests)

    player = Player(name="Adventurer")
    start_region = world.region_list[0]
    player.location = start_region
    start_region.visited = True

    state = GameState(
        seed=seed,
        world=world,
        factions=factions,
        npcs=npcs,
        quests=quests,
        events=events,
        player=player,
    )
    state.log_event(f"Welcome to {world.name}!")
    state.log_event(f"You awaken in {start_region.name}.")

    return state


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Terminal RPG - A procedurally generated adventure")
    parser.add_argument("--seed", type=str, help="World generation seed")
    parser.add_argument("--load", type=str, help="Load save file")
    parser.add_argument("--new-game", action="store_true", help="Start new game with random seed")

    args = parser.parse_args()

    console = Console()

    if args.load:
        state = load_game(args.load)
        if state is None:
            console.print(f"[red]Save file not found: {args.load}[/]")
            sys.exit(1)
        console.print(f"[green]Loaded game: {state.seed}[/]")
    else:
        seed = args.seed or f"world-{__import__('random').randint(1000, 9999)}"
        if args.new_game or not args.seed:
            console.print(f"[dim]Generating world with seed: {seed}[/]")
        state = generate_new_world(seed)
        console.print(f"[green]World generated: {state.world.name}[/]")

    app = GameApp(state)
    app.run()


if __name__ == "__main__":
    main()
