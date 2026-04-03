"""Reusable Rich widgets."""

from rich.panel import Panel
from rich.text import Text

from rpg.ui.colors import (
    BIOME_COLOR_MAP, PANEL_BORDER, PLAYER_COLOR,
    HEALTH_HIGH, HEALTH_MEDIUM, HEALTH_LOW,
)


def create_health_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a text-based health bar."""
    if maximum <= 0:
        filled = 0
    else:
        filled = int((current / maximum) * width)
    bar = "█" * filled + "░" * (width - filled)

    if current / maximum > 0.6:
        color = HEALTH_HIGH
    elif current / maximum > 0.3:
        color = HEALTH_MEDIUM
    else:
        color = HEALTH_LOW

    return f"[{color}]{bar}[/{color}]"


def create_stat_panel(player) -> Panel:
    """Create player stats panel."""
    lines = [
        f"[{PLAYER_COLOR}]@ {player.name}[/]",
        f"Level: {player.level}  XP: {player.xp}/{player.xp_to_next_level}",
        f"HP: {create_health_bar(player.hp, player.max_hp)} {player.hp}/{player.max_hp}",
        f"ATK: {player.attack}  DEF: {player.defense}",
        f"Items: {len(player.inventory)}",
    ]
    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="YOU")


def create_quest_panel(quests) -> Panel:
    """Create quest log panel."""
    from rpg.ui.colors import QUEST_COLOR, SUCCESS_COLOR

    active = [q for q in quests if q.is_active]
    if not active:
        content = "[dim]No active quests[/]"
    else:
        lines = []
        for q in active[:3]:
            lines.append(f"[{QUEST_COLOR}]{q.title}[/]")
            for obj in q.objectives:
                status = f"[{SUCCESS_COLOR}]✓[/]" if obj.completed else "○"
                lines.append(f"  {status} {obj.description}")
        content = "\n".join(lines)

    return Panel(content, border_style=PANEL_BORDER, title="QUESTS")


def create_location_panel(region, npcs, events) -> Panel:
    """Create current location info panel."""
    from rpg.ui.colors import BIOME_COLOR_MAP, NPC_COLOR

    biome_color = BIOME_COLOR_MAP.get(region.biome, "white")
    lines = [
        f"[{biome_color}]{region.name}[/]",
        f"Biome: {region.biome}  Danger: {'⚔️' * region.danger_level}",
        f"",
        f"NPCs nearby:",
    ]

    for npc in npcs[:5]:
        lines.append(f"  [{NPC_COLOR}]{npc.name}[/] ({npc.role})")

    if not npcs:
        lines.append("  [dim]None[/]")

    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="HERE")


def create_map_view(world, player_region, console_width: int = 80) -> str:
    """Create ASCII map view centered on player region."""
    regions = world.region_list
    if not regions:
        return "No map data"

    min_x = min(r.x for r in regions)
    max_x = max(r.x for r in regions)
    min_y = min(r.y for r in regions)
    max_y = max(r.y for r in regions)

    grid = {}
    for r in regions:
        grid[(r.x, r.y)] = r

    lines = []
    for y in range(min_y, max_y + 1):
        row = ""
        for x in range(min_x, max_x + 1):
            region = grid.get((x, y))
            if region is None:
                row += "   "
            elif region.id == player_region.id:
                row += "[bold bright_yellow] @ [/]"
            else:
                biome_color = BIOME_COLOR_MAP.get(region.biome, "white")
                symbol = region.biome[:3].upper()[:3]
                row += f"[{biome_color}]{symbol}[/{biome_color}] "
        lines.append(row)

    return "\n".join(lines)


def create_event_log(events: list[str], max_lines: int = 8) -> Panel:
    """Create event log panel."""
    recent = events[-max_lines:] if events else ["[dim]No events yet[/]"]
    content = "\n".join(recent)
    return Panel(content, border_style=PANEL_BORDER, title="EVENT LOG")


def create_dialogue_view(dialogue_state) -> Panel:
    """Create dialogue panel for NPC conversations."""
    lines = [
        f"[bold]{dialogue_state.npc.name}[/] ({dialogue_state.npc.role})",
        f"[italic]\"{dialogue_state.current_line}\"[/]",
        "",
        "Choices:",
    ]
    for i, choice in enumerate(dialogue_state.choices, 1):
        lines.append(f"  {i}. {choice}")

    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="DIALOGUE")
