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
    email: str
    tipo_usuario: str = "cuidador"
    
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
        dados.senha_login,
        dados.email,
        dados.tipo_usuario
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta

class AtualizacaoUsuario(BaseModel):
    novo_nome: str | None = None
    estilo_instrucao: str | None = None
    nivel_suporte: str | None = None
    data_nascimento: str | None = None
    senha_login: str | None = None
    email: str | None = None
    tipo_usuario: str | None = None


@router.get("/{nome}")
def buscar_usuario(nome: str):
    resposta = controller.buscar_perfil(nome)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.put("/{nome}")
def atualizar_usuario(nome: str, dados: AtualizacaoUsuario):
    resposta = controller.atualizar_perfil(
        nome,
        novo_nome=dados.novo_nome,
        estilo_instrucao=dados.estilo_instrucao,
        nivel_suporte=dados.nivel_suporte,
        data_nascimento=dados.data_nascimento,
        senha_login=dados.senha_login,
        email=dados.email,
        tipo_usuario=dados.tipo_usuario
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.delete("/{nome}")
def excluir_usuario(nome: str):
    resposta = controller.excluir_perfil(nome)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta
