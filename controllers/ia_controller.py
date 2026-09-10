from services.ia_service import IaService
from services.usuario_service import UsuarioService
from services.tarefa_service import TarefaService


class IaController:
    """Orquestra as duas funcionalidades de IA do sistema:
    - Chat Livre: conversa aberta com a IA.
    - Desmembrar com IA: sugere passos para uma tarefa (o usuário decide
      aceitar, recusar ou pedir uma nova sugestão — a gravação dos passos
      aceitos é feita pelo TarefaController/TarefaService, reaproveitando
      o que já existe).
    """

    def __init__(self, ia_service=None, usuario_service=None, tarefa_service=None):
        self.ia_service = ia_service or IaService()
        self.usuario_service = usuario_service or UsuarioService()
        self.tarefa_service = tarefa_service or TarefaService()

    def chat_livre(self, usuario_id, pergunta):
        pergunta = (pergunta or "").strip()
        if not pergunta:
            return {"sucesso": False, "mensagem": "A pergunta não pode ficar vazia."}

        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if usuario is None:
            return {"sucesso": False, "mensagem": "Usuário não encontrado."}

        try:
            respostas = self.ia_service.obter_resposta_chat(pergunta, usuario)
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

        return {"sucesso": True, "mensagem": "Resposta gerada.", "respostas": respostas}

    def sugerir_passos(self, tarefa_id):
        """Gera uma sugestão de passos para a tarefa, sem salvar nada ainda."""
        try:
            tarefa = self.tarefa_service.buscar_tarefa(tarefa_id)
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

        usuario = self.usuario_service.buscar_usuario_por_id(tarefa.usuario_id)
        if usuario is None:
            return {"sucesso": False, "mensagem": "Usuário da tarefa não encontrado."}

        try:
            passos = self.ia_service.gerar_passos_tarefa(tarefa.titulo, usuario)
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

        return {"sucesso": True, "mensagem": "Passos sugeridos.", "passos": passos}
