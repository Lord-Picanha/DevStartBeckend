from app.core.database import SessionLocal
from app.models import chat as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user():
    # Truque do macaco: cria um usuário de mentirinha para você não precisar fazer login agora
    return models.User(id=1, email="macaco@floresta.com", hashed_password="123")