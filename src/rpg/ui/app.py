"""Main application loop."""

from __future__ import annotations

from rich.console import Console

from rpg.models.core import GameState
from rpg.ui.screens import ExploreScreen


class GameApp:
    """Main game application."""

    def __init__(self, state: GameState):
        self.state = state
        self.console = Console()
        self.running = True

    def run(self) -> None:
        """Main game loop."""
        self.console.print("[bold green]Welcome to Terminal RPG![/]")
        self.console.print("[dim]Use h/j/k/l or arrow keys to move. 'q' to quit.[/]")
        self.console.print()

        while self.running:
            self.render()
            self.handle_input()

    def render(self) -> None:
        """Render current screen."""
        screen = ExploreScreen(self.state)
        screen.render(self.console)

    def handle_input(self) -> None:
        """Handle player input."""
        try:
            key = self.console.input("[bold yellow]> [/]")
            key = key.strip().lower()

            if key == "q":
                self.running = False
                self.console.print("[dim]Thanks for playing![/]")
            elif key in ("h", "left", "a"):
                self.move_player("west")
            elif key in ("l", "right", "d"):
                self.move_player("east")
            elif key in ("k", "up", "w"):
                self.move_player("north")
            elif key in ("j", "down", "s"):
                self.move_player("south")
            elif key == "i":
                self.show_inventory()
            elif key == "t":
                self.interact()
            elif key == "m":
                self.show_full_map()
            else:
                self.console.print("[dim]Unknown command. Use h/j/k/l to move, q to quit.[/]")
        except (KeyboardInterrupt, EOFError):
            self.running = False

    def move_player(self, direction: str) -> None:
        """Move player in direction."""
        player = self.state.player
        world = self.state.world
        current = player.location

        if current is None:
            self.state.log_event("You have no location set.")
            return

        neighbors = world.get_neighbors(current.id)
        if not neighbors:
            self.state.log_event("You cannot move from here.")
            return

        if direction == "north":
            target = next((n for n in neighbors if n.y < current.y), neighbors[0])
        elif direction == "south":
            target = next((n for n in neighbors if n.y > current.y), neighbors[0])
        elif direction == "west":
            target = next((n for n in neighbors if n.x < current.x), neighbors[0])
        elif direction == "east":
            target = next((n for n in neighbors if n.x > current.x), neighbors[0])
        else:
            target = neighbors[0]

        player.location = target
        target.visited = True
        self.state.turn_count += 1
        self.state.log_event(f"You travel to {target.name}")

    def show_inventory(self) -> None:
        """Show inventory."""
        player = self.state.player
        if not player.inventory:
            self.console.print("[dim]Inventory is empty.[/]")
        else:
            self.console.print("[bold]Inventory:[/]")
            for item in player.inventory:
                self.console.print(f"  • {item.name} ({item.item_type}) x{item.quantity}")

    def interact(self) -> None:
        """Interact with NPCs in current region."""
        npcs_here = [n for n in self.state.npcs if n.location_id == self.state.player.location.id]
        if not npcs_here:
            self.console.print("[dim]No one to talk to here.[/]")
        else:
            npc = npcs_here[0]
            self.console.print(f"[bold]{npc.name}[/]: {npc.dialogue[0] if npc.dialogue else '...'}")

    def show_full_map(self) -> None:
        """Show full map view."""
        from rpg.ui.widgets import create_map_view
        self.console.print(create_map_view(self.state.world, self.state.player.location))
