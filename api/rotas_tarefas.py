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

class NovosPassos(BaseModel):
    textos: list[str]

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta

@router.post("/{tarefa_id}/passos", status_code=status.HTTP_201_CREATED)
def definir_passos(tarefa_id: int, dados: NovosPassos):
    resposta = controller.definir_passos_ia(tarefa_id, dados.textos)
    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta

@router.get("/{usuario_id}/dashboard")
def dashboard(usuario_id: int):
    return controller.resumo_tarefas(usuario_id)

