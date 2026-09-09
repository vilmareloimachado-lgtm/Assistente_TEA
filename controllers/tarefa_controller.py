from services.tarefa_service import TarefaService


class TarefaController:
    def __init__(self, service=None):
        self.service = service or TarefaService()

    def listar_tarefas(self, usuario_id, tipo=None):
        tarefas = self.service.listar_tarefas(usuario_id, tipo)
        return [self._formatar(t) for t in tarefas]

    def buscar_tarefa(self, tarefa_id):
        try:
            tarefa = self.service.buscar_tarefa(tarefa_id)
            return {"sucesso": True, **self._formatar(tarefa)}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def criar_tarefa(self, usuario_id, tipo, titulo, descricao="", prioridade="media", prazo=""):
        try:
            tarefa = self.service.criar_tarefa(usuario_id, tipo, titulo, descricao, prioridade, prazo)
            return {
                "sucesso": True,
                "mensagem": f"Tarefa '{tarefa.titulo}' criada.",
                "tarefa_id": tarefa.id
            }
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def editar_tarefa(self, tarefa_id, titulo=None, descricao=None, prioridade=None, prazo=None):
        try:
            tarefa = self.service.editar_tarefa(tarefa_id, titulo, descricao, prioridade, prazo)
            return {"sucesso": True, "mensagem": f"Tarefa '{tarefa.titulo}' atualizada."}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def alternar_status_tarefa(self, tarefa_id):
        try:
            tarefa = self.service.alternar_status_tarefa(tarefa_id)
            status = "concluída" if tarefa.concluida else "pendente"
            return {"sucesso": True, "mensagem": f"Tarefa marcada como {status}."}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def excluir_tarefa(self, tarefa_id):
        try:
            self.service.excluir_tarefa(tarefa_id)
            return {"sucesso": True, "mensagem": "Tarefa excluída com sucesso."}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def definir_passos_ia(self, tarefa_id, lista_textos):
        try:
            tarefa = self.service.definir_passos_ia(tarefa_id, lista_textos)
            return {"sucesso": True, "mensagem": f"{len(tarefa.passos)} passo(s) definido(s)."}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def alternar_status_passo(self, passo_id):
        try:
            passo = self.service.alternar_status_passo(passo_id)
            status = "concluído" if passo.concluido else "pendente"
            return {"sucesso": True, "mensagem": f"Passo marcado como {status}."}
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def resumo_tarefas(self, usuario_id):
        return self.service.resumo_tarefas(usuario_id)

    def _formatar(self, tarefa):
        return {
            "tarefa_id": tarefa.id,
            "titulo": tarefa.titulo,
            "descricao": tarefa.descricao,
            "tipo": tarefa.tipo,
            "prioridade": tarefa.prioridade,
            "prazo": tarefa.prazo.strftime("%d/%m/%Y") if tarefa.prazo else "",
            "concluida": tarefa.concluida,
            "passos": [{"texto": p.texto, "concluido": p.concluido} for p in tarefa.passos]
        }
