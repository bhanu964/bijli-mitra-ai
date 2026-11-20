from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Bill, ChatMessage
from backend.app.schemas.schemas import ChatRequestSchema, ChatResponseSchema
from backend.app.ai.assistant import BijliMitraAssistant

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponseSchema)
def chat_with_assistant(
    payload: ChatRequestSchema,
    db: Session = Depends(get_db)
):
    bill_data = None
    if payload.bill_id:
        bill = db.query(Bill).filter(Bill.id == payload.bill_id).first()
        if bill:
            bill_data = {
                "id": bill.id,
                "billing_month": bill.billing_month,
                "consumption_units": bill.consumption_units,
                "printed_total": bill.printed_total,
                "is_gruha_jyothi": bill.is_gruha_jyothi
            }
            
    res = BijliMitraAssistant.respond(
        user_message=payload.message,
        bill_data=bill_data,
        language=payload.language
    )
    
    # Store user message
    msg_user = ChatMessage(
        session_id=payload.session_id,
        bill_id=payload.bill_id,
        role="user",
        content_en=payload.message,
        content_te=payload.message if payload.language == "te" else None
    )
    # Store assistant response
    msg_ai = ChatMessage(
        session_id=payload.session_id,
        bill_id=payload.bill_id,
        role="assistant",
        content_en=res["reply_en"],
        content_te=res["reply_te"],
        grounded_context={"facts": res["grounded_facts"]}
    )
    db.add(msg_user)
    db.add(msg_ai)
    db.commit()
    
    return ChatResponseSchema(
        session_id=payload.session_id,
        reply_en=res["reply_en"],
        reply_te=res["reply_te"],
        grounded_facts=res["grounded_facts"],
        suggested_questions=res["suggested_questions"]
    )
