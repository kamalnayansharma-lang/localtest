"""Physical pytest cases for the order processor traceability demo."""

import pytest
import order_processor

from order_processor import (
    NegativeInventoryError,
    OrderProcessingError,
    calculate_discount,
    calculate_subtotal,
    process_order,
    validate_inventory,
)


def test_calculate_subtotal_multiple_items():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([
        {"sku": "A", "quantity": 2, "unit_price": 3.5},
        {"sku": "B", "quantity": 1, "unit_price": 4},
    ]) == 11


def test_calculate_subtotal_empty_items():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([]) == 0


def test_calculate_subtotal_single_item():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([{"sku": "A", "quantity": 1, "unit_price": 9}]) == 9


def test_calculate_subtotal_large_quantity():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([{"sku": "A", "quantity": 1000, "unit_price": 2}]) == 2000


def test_calculate_subtotal_quantity_one_boundary():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([{"sku": "A", "quantity": 1, "unit_price": 2.5}]) == 2.5


def test_calculate_subtotal_zero_price_boundary():
    """Tests calculate_subtotal for REQ-001."""
    assert calculate_subtotal([{"sku": "A", "quantity": 4, "unit_price": 0}]) == 0


def test_calculate_subtotal_requires_list_type():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="items must be a list"):
        calculate_subtotal("not a list")


def test_calculate_subtotal_rejects_non_list_sequence():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="items must be a list"):
        calculate_subtotal(({"sku": "A", "quantity": 1, "unit_price": 1},))


def test_calculate_subtotal_requires_quantity():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="quantity must be an integer"):
        calculate_subtotal([{"sku": "A", "unit_price": 1}])


def test_calculate_subtotal_rejects_zero_quantity():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_subtotal([{"sku": "A", "quantity": 0, "unit_price": 1}])


def test_calculate_subtotal_rejects_negative_quantity():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_subtotal([{"sku": "A", "quantity": -1, "unit_price": 1}])


def test_calculate_subtotal_rejects_fractional_quantity():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="quantity must be an integer"):
        calculate_subtotal([{"sku": "A", "quantity": 1.5, "unit_price": 1}])


def test_calculate_subtotal_rejects_boolean_quantity():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="quantity must be an integer"):
        calculate_subtotal([{"sku": "A", "quantity": True, "unit_price": 1}])


def test_calculate_subtotal_rejects_negative_price():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="must not be negative"):
        calculate_subtotal([{"sku": "A", "quantity": 1, "unit_price": -1}])


def test_calculate_subtotal_rejects_string_price():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="unit_price must be a number"):
        calculate_subtotal([{"sku": "A", "quantity": 1, "unit_price": "2"}])


def test_calculate_subtotal_rejects_nan_price():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="must be finite"):
        calculate_subtotal([{"sku": "A", "quantity": 1, "unit_price": float("nan")}])


def test_calculate_subtotal_requires_sku():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(TypeError, match="sku must be a string"):
        calculate_subtotal([{"quantity": 1, "unit_price": 1}])


def test_calculate_subtotal_rejects_blank_sku():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="sku must not be empty"):
        calculate_subtotal([{"sku": "  ", "quantity": 1, "unit_price": 1}])


def test_process_order_standard_no_discount():
    """Tests process_order for REQ-001."""
    inventory = {"A": 5}
    result = process_order([{"sku": "A", "quantity": 2, "unit_price": 4}], inventory)
    assert result == {
        "subtotal": 8,
        "discount": 0,
        "total": 8,
        "customer_type": "standard",
    }


def test_process_order_reduces_inventory():
    """Tests process_order for REQ-001."""
    inventory = {"A": 5}
    process_order([{"sku": "A", "quantity": 2, "unit_price": 4}], inventory)
    assert inventory == {"A": 3}


def test_process_order_standard_exact_stock_boundary():
    """Tests process_order for REQ-001."""
    inventory = {"A": 1}
    process_order([{"sku": "A", "quantity": 1, "unit_price": 4}], inventory)
    assert inventory["A"] == 0


def test_process_order_standard_multiple_items():
    """Tests process_order for REQ-001."""
    inventory = {"A": 4, "B": 3}
    result = process_order([
        {"sku": "A", "quantity": 2, "unit_price": 3},
        {"sku": "B", "quantity": 1, "unit_price": 5},
    ], inventory)
    assert result["subtotal"] == 11
    assert inventory == {"A": 2, "B": 2}


def test_calculate_discount_vip_ten_percent():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(100, "VIP") == 10


def test_calculate_discount_vip_case_insensitive():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(100, "vIp") == 10


def test_calculate_discount_zero_subtotal():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(0, "VIP") == 0


def test_calculate_discount_zero_boundary():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(0, "standard") == 0


def test_calculate_discount_standard_customer():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(100, "standard") == 0


def test_calculate_discount_unknown_customer_type():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(100, "guest") == 0


def test_calculate_discount_rejects_negative_subtotal():
    """Tests calculate_discount for REQ-002."""
    with pytest.raises(ValueError, match="must not be negative"):
        calculate_discount(-1, "VIP")


def test_calculate_discount_requires_numeric_subtotal():
    """Tests calculate_discount for REQ-002."""
    with pytest.raises(TypeError, match="subtotal must be a number"):
        calculate_discount("100", "VIP")


def test_calculate_discount_rejects_boolean_subtotal():
    """Tests calculate_discount for REQ-002."""
    with pytest.raises(TypeError, match="subtotal must be a number"):
        calculate_discount(True, "VIP")


def test_calculate_discount_rejects_non_finite_subtotal():
    """Tests calculate_discount for REQ-002."""
    with pytest.raises(ValueError, match="subtotal must be finite"):
        calculate_discount(float("inf"), "VIP")


def test_calculate_discount_requires_customer_type_string():
    """Tests calculate_discount for REQ-002."""
    with pytest.raises(TypeError, match="customer_type must be a string"):
        calculate_discount(100, None)


def test_process_order_vip_discount_amount():
    """Tests process_order for REQ-002."""
    result = process_order(
        [{"sku": "A", "quantity": 2, "unit_price": 50}], {"A": 2}, "VIP"
    )
    assert result["discount"] == 10


def test_process_order_vip_discounted_total():
    """Tests process_order for REQ-002."""
    result = process_order(
        [{"sku": "A", "quantity": 2, "unit_price": 50}], {"A": 2}, "VIP"
    )
    assert result["total"] == 90


def test_process_order_non_vip_receives_no_discount():
    """Tests process_order for REQ-002."""
    result = process_order(
        [{"sku": "A", "quantity": 2, "unit_price": 50}], {"A": 2}, "standard"
    )
    assert result["discount"] == 0


def test_validate_inventory_sufficient_stock():
    """Tests validate_inventory for REQ-003."""
    assert validate_inventory([{"sku": "A", "quantity": 2, "unit_price": 1}], {"A": 3}) is None


def test_validate_inventory_exact_stock_boundary():
    """Tests validate_inventory for REQ-003."""
    assert validate_inventory([{"sku": "A", "quantity": 2, "unit_price": 1}], {"A": 2}) is None


def test_validate_inventory_rejects_missing_sku_record():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(OrderProcessingError, match="no inventory record"):
        validate_inventory([{"sku": "A", "quantity": 1, "unit_price": 1}], {})


def test_validate_inventory_rejects_negative_stock():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(NegativeInventoryError, match="is negative"):
        validate_inventory([{"sku": "A", "quantity": 1, "unit_price": 1}], {"A": -1})


def test_validate_inventory_rejects_insufficient_stock():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(OrderProcessingError, match="insufficient inventory"):
        validate_inventory([{"sku": "A", "quantity": 3, "unit_price": 1}], {"A": 2})


def test_validate_inventory_aggregates_repeated_sku_demand():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(OrderProcessingError, match="insufficient inventory"):
        validate_inventory([
            {"sku": "A", "quantity": 2, "unit_price": 1},
            {"sku": "A", "quantity": 2, "unit_price": 1},
        ], {"A": 3})


def test_validate_inventory_allows_aggregated_demand_when_sufficient():
    """Tests validate_inventory for REQ-003."""
    assert validate_inventory([
        {"sku": "A", "quantity": 2, "unit_price": 1},
        {"sku": "A", "quantity": 2, "unit_price": 1},
    ], {"A": 4}) is None


def test_validate_inventory_requires_dictionary_type():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(TypeError, match="inventory must be a dictionary"):
        validate_inventory([], [("A", 1)])


def test_validate_inventory_rejects_fractional_stock():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(TypeError, match="quantities must be integers"):
        validate_inventory([], {"A": 1.5})


def test_validate_inventory_rejects_boolean_stock():
    """Tests validate_inventory for REQ-003."""
    with pytest.raises(TypeError, match="quantities must be integers"):
        validate_inventory([], {"A": True})


def test_process_order_negative_stock_does_not_mutate_inventory():
    """Tests process_order for REQ-003."""
    inventory = {"A": -1}
    with pytest.raises(NegativeInventoryError):
        process_order([{"sku": "A", "quantity": 1, "unit_price": 2}], inventory)
    assert inventory == {"A": -1}


def test_process_order_insufficient_stock_does_not_mutate_inventory():
    """Tests process_order for REQ-003."""
    inventory = {"A": 1, "B": 5}
    items = [
        {"sku": "A", "quantity": 1, "unit_price": 2},
        {"sku": "B", "quantity": 6, "unit_price": 2},
    ]
    with pytest.raises(OrderProcessingError):
        process_order(items, inventory)
    assert inventory == {"A": 1, "B": 5}


def test_process_order_aggregates_duplicate_sku_before_mutation():
    """Tests process_order for REQ-003."""
    inventory = {"A": 3}
    items = [
        {"sku": "A", "quantity": 2, "unit_price": 2},
        {"sku": "A", "quantity": 2, "unit_price": 2},
    ]
    with pytest.raises(OrderProcessingError, match="insufficient inventory"):
        process_order(items, inventory)
    assert inventory == {"A": 3}


def test_process_order_insufficient_inventory_is_atomic_across_skus():
    """Tests process_order for REQ-003."""
    inventory = {"A": 10, "B": 0}
    items = [
        {"sku": "A", "quantity": 2, "unit_price": 2},
        {"sku": "B", "quantity": 1, "unit_price": 2},
    ]
    with pytest.raises(OrderProcessingError):
        process_order(items, inventory)
    assert inventory == {"A": 10, "B": 0}


def test_calculate_subtotal_supports_arbitrary_precision_integer_prices():
    """Tests calculate_subtotal for REQ-001."""
    large_price = 10**400
    assert calculate_subtotal(
        [{"sku": "A", "quantity": 1, "unit_price": large_price}]
    ) == large_price


def test_calculate_subtotal_rejects_overflowing_line_total():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="finite"):
        calculate_subtotal([{"sku": "A", "quantity": 2, "unit_price": 1e308}])


def test_calculate_subtotal_rejects_overflowing_sum():
    """Tests calculate_subtotal for REQ-001."""
    with pytest.raises(ValueError, match="finite"):
        calculate_subtotal([
            {"sku": "A", "quantity": 1, "unit_price": 1e308},
            {"sku": "B", "quantity": 1, "unit_price": 1e308},
        ])


def test_calculate_discount_handles_large_standard_subtotal():
    """Tests calculate_discount for REQ-002."""
    assert calculate_discount(10**400, "standard") == 0


def test_validate_inventory_ignores_negative_unordered_sku():
    """Tests validate_inventory for REQ-003."""
    assert validate_inventory(
        [{"sku": "A", "quantity": 1, "unit_price": 1}],
        {"A": 2, "UNRELATED": -1},
    ) is None


def test_process_order_is_exposed_as_a_module_function():
    """Tests process_order for REQ-001; module-export check only."""
    assert callable(order_processor.process_order)


def test_order_processing_error_has_expected_class_name():
    """Tests OrderProcessingError for REQ-003; class metadata only."""
    assert OrderProcessingError.__name__ == "OrderProcessingError"


def test_negative_inventory_error_is_defined_in_order_processor():
    """Tests NegativeInventoryError for REQ-003; module metadata only."""
    assert NegativeInventoryError.__module__ == "order_processor"


def test_order_processor_exposes_version_metadata():
    """Tests order_processor for REQ-001; unrelated metadata check."""
    assert order_processor.__version__ == "1.0.0"


def test_order_processor_exposes_author_metadata():
    """Tests order_processor for REQ-002; unrelated metadata check."""
    assert order_processor.__author__
