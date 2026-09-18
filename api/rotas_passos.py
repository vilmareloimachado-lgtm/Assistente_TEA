from fastapi import APIRouter, HTTPException, status

from controllers.tarefa_controller import TarefaController

router = APIRouter(
    prefix="/passos",
    tags=["passos"]
)

controller = TarefaController()


@router.patch("/{passo_id}/status")
def alternar_status_passo(passo_id: int):
    resposta = controller.alternar_status_passo(passo_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta