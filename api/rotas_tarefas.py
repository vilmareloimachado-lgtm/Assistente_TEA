from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from controllers.tarefa_controller import TarefaController

router = APIRouter(
    prefix="/tarefas",
    tags=["tarefas"]
)

controller = TarefaController()


class NovaTarefa(BaseModel):
    titulo: str
    descricao: str = ""
    tipo: str
    prioridade: str = "media"
    prazo: str = ""


@router.get("/{usuario_id}")
def listar_tarefas(usuario_id: int):
    tarefas = controller.listar_tarefas(usuario_id)
    return {
        "dados": tarefas
    }


@router.post("/{usuario_id}", status_code=status.HTTP_201_CREATED)
def criar_tarefa(usuario_id: int, dados: NovaTarefa):
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
            status_code=422,
            detail=resposta["mensagem"]
        )

    return resposta