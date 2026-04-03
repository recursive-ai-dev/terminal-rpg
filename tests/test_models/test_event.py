"""Tests for event model."""

from rpg.models.event import GameEvent


def test_event_creation():
    event = GameEvent(id="e1", event_type="discovery", description="Found something")
    assert event.resolved is False


def test_event_resolve():
    event = GameEvent(id="e1", event_type="combat", description="Fight", consequences={"xp": 50})
    result = event.resolve()
    assert event.resolved is True
    assert result["xp"] == 50


def test_event_serialization():
    event = GameEvent(id="e1", event_type="festival", description="Party", actors=["npc_0", "npc_1"])
    data = event.to_dict()
    restored = GameEvent.from_dict(data)
    assert restored.event_type == "festival"
    assert restored.actors == ["npc_0", "npc_1"]
