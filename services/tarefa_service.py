from datetime import date, datetime

from repositories.tarefa_repository import TarefaRepository
from repositories.usuario_repository import UsuarioRepository


class TarefaService:
    TIPOS_VALIDOS = {"tarefas_diarias", "tarefas_educacionais"}
    PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}

    def __init__(self, repository=None, usuario_repository=None):
        self.repository = repository or TarefaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()

    def validar_prazo(self, prazo):
        if not prazo:
            return None
        try:
            return datetime.strptime(prazo, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Prazo inválido. Utilize o formato DD/MM/AAAA.")

    def listar_tarefas(self, usuario_id, tipo=None):
        return self.repository.listar_por_usuario(usuario_id, tipo)

    def buscar_tarefa(self, tarefa_id):
        tarefa = self.repository.buscar_por_id(tarefa_id)
        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")
        return tarefa

    def criar_tarefa(self, usuario_id, tipo, titulo, descricao="", prioridade="media", prazo=""):
        if self.usuario_repository.buscar_por_id(usuario_id) is None:
            raise ValueError("Usuário não encontrado.")

        titulo = (titulo or "").strip()
        if not titulo:
            raise ValueError("O título da tarefa não pode ficar vazio.")

        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("O tipo deve ser 'tarefas_diarias' ou 'tarefas_educacionais'.")

        if prioridade not in self.PRIORIDADES_VALIDAS:
            raise ValueError("A prioridade deve ser 'baixa', 'media' ou 'alta'.")

        prazo_convertido = self.validar_prazo(prazo)

        return self.repository.criar(usuario_id, tipo, titulo, descricao, prioridade, prazo_convertido)

    def editar_tarefa(self, tarefa_id, titulo=None, descricao=None, prioridade=None, prazo=None):
        self.buscar_tarefa(tarefa_id)

        if titulo is not None:
            titulo = titulo.strip()
            if not titulo:
                raise ValueError("O título da tarefa não pode ficar vazio.")

        if prioridade is not None and prioridade not in self.PRIORIDADES_VALIDAS:
            raise ValueError("A prioridade deve ser 'baixa', 'media' ou 'alta'.")

        if prazo is not None:
            prazo = self.validar_prazo(prazo)

        return self.repository.atualizar(
            tarefa_id, titulo=titulo, descricao=descricao, prioridade=prioridade, prazo=prazo
        )

    def alternar_status_tarefa(self, tarefa_id):
        tarefa = self.buscar_tarefa(tarefa_id)

        if not tarefa.concluida and tarefa.passos and not all(p.concluido for p in tarefa.passos):
            raise ValueError("Conclua todos os passos antes de marcar a tarefa como concluída.")

        return self.repository.alternar_status(tarefa_id)

    def excluir_tarefa(self, tarefa_id):
        excluida = self.repository.excluir(tarefa_id)
        if not excluida:
            raise ValueError("Tarefa não encontrada.")
        return True

    def definir_passos_ia(self, tarefa_id, lista_textos):
        self.buscar_tarefa(tarefa_id)
        if not lista_textos:
            raise ValueError("A lista de passos não pode ficar vazia.")
        return self.repository.definir_passos(tarefa_id, lista_textos)

    def alternar_status_passo(self, passo_id):
        passo = self.repository.alternar_status_passo(passo_id)
        if passo is None:
            raise ValueError("Passo não encontrado.")
        return passo

    def resumo_tarefas(self, usuario_id):
        tarefas = self.repository.listar_por_usuario(usuario_id)
        total = len(tarefas)
        concluidas = sum(1 for t in tarefas if t.concluida)
        pendentes = total - concluidas

        por_tipo = {}
        for tipo in self.TIPOS_VALIDOS:
            tarefas_tipo = [t for t in tarefas if t.tipo == tipo]
            por_tipo[tipo] = {
                "total": len(tarefas_tipo),
                "concluidas": sum(1 for t in tarefas_tipo if t.concluida),
            }

        por_prioridade = {}
        for prioridade in self.PRIORIDADES_VALIDAS:
            tarefas_prioridade = [t for t in tarefas if t.prioridade == prioridade]
            por_prioridade[prioridade] = {
                "total": len(tarefas_prioridade),
                "concluidas": sum(1 for t in tarefas_prioridade if t.concluida),
            }

        hoje = date.today()
        vencidas = sum(
            1 for t in tarefas
            if not t.concluida and t.prazo is not None and t.prazo < hoje
        )

        total_passos = sum(len(t.passos) for t in tarefas)
        passos_concluidos = sum(sum(1 for p in t.passos if p.concluido) for t in tarefas)

        return {
            "total": total,
            "concluidas": concluidas,
            "pendentes": pendentes,
            "por_tipo": por_tipo,
            "por_prioridade": por_prioridade,
            "vencidas": vencidas,
            "passos": {"total": total_passos, "concluidos": passos_concluidos},
        }
