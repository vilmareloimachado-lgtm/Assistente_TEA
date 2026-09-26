from fastapi import HTTPException, status, Header, Depends

from config.auth import validar_token


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

def exigir_mesmo_usuario(usuario_id: int):
    def verificador(payload: dict = Depends(exigir_login)):
        if payload.get("tipo_usuario") == "cuidador":
            return payload

        if payload.get("usuario_id") != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar dados de outro usuário."
            )

        return payload

    return verificador