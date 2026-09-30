import os
import jwt

from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITMO = "HS256"

# Quanto tempo o login vale (em horas) para cada tipo de usuario.
EXPIRACAO_HORAS_CUIDADOR = 12
EXPIRACAO_HORAS_USUARIO_TEA = 24 * 7  # 7 dias


def horas_de_expiracao(tipo_usuario):
    if tipo_usuario == "usuario_tea":
        return EXPIRACAO_HORAS_USUARIO_TEA
    return EXPIRACAO_HORAS_CUIDADOR


def obter_chave_secreta():
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY não encontrada. Defina-a no arquivo .env.")
    return SECRET_KEY


def validar_token(token):
    try:
        return jwt.decode(token, obter_chave_secreta(), algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado. Faça login novamente.")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido.")