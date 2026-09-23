import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Inicializa o cliente apenas se houver chave configurada
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def generate_chat_response(history: list[dict]) -> str:
    # Se a chave não existir ou for a chave de testes 'sk-dummy', responde em modo simulação
    if not settings.OPENAI_API_KEY or "sk-dummy" in settings.OPENAI_API_KEY:
        ultima_mensagem = history[-1]["content"] if history else ""
        return f"Olá! Sou o Tutor IA (Simulado). Recebi a tua dúvida: '{ultima_mensagem}'. O teu backend e frontend já estão 100% conectados! 🐒"

    # Se tiveres uma chave real da OpenAI no teu .env, ele usa a API oficial:
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            temperature=0.7,
            max_tokens=1024,
            timeout=15.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro no serviço da OpenAI: {e}")
        return "Ops! Ocorreu um erro ao comunicar com a OpenAI. Confere a tua API Key no ficheiro .env."