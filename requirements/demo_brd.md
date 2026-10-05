# E-commerce Order Processor Business Requirements

## REQ-001: Standard Processing
The order processor shall calculate an order subtotal from each item's quantity and unit price, and process valid standard-customer orders by reducing inventory by the quantities ordered.

## REQ-002: VIP Discounts
The order processor shall apply a 10% discount to the subtotal of orders placed by VIP customers. Other customer types shall receive no discount.

## REQ-003: Error Handling for Negative Inventory
The order processor shall reject an order when inventory is negative or insufficient for the requested quantities. Rejected orders shall not change any inventory.
