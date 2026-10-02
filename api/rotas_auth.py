from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from controllers.usuario_controller import UsuarioController
from api.permissoes import exigir_tipo_usuario

router = APIRouter(
    prefix="/auth",
    tags=["autenticação"]
)

controller = UsuarioController()


class LoginUsuario(BaseModel):
    email: str
    senha: str


class LoginUsuarioTea(BaseModel):
    usuario_id: int
    pin: str | None = None


@router.post("/login")
def login(dados: LoginUsuario):
    resposta = controller.login(dados.email, dados.senha)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resposta["mensagem"]
        )

    return resposta


@router.post("/entrar-perfil")
def entrar_perfil(
    dados: LoginUsuarioTea,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.login_usuario_tea(
        usuario_logado["usuario_id"],
        dados.usuario_id,
        dados.pin
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resposta["mensagem"]
        )

    return resposta