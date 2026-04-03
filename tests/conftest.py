"""Shared pytest fixtures."""

import pytest
from rpg.models.core import Player, Item, GameState


@pytest.fixture
def player():
    """Return a default player."""
    return Player(name="TestPlayer")


@pytest.fixture
def game_state():
    """Return a default game state."""
    return GameState(seed="test-seed-123")


@pytest.fixture
def sample_items():
    """Return a list of sample items."""
    return [
        Item(name="Rusty Sword", item_type="weapon", value=10, stats={"attack": 5}),
        Item(name="Wooden Shield", item_type="armor", value=8, stats={"defense": 3}),
        Item(name="Health Potion", item_type="consumable", value=25, quantity=3),
    ]
