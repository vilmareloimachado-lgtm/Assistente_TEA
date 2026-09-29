from fastapi import APIRouter, HTTPException, status, Depends

from controllers.tarefa_controller import TarefaController
from api.permissoes import exigir_dono_do_passo

router = APIRouter(
    prefix="/passos",
    tags=["passos"]
)

controller = TarefaController()


@router.patch("/{passo_id}/status")
def alternar_status_passo(passo_id: int, usuario_logado: dict = Depends(exigir_dono_do_passo)):
    resposta = controller.alternar_status_passo(passo_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resposta["mensagem"]
        )

    return resposta