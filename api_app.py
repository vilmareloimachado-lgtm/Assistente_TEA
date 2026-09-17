from fastapi import FastAPI

from api.rotas_usuarios import router as usuarios_router
from api.rotas_tarefas import router as tarefas_router

app = FastAPI(
    title="Assistente TEA API",
    description="API criada na Aula 04",
    version="1.0.0"
)

app.include_router(usuarios_router)
app.include_router(tarefas_router)

@app.get("/")
def inicio():
    return {
        "sistema": "Assistente TEA",
        "api": "funcionando"
    }