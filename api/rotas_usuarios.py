from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from controllers.usuario_controller import UsuarioController
from api.permissoes import exigir_tipo_usuario

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

controller = UsuarioController()


# ------------------------------------------------------------
# Dados recebidos pela API
# ------------------------------------------------------------
class NovaContaCuidador(BaseModel):
    nome: str
    email: str
    senha: str
    data_nascimento: str


class NovoUsuarioTea(BaseModel):
    nome: str
    estilo_instrucao: str = "direto"
    nivel_suporte: str
    data_nascimento: str
    pin: str | None = None


class AtualizacaoUsuarioTea(BaseModel):
    nome: str | None = None
    estilo_instrucao: str | None = None
    nivel_suporte: str | None = None
    data_nascimento: str | None = None


class NovoPin(BaseModel):
    pin: str


class NovoCuidadorVinculado(BaseModel):
    email: str


class TransferenciaPrincipal(BaseModel):
    novo_principal_id: int


class ExclusaoConta(BaseModel):
    senha: str


# ------------------------------------------------------------
# Conta do cuidador
# ------------------------------------------------------------
@router.post("/conta", status_code=status.HTTP_201_CREATED)
def criar_conta(dados: NovaContaCuidador):
    resposta = controller.cadastrar_cuidador(
        dados.nome,
        dados.email,
        dados.senha,
        dados.data_nascimento
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.delete("/conta")
def excluir_conta(
    dados: ExclusaoConta,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.excluir_cuidador(
        usuario_logado["usuario_id"],
        dados.senha
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Perfis de usuarios TEA do cuidador logado
# ------------------------------------------------------------
@router.get("")
def listar_usuarios(
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    return controller.listar_usuarios_do_cuidador(
        usuario_logado["usuario_id"]
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_usuario_tea(
    dados: NovoUsuarioTea,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.criar_usuario_tea(
        usuario_logado["usuario_id"],
        dados.nome,
        dados.estilo_instrucao,
        dados.nivel_suporte,
        dados.data_nascimento,
        dados.pin
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.get("/{usuario_id}")
def buscar_usuario(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    perfis = controller.listar_usuarios_do_cuidador(
        usuario_logado["usuario_id"]
    )

    ids_permitidos = {
        usuario["usuario_id"]
        for usuario in perfis["usuarios"]
    }

    if usuario_id not in ids_permitidos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado."
        )

    resposta = controller.buscar_perfil_por_id(usuario_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resposta["mensagem"]
        )

    return resposta


@router.put("/{usuario_id}")
def atualizar_usuario(
    usuario_id: int,
    dados: AtualizacaoUsuarioTea,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.atualizar_usuario_tea(
        usuario_logado["usuario_id"],
        usuario_id,
        nome=dados.nome,
        estilo_instrucao=dados.estilo_instrucao,
        nivel_suporte=dados.nivel_suporte,
        data_nascimento=dados.data_nascimento
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.delete("/{usuario_id}")
def excluir_usuario(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.excluir_usuario_tea(
        usuario_logado["usuario_id"],
        usuario_id
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# PIN do perfil TEA
# ------------------------------------------------------------
@router.put("/{usuario_id}/pin")
def definir_pin(
    usuario_id: int,
    dados: NovoPin,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.definir_pin(
        usuario_logado["usuario_id"],
        usuario_id,
        dados.pin
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.delete("/{usuario_id}/pin")
def remover_pin(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.remover_pin(
        usuario_logado["usuario_id"],
        usuario_id
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Cuidadores vinculados ao perfil TEA
# ------------------------------------------------------------
@router.get("/{usuario_id}/cuidadores")
def listar_cuidadores(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.listar_cuidadores_do_usuario(
        usuario_logado["usuario_id"],
        usuario_id
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.post("/{usuario_id}/cuidadores")
def adicionar_cuidador(
    usuario_id: int,
    dados: NovoCuidadorVinculado,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.adicionar_cuidador(
        usuario_logado["usuario_id"],
        usuario_id,
        dados.email
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.delete("/{usuario_id}/cuidadores/{cuidador_id}")
def remover_cuidador(
    usuario_id: int,
    cuidador_id: int,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.remover_cuidador(
        usuario_logado["usuario_id"],
        usuario_id,
        cuidador_id
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.put("/{usuario_id}/cuidador-principal")
def transferir_cuidador_principal(
    usuario_id: int,
    dados: TransferenciaPrincipal,
    usuario_logado: dict = Depends(exigir_tipo_usuario("cuidador"))
):
    resposta = controller.transferir_principal(
        usuario_logado["usuario_id"],
        usuario_id,
        dados.novo_principal_id
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta
