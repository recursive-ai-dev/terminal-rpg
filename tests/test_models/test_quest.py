"""Tests for quest model."""

import pytest

from rpg.models.quest import Quest, Objective


def test_objective_creation():
    obj = Objective(description="Test objective", target_id="target1")
    assert obj.description == "Test objective"
    assert obj.completed is False
    assert obj.progress() == 0.0


def test_objective_progress():
    obj = Objective(description="Test", target_id="t", target_count=3)
    obj.current_count = 1
    assert obj.progress() == pytest.approx(0.333, rel=0.01)


def test_objective_complete():
    obj = Objective(description="Test", target_id="t", target_count=2)
    obj.current_count = 2
    obj.completed = True
    assert obj.completed is True


def test_quest_activation():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    assert quest.is_active is False
    quest.activate()
    assert quest.is_active is True


def test_quest_completion():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Obj1", target_id="t", target_count=1))
    quest.advance_objective("t")
    assert quest.all_objectives_complete is True
    assert quest.is_completed is True


def test_quest_advance_objective():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Obj1", target_id="enemy", target_count=3))
    quest.advance_objective("enemy", 2)
    assert quest.objectives[0].current_count == 2
    assert quest.objectives[0].completed is False
    quest.advance_objective("enemy", 1)
    assert quest.objectives[0].completed is True
    assert quest.is_completed is True


def test_quest_serialization():
    quest = Quest(id="q1", title="Test Quest", description="A test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Do thing", target_id="t", target_count=2))
    quest.rewards = {"xp": 100, "gold": 50}

    data = quest.to_dict()
    restored = Quest.from_dict(data)
    assert restored.title == "Test Quest"
    assert len(restored.objectives) == 1
    assert restored.rewards["xp"] == 100
