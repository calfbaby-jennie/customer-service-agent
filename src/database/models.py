# src/database/models.py
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Ticket(Base):
    """工单模型"""
    __tablename__ = "tickets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_content = Column(Text, nullable=False)
    customer_id = Column(String(100), nullable=False)
    order_id = Column(String(100), nullable=True)
    
    # 分类结果
    classification = Column(String(50), nullable=True)  # "退货" / "咨询" / "投诉"
    classification_score = Column(Float, nullable=True)  # 0-1
    
    # 建议
    recommendation = Column(Text, nullable=True)
    eval_score = Column(Float, nullable=True)  # 0-100
    
    # 最终决策
    final_action = Column(String(50), nullable=True)  # "auto_send" / "human_confirm" / "reject"
    
    # 人工处理信息
    handled_by = Column(String(100), nullable=True)  # 客服名字
    human_override = Column(Boolean, default=False)  # 是否被人工改过
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Ticket {self.id}: {self.classification}>"

class ExecutionLog(Base):
    """执行日志（用于追踪 Agent 执行过程）"""
    __tablename__ = "execution_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), nullable=False)  # 外键指向 Ticket
    
    agent_name = Column(String(50), nullable=False)  # "supervisor" / "policy" / "action" / "critic"
    agent_action = Column(Text, nullable=False)  # 做了什么
    agent_result = Column(Text, nullable=True)   # 结果是什么
    
    # Agent 花费
    tokens_used = Column(Integer, nullable=True)  # LLM token 数量
    cost = Column(Float, nullable=True)          # 成本（美元）
    latency_ms = Column(Integer, nullable=True)  # 延迟（毫秒）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionLog {self.agent_name} for {self.ticket_id}>"