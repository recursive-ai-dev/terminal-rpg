"""Save/load system."""

from __future__ import annotations

import json
from pathlib import Path

from rpg.models.core import GameState


SAVE_DIR = Path.home() / ".terminal-rpg" / "saves"


def save_game(state: GameState, filename: str | None = None) -> Path:
    """Save game state to JSON."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    if filename is None:
        # Auto-generate from seed
        filename = f"save_{state.seed}.json"

    filepath = SAVE_DIR / filename
    data = state.to_dict()
    filepath.write_text(json.dumps(data, indent=2))
    return filepath


def load_game(filename: str) -> GameState | None:
    """Load game state from JSON. Returns None if file not found."""
    filepath = SAVE_DIR / filename
    if not filepath.exists():
        return None

    data = json.loads(filepath.read_text())
    return GameState.from_dict(data)


def list_saves() -> list[dict[str, str]]:
    """List available save files."""
    if not SAVE_DIR.exists():
        return []

    saves = []
    for path in sorted(SAVE_DIR.glob("*.json")):
        saves.append({
            "filename": path.name,
            "path": str(path),
        })
    return saves
