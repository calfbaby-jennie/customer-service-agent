"""
本地测试脚本 - 不需要启动服务器，直接测试 Agent 管道
"""
import asyncio
from src.agents.executor import run_agent_pipeline

async def test():
    # 测试工单集合
    test_tickets = [
        {
            "id": "TEST-001",
            "content": "我的订单已经一周还没收到，想退货"
        },
        {
            "id": "TEST-002",
            "content": "产品质量很差，完全不符合描述，想要退货退款"
        },
        {
            "id": "TEST-003",
            "content": "请问配送要多久？"  # 这个不是退货
        },
    ]

    print("\n" + "="*60)
    print("Customer Service Agent - 本地测试")
    print("="*60 + "\n")

    for ticket in test_tickets:
        print(f"\n{'='*60}")
        print(f"测试工单 #{ticket['id']}")
        print(f"内容：{ticket['content']}")
        print('='*60)

        try:
            state = await run_agent_pipeline(
                ticket_id=ticket['id'],
                ticket_content=ticket['content'],
            )

            print(f"\n【处理结果】")
            print(f"✓ 分类：{state['classification']}")
            print(f"✓ 置信度：{state['classification_score']:.2f}")
            if state['eval_score']:
                print(f"✓ 评分：{state['eval_score']:.0f}/100")
            print(f"✓ 决策：{state['final_action']}")

            if state['recommendation']:
                print(f"\n【生成建议】")
                print(state['recommendation'][:200] + "..." if len(state['recommendation']) > 200 else state['recommendation'])

            print(f"\n【执行日志】 ({len(state['execution_logs'])} steps)")
            for i, log in enumerate(state['execution_logs'], 1):
                print(f"  {i}. {log['agent'].upper()}: {log['action']}")

        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("🚀 启动本地测试...\n")
    asyncio.run(test())
