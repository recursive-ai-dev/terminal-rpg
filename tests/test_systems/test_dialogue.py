"""Tests for dialogue system."""

from rpg.models.npc import NPC
from rpg.systems.dialogue import start_dialogue, advance_dialogue


def test_start_dialogue():
    npc = NPC(id="npc_0", name="Test", role="merchant", dialogue=["Hello", "Browse my wares"])
    state = start_dialogue(npc)
    assert state.npc == npc
    assert state.current_line == "Hello"
    assert "Trade" in state.choices


def test_leave_dialogue():
    npc = NPC(id="npc_0", name="Test", role="neutral", dialogue=["Hi"])
    state = start_dialogue(npc)
    state = advance_dialogue(state, "Leave")
    assert state.finished is True


def test_quest_giver_dialogue():
    npc = NPC(id="npc_0", name="Test", role="quest_giver", dialogue=["Need help?"])
    state = start_dialogue(npc)
    state = advance_dialogue(state, "Ask for work")
    assert state.quest_offered is not None
