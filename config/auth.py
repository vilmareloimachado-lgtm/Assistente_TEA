import os
import jwt

from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITMO = "HS256"
EXPIRACAO_HORAS = 3


def validar_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado. Faça login novamente.")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido.")
    