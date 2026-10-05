"""Order processing logic for the traceability demo."""

import math
from typing import Any


class OrderProcessingError(ValueError):
    """Raised when an order cannot be fulfilled."""


class NegativeInventoryError(OrderProcessingError):
    """Raised when inventory contains a negative quantity."""


def _validated_items(items: list[dict[str, Any]]) -> list[tuple[str, int, int | float]]:
    """Validate line-item shape and return normalized SKU, quantity, and price tuples."""
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    validated: list[tuple[str, int, int | float]] = []
    for item in items:
        if not isinstance(item, dict):
            raise TypeError("each item must be a dictionary")
        sku = item.get("sku")
        if not isinstance(sku, str):
            raise TypeError("item sku must be a string")
        if not sku.strip():
            raise ValueError("item sku must not be empty")

        quantity = item.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("item quantity must be an integer")
        if quantity <= 0:
            raise ValueError("item quantity must be greater than zero")

        unit_price = item.get("unit_price")
        if isinstance(unit_price, bool) or not isinstance(unit_price, (int, float)):
            raise TypeError("unit_price must be a number")
        if not math.isfinite(unit_price):
            raise ValueError("unit_price must be finite")
        if unit_price < 0:
            raise ValueError("unit_price must not be negative")
        validated.append((sku, quantity, unit_price))
    return validated


def calculate_subtotal(items: list[dict[str, Any]]) -> int | float:
    """Calculate a line-item subtotal. Requirement: REQ-001."""
    return sum(quantity * unit_price for _, quantity, unit_price in _validated_items(items))


def calculate_discount(subtotal: int | float, customer_type: str) -> int | float:
    """Apply the VIP discount when applicable. Requirement: REQ-002."""
    if isinstance(subtotal, bool) or not isinstance(subtotal, (int, float)):
        raise TypeError("subtotal must be a number")
    if not math.isfinite(subtotal):
        raise ValueError("subtotal must be finite")
    if subtotal < 0:
        raise ValueError("subtotal must not be negative")
    if not isinstance(customer_type, str):
        raise TypeError("customer_type must be a string")
    return subtotal * 0.10 if customer_type.strip().lower() == "vip" else 0


def validate_inventory(
    items: list[dict[str, Any]], inventory: dict[str, int]
) -> None:
    """Reject invalid, negative, or insufficient inventory. Requirement: REQ-003."""
    validated_items = _validated_items(items)
    if not isinstance(inventory, dict):
        raise TypeError("inventory must be a dictionary")

    for sku, available in inventory.items():
        if not isinstance(sku, str):
            raise TypeError("inventory SKUs must be strings")
        if isinstance(available, bool) or not isinstance(available, int):
            raise TypeError("inventory quantities must be integers")
        if available < 0:
            raise NegativeInventoryError(f"inventory for {sku} is negative")

    required: dict[str, int] = {}
    for sku, quantity, _ in validated_items:
        required[sku] = required.get(sku, 0) + quantity
    for sku, quantity in required.items():
        if sku not in inventory:
            raise OrderProcessingError(f"no inventory record for {sku}")
        if inventory[sku] < quantity:
            raise OrderProcessingError(f"insufficient inventory for {sku}")


def process_order(
    items: list[dict[str, Any]],
    inventory: dict[str, int],
    customer_type: str = "standard",
) -> dict[str, Any]:
    """Validate and process an order without partial inventory updates.

    Requirement: REQ-001, REQ-002, REQ-003.
    """
    subtotal = calculate_subtotal(items)
    validate_inventory(items, inventory)
    discount = calculate_discount(subtotal, customer_type)

    for sku, quantity, _ in _validated_items(items):
        inventory[sku] -= quantity

    return {
        "subtotal": subtotal,
        "discount": discount,
        "total": subtotal - discount,
        "customer_type": customer_type,
    }
