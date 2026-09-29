from fastapi import HTTPException, status, Header, Depends

from config.auth import validar_token
from services.tarefa_service import TarefaService

tarefa_service = TarefaService()


def exigir_login(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não enviado. Faça login primeiro."
        )

    partes = authorization.split(" ")
    if len(partes) != 2 or partes[0] != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato do token inválido. Use: Bearer <token>."
        )

    token = partes[1]

    try:
        return validar_token(token)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro)
        )


def exigir_tipo_usuario(*tipos_permitidos):
    def verificador(payload: dict = Depends(exigir_login)):
        if payload.get("tipo_usuario") not in tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso."
            )
        return payload

    return verificador

def exigir_mesmo_usuario(usuario_id: int, payload: dict = Depends(exigir_login)):
    if payload.get("tipo_usuario") == "cuidador":
        return payload

    if payload.get("usuario_id") != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar dados de outro usuário."
        )

    return payload

def exigir_dono_da_tarefa(tarefa_id: int, payload: dict = Depends(exigir_login)):
    if payload.get("tipo_usuario") == "cuidador":
        return payload

    try:
        tarefa = tarefa_service.buscar_tarefa(tarefa_id)
    except ValueError:
        return payload

    if tarefa.usuario_id != payload.get("usuario_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar tarefas de outro usuário."
        )

    return payload

def exigir_dono_do_passo(passo_id: int, payload: dict = Depends(exigir_login)):
    if payload.get("tipo_usuario") == "cuidador":
        return payload

    try:
        passo = tarefa_service.buscar_passo(passo_id)
        tarefa = tarefa_service.buscar_tarefa(passo.tarefa_id)
    except ValueError:
        return payload

    if tarefa.usuario_id != payload.get("usuario_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar passos de outro usuário."
        )

    return payload
