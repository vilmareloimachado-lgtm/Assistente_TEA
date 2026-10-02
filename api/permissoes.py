from fastapi import HTTPException, status, Header, Depends

from config.auth import validar_token
from services.tarefa_service import TarefaService
from repositories.usuario_repository import UsuarioRepository


tarefa_service = TarefaService()
usuario_repository = UsuarioRepository()


# ------------------------------------------------------------
# Login
# ------------------------------------------------------------
def exigir_login(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não informado."
        )

    partes = authorization.split()

    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato do token inválido."
        )

    token = partes[1]

    try:
        return validar_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )


# ------------------------------------------------------------
# Tipo de usuário
# ------------------------------------------------------------
def exigir_tipo_usuario(*tipos_permitidos):
    def verificar(payload: dict = Depends(exigir_login)):
        if payload.get("tipo_usuario") not in tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta operação."
            )

        return payload

    return verificar


# ------------------------------------------------------------
# Vínculo cuidador → usuário TEA
# ------------------------------------------------------------
def _exigir_vinculo_cuidador(cuidador_id: int, usuario_id: int):
    vinculo = usuario_repository.buscar_vinculo(
        cuidador_id,
        usuario_id
    )

    if vinculo is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este perfil."
        )

    return vinculo


# ------------------------------------------------------------
# Acesso aos dados de um usuário TEA
# ------------------------------------------------------------
def exigir_mesmo_usuario(
    usuario_id: int,
    payload: dict = Depends(exigir_login)
):
    tipo_usuario = payload.get("tipo_usuario")
    usuario_logado_id = payload.get("usuario_id")

    # Usuário TEA só acessa os próprios dados.
    if tipo_usuario == "usuario_tea":
        if usuario_logado_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar dados de outro usuário."
            )

        return payload

    # Cuidador só acessa usuários TEA vinculados a ele.
    if tipo_usuario == "cuidador":
        _exigir_vinculo_cuidador(
            usuario_logado_id,
            usuario_id
        )

        return payload

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para realizar esta operação."
    )


# ------------------------------------------------------------
# Acesso a uma tarefa
# ------------------------------------------------------------
def exigir_dono_da_tarefa(
    tarefa_id: int,
    payload: dict = Depends(exigir_login)
):
    try:
        tarefa = tarefa_service.buscar_tarefa_por_id(tarefa_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada."
        )

    tipo_usuario = payload.get("tipo_usuario")
    usuario_logado_id = payload.get("usuario_id")

    # Usuário TEA só acessa tarefas próprias.
    if tipo_usuario == "usuario_tea":
        if tarefa.usuario_id != usuario_logado_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta tarefa."
            )

        return payload

    # Cuidador precisa estar vinculado ao dono da tarefa.
    if tipo_usuario == "cuidador":
        _exigir_vinculo_cuidador(
            usuario_logado_id,
            tarefa.usuario_id
        )

        return payload

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para realizar esta operação."
    )


# ------------------------------------------------------------
# Acesso a um passo
# ------------------------------------------------------------
def exigir_dono_do_passo(
    passo_id: int,
    payload: dict = Depends(exigir_login)
):
    try:
        passo = tarefa_service.buscar_passo_por_id(passo_id)
        tarefa = tarefa_service.buscar_tarefa_por_id(
            passo.tarefa_id
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passo não encontrado."
        )

    tipo_usuario = payload.get("tipo_usuario")
    usuario_logado_id = payload.get("usuario_id")

    # Usuário TEA só acessa passos das próprias tarefas.
    if tipo_usuario == "usuario_tea":
        if tarefa.usuario_id != usuario_logado_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este passo."
            )

        return payload

    # Cuidador precisa estar vinculado ao usuário dono da tarefa.
    if tipo_usuario == "cuidador":
        _exigir_vinculo_cuidador(
            usuario_logado_id,
            tarefa.usuario_id
        )

        return payload

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para realizar esta operação."
    )
