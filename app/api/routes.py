from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.api import deps
from app.models import chat as models
from app.services.openai_service import generate_chat_response

router = APIRouter()

class MessageCreate(BaseModel):
    conversation_id: int
    content: str

class MessageOut(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True

@router.post("/chat", response_model=MessageOut)
async def chat_endpoint(
    payload: MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Confere se a conversa existe
    conv = db.query(models.Conversation).filter(
        models.Conversation.id == payload.conversation_id
    ).first()
    
    # Se não existir, cria uma na hora (truque para facilitar seu teste!)
    if not conv:
        conv = models.Conversation(id=payload.conversation_id, user_id=current_user.id)
        db.add(conv)
        db.commit()

    # 2. Salva a sua pergunta
    user_msg = models.Message(conversation_id=conv.id, role="user", content=payload.content)
    db.add(user_msg)
    db.commit()

    # 3. Pega as mensagens antigas para o Gorila lembrar do assunto
    raw_history = db.query(models.Message).filter(models.Message.conversation_id == conv.id).all()
    ai_history = [{"role": msg.role, "content": msg.content} for msg in raw_history]

    # 4. Envia para a OpenAI
    try:
        ai_response_text = await generate_chat_response(ai_history)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # 5. Salva a resposta do Gorila
    ai_msg = models.Message(conversation_id=conv.id, role="assistant", content=ai_response_text)
    db.add(ai_msg)
    db.commit()

    return ai_msg