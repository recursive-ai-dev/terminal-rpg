"""Inventory management."""

from __future__ import annotations

from rpg.models.core import Player, Item


def add_item(player: Player, item: Item) -> bool:
    """Add item to player inventory. Returns True if successful."""
    # Stack consumables
    if item.item_type == "consumable":
        for existing in player.inventory:
            if existing.name == item.name and existing.item_type == item.item_type:
                existing.quantity += item.quantity
                return True
    player.inventory.append(item)
    return True


def remove_item(player: Player, item_name: str, quantity: int = 1) -> Item | None:
    """Remove item from inventory. Returns the removed item or None."""
    for i, item in enumerate(player.inventory):
        if item.name == item_name:
            if item.quantity > quantity:
                item.quantity -= quantity
                removed = Item(
                    name=item.name,
                    item_type=item.item_type,
                    value=item.value,
                    stats=item.stats.copy(),
                    quantity=quantity,
                )
                return removed
            else:
                return player.inventory.pop(i)
    return None


def use_item(player: Player, item_name: str) -> str | None:
    """Use a consumable item. Returns message or None if can't use."""
    for item in player.inventory:
        if item.name == item_name and item.item_type == "consumable":
            if item.quantity <= 0:
                return "You don't have any of those."

            message = _apply_consumable(player, item)
            item.quantity -= 1
            if item.quantity <= 0:
                player.inventory.remove(item)
            return message

    return "You can't use that."


def _apply_consumable(player: Player, item: Item) -> str:
    """Apply consumable effects."""
    if "Health Potion" in item.name:
        healed = player.heal(30)
        return f"You drink the potion and heal {healed} HP."
    if "Stamina Tonic" in item.name:
        player.stats["speed"] += 1
        return "You feel a surge of energy! Speed +1"
    if "Elixir" in item.name:
        player.stats["luck"] += 1
        return "You feel luckier! Luck +1"
    if "Rations" in item.name:
        return "You eat the rations. Satisfying."
    if "Antidote" in item.name:
        return "The antidote courses through your veins."
    if "Bandages" in item.name:
        healed = player.heal(10)
        return f"You bandage your wounds and heal {healed} HP."
    return f"You use the {item.name}. Nothing happens."


def get_inventory_summary(player: Player) -> list[dict]:
    """Get inventory as summary list."""
    return [
        {
            "name": item.name,
            "type": item.item_type,
            "quantity": item.quantity,
            "value": item.value,
        }
        for item in player.inventory
    ]
