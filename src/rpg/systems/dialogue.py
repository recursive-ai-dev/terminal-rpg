"""Dialogue system."""

from __future__ import annotations

from dataclasses import dataclass, field

from rpg.models.npc import NPC


@dataclass
class DialogueState:
    """Current dialogue state with an NPC."""
    npc: NPC
    current_line: str = ""
    choices: list[str] = field(default_factory=list)
    finished: bool = False
    trade_opened: bool = False
    quest_offered: str | None = None  # Quest ID


def start_dialogue(npc: NPC) -> DialogueState:
    """Start a conversation with an NPC."""
    state = DialogueState(npc=npc)

    if npc.dialogue:
        state.current_line = npc.dialogue[0]

    # Available choices based on NPC role
    state.choices = ["Leave"]
    if npc.is_merchant:
        state.choices.insert(0, "Trade")
    if npc.gives_quests:
        state.choices.insert(0, "Ask for work")
    state.choices.insert(0, "Continue")

    return state


def advance_dialogue(state: DialogueState, choice: str) -> DialogueState:
    """Process player's dialogue choice."""
    if choice == "Leave":
        state.finished = True
        return state

    if choice == "Trade" and state.npc.is_merchant:
        state.trade_opened = True
        state.finished = True
        return state

    if choice == "Ask for work" and state.npc.gives_quests:
        state.quest_offered = state.npc.id  # Will be resolved to quest ID by game
        state.current_line = f"I have something that needs doing. Interested?"
        state.choices = ["Accept", "Decline", "Leave"]
        return state

    if choice == "Accept" and state.quest_offered:
        state.current_line = "Good. Don't disappoint me."
        state.choices = ["Leave"]
        return state

    if choice == "Decline" and state.quest_offered:
        state.current_line = "Perhaps another time then."
        state.quest_offered = None
        state.choices = ["Leave"]
        return state

    # Continue cycling through dialogue
    if choice == "Continue" and state.npc.dialogue:
        current_idx = state.npc.dialogue.index(state.current_line) if state.current_line in state.npc.dialogue else -1
        next_idx = (current_idx + 1) % len(state.npc.dialogue)
        state.current_line = state.npc.dialogue[next_idx]

    return state
