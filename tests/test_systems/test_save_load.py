"""Tests for save/load system."""

import json
from pathlib import Path
from unittest.mock import patch

from rpg.models.core import GameState, Player
from rpg.systems.save_load import save_game, load_game, list_saves


def test_save_and_load(tmp_path):
    with patch("rpg.systems.save_load.SAVE_DIR", tmp_path):
        state = GameState(seed="test-seed")
        state.player = Player(name="TestPlayer", hp=80)
        state.turn_count = 42

        save_game(state, "test_save.json")
        loaded = load_game("test_save.json")

        assert loaded is not None
        assert loaded.player.name == "TestPlayer"
        assert loaded.player.hp == 80
        assert loaded.turn_count == 42


def test_load_nonexistent():
    result = load_game("does_not_exist.json")
    assert result is None


def test_list_saves(tmp_path):
    with patch("rpg.systems.save_load.SAVE_DIR", tmp_path):
        # Create a fake save
        (tmp_path / "save_test.json").write_text("{}")
        saves = list_saves()
        assert len(saves) == 1
        assert saves[0]["filename"] == "save_test.json"
