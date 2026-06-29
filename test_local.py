"""
Local test script for the Agent pipeline.
"""
import asyncio
import traceback

from src.agents.executor import run_agent_pipeline


async def test() -> int:
    test_tickets = [
        {
            "id": "TEST-001",
            "customer_id": "CUST-001",
            "order_id": "ORD-12345",
            "content": "我的订单已经一周还没收到，想退货",
        },
        {
            "id": "TEST-002",
            "customer_id": "CUST-002",
            "order_id": "ORD-23456",
            "content": "产品质量很差，完全不符合描述，想要退货退款",
        },
        {
            "id": "TEST-003",
            "customer_id": "CUST-003",
            "order_id": "ORD-34567",
            "content": "请问配送要多久？",
        },
    ]

    failures = 0

    print("\n" + "=" * 60)
    print("Customer Service Agent - 本地测试")
    print("=" * 60 + "\n")

    for ticket in test_tickets:
        print(f"\n{'=' * 60}")
        print(f"测试工单 #{ticket['id']}")
        print(f"内容：{ticket['content']}")
        print("=" * 60)

        try:
            state = await run_agent_pipeline(
                ticket_id=ticket["id"],
                ticket_content=ticket["content"],
                customer_id=ticket["customer_id"],
                order_id=ticket["order_id"],
            )

            print("\n【处理结果】")
            print(f"✓ 分类：{state['classification']}")
            print(f"✓ 置信度：{state['classification_score']:.2f}")
            if state["eval_score"] is not None:
                print(f"✓ 评分：{state['eval_score']:.0f}/100")
            print(f"✓ 决策：{state['final_action']}")

            if state["recommendation"]:
                print("\n【生成建议】")
                recommendation = state["recommendation"]
                print(recommendation[:200] + "..." if len(recommendation) > 200 else recommendation)

            print(f"\n【执行日志】 ({len(state['execution_logs'])} steps)")
            for i, log in enumerate(state["execution_logs"], 1):
                print(f"  {i}. {log['agent'].upper()}: {log['action']}")

        except Exception as exc:
            failures += 1
            print(f"❌ 错误：{exc}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"测试完成：{len(test_tickets) - failures} 成功，{failures} 失败")
    print("=" * 60 + "\n")

    return failures


if __name__ == "__main__":
    print("🚀 启动本地测试...\n")
    failed = asyncio.run(test())
    raise SystemExit(1 if failed else 0)
