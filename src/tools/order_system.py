def get_order(order_id: str | None) -> dict:
    """Mock ERP/Oracle order lookup."""
    return {
        "order_id": order_id or "ORD-DEMO",
        "status": "待收货",
        "amount": 299.99,
        "created_date": "2026-06-20",
        "logistics_status": "运输中",
        "days_since_purchase": 8,
    }
