import unittest

from services.tarefa_service import TarefaService


class PassoFake:
    def __init__(self, texto, concluido=False, ordem=1):
        self.texto = texto
        self.concluido = concluido
        self.ordem = ordem


class TarefaFake:
    def __init__(self, id, usuario_id, tipo, titulo, descricao="", prioridade="media", prazo=None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.titulo = titulo
        self.descricao = descricao
        self.prioridade = prioridade
        self.prazo = prazo
        self.concluida = False
        self.passos = []


class TarefaRepositoryFake:
    def __init__(self):
        self.tarefas = {}
        self.proximo_id = 1

    def listar_por_usuario(self, usuario_id, tipo=None):
        resultado = [t for t in self.tarefas.values() if t.usuario_id == usuario_id]
        if tipo is not None:
            resultado = [t for t in resultado if t.tipo == tipo]
        return resultado

    def buscar_por_id(self, tarefa_id):
        return self.tarefas.get(tarefa_id)

    def criar(self, usuario_id, tipo, titulo, descricao="", prioridade="media", prazo=None):
        tarefa = TarefaFake(self.proximo_id, usuario_id, tipo, titulo, descricao, prioridade, prazo)
        self.tarefas[tarefa.id] = tarefa
        self.proximo_id += 1
        return tarefa

    def atualizar(self, tarefa_id, titulo=None, descricao=None, prioridade=None, prazo=None):
        tarefa = self.tarefas.get(tarefa_id)
        if tarefa is None:
            return None
        if titulo is not None:
            tarefa.titulo = titulo
        if descricao is not None:
            tarefa.descricao = descricao
        if prioridade is not None:
            tarefa.prioridade = prioridade
        if prazo is not None:
            tarefa.prazo = prazo
        return tarefa

    def alternar_status(self, tarefa_id):
        tarefa = self.tarefas.get(tarefa_id)
        if tarefa is None:
            return None
        tarefa.concluida = not tarefa.concluida
        return tarefa

    def excluir(self, tarefa_id):
        return self.tarefas.pop(tarefa_id, None) is not None

    def definir_passos(self, tarefa_id, lista_textos):
        tarefa = self.tarefas.get(tarefa_id)
        if tarefa is None:
            return None
        tarefa.passos = [PassoFake(texto, ordem=i) for i, texto in enumerate(lista_textos, start=1)]
        return tarefa


class UsuarioRepositoryFake:
    def __init__(self, ids_existentes):
        self.ids_existentes = set(ids_existentes)

    def buscar_por_id(self, usuario_id):
        return object() if usuario_id in self.ids_existentes else None


class TestTarefaService(unittest.TestCase):
    def setUp(self):
        self.repo = TarefaRepositoryFake()
        self.usuario_repo = UsuarioRepositoryFake(ids_existentes=[1])
        self.service = TarefaService(self.repo, self.usuario_repo)

    def test_cria_tarefa_valida(self):
        tarefa = self.service.criar_tarefa(1, "tarefas_diarias", "Organizar mochila")
        self.assertEqual(tarefa.titulo, "Organizar mochila")

    def test_nao_aceita_usuario_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.criar_tarefa(999, "tarefas_diarias", "Tarefa qualquer")

    def test_nao_aceita_titulo_vazio(self):
        with self.assertRaises(ValueError):
            self.service.criar_tarefa(1, "tarefas_diarias", "   ")

    def test_nao_aceita_tipo_invalido(self):
        with self.assertRaises(ValueError):
            self.service.criar_tarefa(1, "tipo_invalido", "Tarefa qualquer")

    def test_nao_aceita_prioridade_invalida(self):
        with self.assertRaises(ValueError):
            self.service.criar_tarefa(1, "tarefas_diarias", "Tarefa qualquer", prioridade="urgentissima")

    def test_nao_aceita_prazo_invalido(self):
        with self.assertRaises(ValueError):
            self.service.criar_tarefa(1, "tarefas_diarias", "Tarefa qualquer", prazo="31-13-2026")

    def test_nao_permite_concluir_com_passo_pendente(self):
        tarefa = self.service.criar_tarefa(1, "tarefas_diarias", "Estudar Python")
        self.service.definir_passos_ia(tarefa.id, ["Ler capítulo 1", "Fazer exercícios"])

        with self.assertRaises(ValueError):
            self.service.alternar_status_tarefa(tarefa.id)

    def test_permite_concluir_com_passos_todos_feitos(self):
        tarefa = self.service.criar_tarefa(1, "tarefas_diarias", "Estudar Python")
        self.service.definir_passos_ia(tarefa.id, ["Ler capítulo 1"])
        tarefa.passos[0].concluido = True

        atualizada = self.service.alternar_status_tarefa(tarefa.id)
        self.assertTrue(atualizada.concluida)

    def test_resumo_tarefas_traz_metricas_por_tipo_prioridade_e_passos(self):
        t1 = self.service.criar_tarefa(1, "tarefas_diarias", "Arrumar a cama", prioridade="baixa")
        t2 = self.service.criar_tarefa(1, "tarefas_educacionais", "Estudar frações", prioridade="alta")
        self.service.definir_passos_ia(t2.id, ["Ler capítulo 1", "Fazer exercícios"])
        t2.passos[0].concluido = True

        resumo = self.service.resumo_tarefas(1)

        self.assertEqual(resumo["total"], 2)
        self.assertEqual(resumo["por_tipo"]["tarefas_diarias"]["total"], 1)
        self.assertEqual(resumo["por_tipo"]["tarefas_educacionais"]["total"], 1)
        self.assertEqual(resumo["por_prioridade"]["alta"]["total"], 1)
        self.assertEqual(resumo["por_prioridade"]["baixa"]["total"], 1)
        self.assertEqual(resumo["passos"]["total"], 2)
        self.assertEqual(resumo["passos"]["concluidos"], 1)
        self.assertEqual(resumo["vencidas"], 0)


if __name__ == "__main__":
    unittest.main()
