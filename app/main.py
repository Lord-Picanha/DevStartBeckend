from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.database import engine, Base
import app.models.chat  # Garante que os modelos são carregados pelo SQLAlchemy

# Cria automaticamente as tabelas na base de dados ao arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevStart Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")