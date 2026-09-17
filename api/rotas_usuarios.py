from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

controller = UsuarioController()

class NovoUsuario(BaseModel):
    nome: str
    estilo_instrucao: str = "direto"
    nivel_suporte: str
    data_nascimento: str
    senha_login: str
    
@router.get("")
def listar_usuarios():
    return {
        "dados": controller.listar_perfis()
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: NovoUsuario):
    resposta = controller.criar_perfil(
        dados.nome,
        dados.estilo_instrucao,
        dados.nivel_suporte,
        dados.data_nascimento,
        dados.senha_login
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=422,
            detail=resposta["mensagem"]
        )

    return resposta
