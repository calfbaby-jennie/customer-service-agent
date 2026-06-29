"""
FastAPI routes.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..agents.executor import run_agent_pipeline
from ..database.connection import get_db
from ..database.models import ExecutionLog, Ticket

router = APIRouter()


class TicketRequest(BaseModel):
    """Ticket processing request."""

    customer_id: str
    order_id: Optional[str] = None
    content: str


class TicketResponse(BaseModel):
    """Ticket processing response."""

    ticket_id: str
    classification: Optional[str]
    eval_score: Optional[float]
    recommendation: Optional[str]
    final_action: Optional[str]


@router.post("/tickets", response_model=TicketResponse)
async def process_ticket(request: TicketRequest, db: Session = Depends(get_db)):
    """Process a customer-service ticket."""
    ticket_id = f"TKT-{uuid4().hex[:12]}"

    try:
        state = await run_agent_pipeline(
            ticket_id=ticket_id,
            ticket_content=request.content,
            customer_id=request.customer_id,
            order_id=request.order_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent pipeline failed: {exc}") from exc

    ticket = Ticket(
        id=state["ticket_id"],
        ticket_content=request.content,
        customer_id=request.customer_id,
        order_id=request.order_id,
        classification=state.get("classification"),
        classification_score=state.get("classification_score"),
        recommendation=state.get("recommendation"),
        eval_score=state.get("eval_score"),
        final_action=state.get("final_action"),
        processed_at=datetime.utcnow(),
    )
    db.add(ticket)

    for log in state["execution_logs"]:
        db.add(
            ExecutionLog(
                ticket_id=state["ticket_id"],
                agent_name=log["agent"],
                agent_action=log["action"],
                agent_result=str(log.get("result", log)),
            )
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return TicketResponse(
        ticket_id=state["ticket_id"],
        classification=state.get("classification"),
        eval_score=state.get("eval_score"),
        recommendation=state.get("recommendation"),
        final_action=state.get("final_action"),
    )


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Query a ticket by id."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "id": ticket.id,
        "classification": ticket.classification,
        "recommendation": ticket.recommendation,
        "final_action": ticket.final_action,
        "eval_score": ticket.eval_score,
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Return basic automation statistics."""
    total = db.query(Ticket).count()
    auto_send = db.query(Ticket).filter(Ticket.final_action == "auto_send").count()

    return {
        "total_tickets": total,
        "auto_send_count": auto_send,
        "auto_rate": auto_send / total if total > 0 else 0,
    }
