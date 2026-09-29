from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from controllers.ia_controller import IaController
from api.permissoes import exigir_login, exigir_mesmo_usuario, exigir_dono_da_tarefa

router = APIRouter(
    prefix="/ia",
    tags=["ia"]
)

controller = IaController()


class PerguntaChat(BaseModel):
    pergunta: str


@router.post("/{usuario_id}/chat")
def chat_livre(usuario_id: int, dados: PerguntaChat, usuario_logado: dict = Depends(exigir_mesmo_usuario)):
    resposta = controller.chat_livre(usuario_id, dados.pergunta)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta


@router.post("/tarefas/{tarefa_id}/sugerir-passos")
def sugerir_passos(tarefa_id: int, usuario_logado: dict = Depends(exigir_dono_da_tarefa)):
    resposta = controller.sugerir_passos(tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta
