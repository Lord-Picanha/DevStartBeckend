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
):
    # 1. Garante que existe pelo menos o utilizador padrão (ID 1) para testes
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(
            id=1, 
            email="dev@devstart.com", 
            hashed_password="hashed_dummy_password"
        )
        db.add(user)
        db.commit()

    # 2. Confere se a conversa existe
    conv = db.query(models.Conversation).filter(
        models.Conversation.id == payload.conversation_id
    ).first()
    
    # Se não existir, cria a conversa associada ao utilizador 1
    if not conv:
        conv = models.Conversation(id=payload.conversation_id, user_id=1)
        db.add(conv)
        db.commit()

    # 3. Salva a pergunta do utilizador
    user_msg = models.Message(
        conversation_id=conv.id, 
        role="user", 
        content=payload.content
    )
    db.add(user_msg)
    db.commit()

    # 4. Procura o histórico da conversa
    raw_history = db.query(models.Message).filter(
        models.Message.conversation_id == conv.id
    ).order_by(models.Message.created_at.asc()).all()
    
    ai_history = [{"role": msg.role, "content": msg.content} for msg in raw_history]

    # 5. Envia o histórico para o serviço de IA
    try:
        ai_response_text = await generate_chat_response(ai_history)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro no serviço de IA: {str(e)}")

    # 6. Salva e retorna a resposta da IA
    ai_msg = models.Message(
        conversation_id=conv.id, 
        role="assistant", 
        content=ai_response_text
    )
    db.add(ai_msg)
    db.commit()

    return ai_msg