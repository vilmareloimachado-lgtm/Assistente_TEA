from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from controllers.tarefa_controller import TarefaController
from api.permissoes import (
    exigir_mesmo_usuario,
    exigir_dono_da_tarefa,
    exigir_cuidador_para_excluir_tarefa
)


router = APIRouter(
    prefix="/tarefas",
    tags=["tarefas"]
)

controller = TarefaController()


# ------------------------------------------------------------
# Modelos de entrada
# ------------------------------------------------------------
class NovaTarefa(BaseModel):
    titulo: str
    descricao: str = ""
    tipo: str
    prioridade: str = "media"
    prazo: str = ""


class NovosPassos(BaseModel):
    textos: list[str]


class TarefaAtualizacao(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    prioridade: str | None = None
    prazo: str | None = None


# ------------------------------------------------------------
# Listar tarefas de um usuário
# ------------------------------------------------------------
@router.get("/{usuario_id}")
def listar_tarefas(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_mesmo_usuario)
):
    tarefas = controller.listar_tarefas(usuario_id)

    return {
        "dados": tarefas
    }


# ------------------------------------------------------------
# Criar tarefa
# ------------------------------------------------------------
@router.post("/{usuario_id}", status_code=status.HTTP_201_CREATED)
def criar_tarefa(
    usuario_id: int,
    dados: NovaTarefa,
    usuario_logado: dict = Depends(exigir_mesmo_usuario)
):
    resposta = controller.criar_tarefa(
        usuario_id,
        dados.tipo,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Definir passos da tarefa
# ------------------------------------------------------------
@router.post("/{tarefa_id}/passos", status_code=status.HTTP_201_CREATED)
def definir_passos(
    tarefa_id: int,
    dados: NovosPassos,
    usuario_logado: dict = Depends(exigir_dono_da_tarefa)
):
    resposta = controller.definir_passos_ia(
        tarefa_id,
        dados.textos
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------
@router.get("/{usuario_id}/dashboard")
def dashboard(
    usuario_id: int,
    usuario_logado: dict = Depends(exigir_mesmo_usuario)
):
    return controller.resumo_tarefas(usuario_id)


# ------------------------------------------------------------
# Editar tarefa
# ------------------------------------------------------------
@router.put("/{tarefa_id}")
def editar_tarefa(
    tarefa_id: int,
    dados: TarefaAtualizacao,
    usuario_logado: dict = Depends(exigir_dono_da_tarefa)
):
    resposta = controller.editar_tarefa(
        tarefa_id,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Alterar status da tarefa
# ------------------------------------------------------------
@router.patch("/{tarefa_id}/status")
def alternar_status_tarefa(
    tarefa_id: int,
    usuario_logado: dict = Depends(exigir_dono_da_tarefa)
):
    resposta = controller.alternar_status_tarefa(tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


# ------------------------------------------------------------
# Excluir tarefa
# ------------------------------------------------------------
@router.delete("/{tarefa_id}")
def excluir_tarefa(
    tarefa_id: int,
    usuario_logado: dict = Depends(
        exigir_cuidador_para_excluir_tarefa
    )
):
    resposta = controller.excluir_tarefa(tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta