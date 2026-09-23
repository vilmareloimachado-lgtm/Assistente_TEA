from fastapi import FastAPI

from api.rotas_usuarios import router as usuarios_router
from api.rotas_tarefas import router as tarefas_router
from api.rotas_passos import router as passos_router
from api.rotas_ia import router as ia_router

app = FastAPI(
    title="Assistente TEA API",
    description="API criada na Aula 04",
    version="1.0.0"
)

app.include_router(usuarios_router)
app.include_router(tarefas_router)
app.include_router(passos_router)
app.include_router(ia_router)


@app.get("/")
def inicio():
    return {
        "sistema": "Assistente TEA",
        "api": "funcionando"
    }