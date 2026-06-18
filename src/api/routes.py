# src/api/routes.py
"""
FastAPI 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.models import Ticket, ExecutionLog
from ..agents.executor import run_agent_pipeline
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TicketRequest(BaseModel):
    """工单请求"""
    customer_id: str
    order_id: str
    content: str

class TicketResponse(BaseModel):
    """工单响应"""
    ticket_id: str
    classification: str
    eval_score: float
    recommendation: str
    final_action: str

@router.post("/tickets", response_model=TicketResponse)
async def process_ticket(
    request: TicketRequest,
    db: Session = Depends(get_db)
):
    """
    处理客户工单
    """
    # 1. 运行 Agent 管道
    state = await run_agent_pipeline(
        ticket_id=f"TKT-{datetime.utcnow().timestamp()}",
        ticket_content=request.content
    )
    
    # 2. 保存到数据库
    ticket = Ticket(
        id=state['ticket_id'],
        ticket_content=request.content,
        customer_id=request.customer_id,
        order_id=request.order_id,
        classification=state['classification'],
        classification_score=state['classification_score'],
        recommendation=state['recommendation'],
        eval_score=state['eval_score'],
        final_action=state['final_action'],
        processed_at=datetime.utcnow(),
    )
    db.add(ticket)
    
    # 3. 保存执行日志
    for log in state['execution_logs']:
        exec_log = ExecutionLog(
            ticket_id=state['ticket_id'],
            agent_name=log['agent'],
            agent_action=log['action'],
            agent_result=str(log.get('result', '')),
        )
        db.add(exec_log)
    
    db.commit()
    
    # 4. 返回响应
    return TicketResponse(
        ticket_id=state['ticket_id'],
        classification=state['classification'],
        eval_score=state['eval_score'],
        recommendation=state['recommendation'],
        final_action=state['final_action'],
    )

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """查询工单"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        'id': ticket.id,
        'classification': ticket.classification,
        'recommendation': ticket.recommendation,
        'final_action': ticket.final_action,
        'eval_score': ticket.eval_score,
    }

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""
    total = db.query(Ticket).count()
    auto_send = db.query(Ticket).filter(Ticket.final_action == "auto_send").count()
    
    return {
        'total_tickets': total,
        'auto_send_count': auto_send,
        'auto_rate': auto_send / total if total > 0 else 0,
    }