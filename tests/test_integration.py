"""Integration tests for full game generation and startup."""

from rpg.main import generate_new_world


def test_generate_new_world():
    state = generate_new_world("integration-test-seed")
    assert state.seed == "integration-test-seed"
    assert state.world is not None
    assert len(state.world.regions) > 0
    assert len(state.factions) > 0
    assert len(state.npcs) > 0
    assert len(state.quests) > 0
    assert len(state.events) > 0
    assert state.player.location is not None
    assert state.player.location.visited is True


def test_world_has_coherent_data():
    state = generate_new_world("coherence-test")

    # All NPCs should be in valid regions
    for npc in state.npcs:
        assert npc.location_id in state.world.regions

    # All quests should have valid giver NPCs
    quest_giver_ids = {npc.id for npc in state.npcs}
    for quest in state.quests:
        assert quest.giver_id in quest_giver_ids

    # Player should start in a valid region
    assert state.player.location.id in state.world.regions


def test_event_log_populated():
    state = generate_new_world("log-test")
    assert len(state.event_log) > 0
