def search_return_policy(ticket_content: str) -> str:
    """Mock Elasticsearch knowledge-base lookup for return/after-sales policies."""
    return """
退货/售后政策：
- 7 天无理由退货：商品需完整、未使用，不影响二次销售
- 物流超时：超过承诺送达时间可优先人工确认，并可补偿运费券
- 商品质量问题：客户提供照片后可免退货运费并优先退款
- 高风险订单或信息缺失：转人工确认，不自动发送
""".strip()
