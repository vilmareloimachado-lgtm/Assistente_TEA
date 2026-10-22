from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.permissoes import exigir_login, exigir_tipo_usuario
from controllers.material_controller import MaterialController
from services.material_service import ErroMaterial
from services.previa_link_service import PreviaLinkService


router = APIRouter(prefix="/materiais", tags=["materiais de apoio"])
controller = MaterialController()


class DadosMaterial(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str = Field(default="", max_length=2000)
    tipo: str = Field(min_length=1, max_length=100)
    link: str = Field(min_length=1, max_length=2048)
    imagem_url: str | None = Field(default=None, max_length=2048)


class NovoMaterial(DadosMaterial):
    usuario_ids: list[int] = Field(min_length=1, max_length=20)


class LinkPrevia(BaseModel):
    link: str = Field(min_length=1, max_length=2048)


def executar(funcao, *args):
    try:
        return funcao(*args)
    except ErroMaterial as erro:
        raise HTTPException(status_code=erro.status, detail=str(erro)) from erro


@router.post("/previa")
def previa(dados: LinkPrevia, payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    try:
        return {"sucesso": True, **PreviaLinkService().obter(dados.link)}
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(dados: NovoMaterial, payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    return executar(controller.criar, payload, dados.usuario_ids, dados.model_dump(exclude={"usuario_ids"}))


@router.get("/usuarios/{usuario_id}")
def listar(usuario_id: int, limite: int = Query(50, ge=1, le=100), inicio: int = Query(0, ge=0),
           payload: dict = Depends(exigir_login)):
    return executar(controller.listar, payload, usuario_id, limite, inicio)


@router.put("/usuarios/{usuario_id}/{destinatario_id}")
def editar(usuario_id: int, destinatario_id: int, dados: DadosMaterial,
           payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    return executar(controller.editar, payload, usuario_id, destinatario_id, dados.model_dump())


@router.delete("/usuarios/{usuario_id}/{destinatario_id}")
def excluir(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    return executar(controller.excluir, payload, usuario_id, destinatario_id)


@router.post("/usuarios/{usuario_id}/{destinatario_id}/aprovar")
def aprovar(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    return executar(controller.decidir, payload, usuario_id, destinatario_id, True)


@router.post("/usuarios/{usuario_id}/{destinatario_id}/recusar")
def recusar(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("cuidador"))):
    return executar(controller.decidir, payload, usuario_id, destinatario_id, False)


@router.post("/usuarios/{usuario_id}/{destinatario_id}/abrir")
def abrir(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("usuario_tea"))):
    return executar(controller.registrar, payload, usuario_id, destinatario_id, "abrir")


@router.post("/usuarios/{usuario_id}/{destinatario_id}/visto")
def visto(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("usuario_tea"))):
    return executar(controller.registrar, payload, usuario_id, destinatario_id, "visto")


@router.post("/usuarios/{usuario_id}/{destinatario_id}/remover")
def remover(usuario_id: int, destinatario_id: int, payload: dict = Depends(exigir_tipo_usuario("usuario_tea"))):
    return executar(controller.registrar, payload, usuario_id, destinatario_id, "remover")
