from services.material_service import MaterialService


class MaterialController:
    def __init__(self, service=None):
        self.service = service or MaterialService()

    def listar(self, payload, usuario_id, limite=50, inicio=0):
        return self.service.listar(payload, usuario_id, limite, inicio)

    def criar(self, payload, usuario_ids, dados):
        return self.service.criar(payload, usuario_ids, dados)

    def editar(self, payload, usuario_id, destinatario_id, dados):
        return self.service.editar(payload, usuario_id, destinatario_id, dados)

    def decidir(self, payload, usuario_id, destinatario_id, aprovar):
        return self.service.decidir(payload, usuario_id, destinatario_id, aprovar)

    def registrar(self, payload, usuario_id, destinatario_id, acao):
        return self.service.registrar(payload, usuario_id, destinatario_id, acao)

    def excluir(self, payload, usuario_id, destinatario_id):
        return self.service.excluir(payload, usuario_id, destinatario_id)
