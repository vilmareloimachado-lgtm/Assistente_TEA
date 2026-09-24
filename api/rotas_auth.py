from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/auth",
    tags=["autenticação"]
)

controller = UsuarioController()


class LoginUsuario(BaseModel):
    email: str
    senha: str


@router.post("/login")
def login(dados: LoginUsuario):
    resposta = controller.login(dados.email, dados.senha)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resposta["mensagem"]
        )

    return resposta