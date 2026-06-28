"""Screen classes for different game views."""

from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

from rpg.ui.widgets import (
    create_stat_panel,
    create_quest_panel,
    create_location_panel,
    create_map_view,
    create_event_log,
    create_dialogue_view,
)


class ExploreScreen:
    """Main exploration screen."""

    def __init__(self, game_state):
        self.state = game_state

    def render(self, console: Console) -> None:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=10),
        )

        player = self.state.player
        region = player.location
        world = self.state.world

        npcs_here = [n for n in self.state.npcs if n.location_id == region.id]
        active_quests = [q for q in self.state.quests if q.is_active]

        layout["header"].update(
            Panel(
                f"[bold cyan]{world.name}[/] — Turn {self.state.turn_count}",
                border_style="bright_blue",
            )
        )

        body = Layout(name="body")
        body.split_row(
            Layout(name="map", ratio=2),
            Layout(name="sidebar", ratio=1),
        )

        body["map"].update(
            Panel(
                create_map_view(world, region, console.width or 80),
                border_style="bright_blue",
                title="WORLD MAP",
            )
        )

        sidebar = Layout(name="sidebar")
        sidebar.split_column(
            Layout(create_stat_panel(player)),
            Layout(create_quest_panel(active_quests)),
            Layout(create_location_panel(region, npcs_here, [])),
        )
        body["sidebar"].update(sidebar)

        layout["body"].update(body)
        layout["footer"].update(create_event_log(self.state.event_log))

        console.clear()
        console.print(layout)


class DialogueScreen:
    """Dialogue screen."""

    def __init__(self, dialogue_state):
        self.dialogue_state = dialogue_state

    def render(self, console: Console) -> None:
        console.clear()
        console.print(create_dialogue_view(self.dialogue_state))
