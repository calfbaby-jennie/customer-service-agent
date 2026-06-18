# src/models/schemas.py
from typing import TypedDict, Optional, List
from datetime import datetime

class AgentState(TypedDict):
    """Agent 执行状态"""
    # 输入
    ticket_id: str
    ticket_content: str
    
    # 中间结果
    classification: Optional[str]  # 分类结果
    classification_score: Optional[float]
    order_data: Optional[dict]     # 订单信息
    policy_info: Optional[str]     # 退货政策
    
    # 输出
    recommendation: Optional[str]  # 处理建议
    eval_score: Optional[float]    # 评估分数
    final_action: Optional[str]    # 最终决策
    
    # 元数据
    execution_logs: List[dict]     # 执行日志
    created_at: datetime = datetime.utcnow()