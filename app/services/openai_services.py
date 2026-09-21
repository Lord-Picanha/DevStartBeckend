import logging
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from app.core.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_chat_response(history: list[dict]) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            temperature=0.7,
            max_tokens=1024,
            timeout=15.0
        )
        return response.choices[0].message.content
        
    except RateLimitError:
        logger.error("OpenAI Rate Limit Excedido.")
        raise ValueError("O serviço está com alta demanda. Tente novamente em instantes.")
    except APIConnectionError:
        logger.error("Falha de conexão com a OpenAI.")
        raise ValueError("Erro de conexão com o servidor de IA.")
    except APIError as e:
        logger.error(f"Erro genérico da OpenAI: {str(e)}")
        raise ValueError("Ocorreu um erro ao processar a tua mensagem.")
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise ValueError("Erro interno no processamento da resposta.")