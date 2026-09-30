from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config.database import SessionLocal
from models.tarefa import Tarefa
from models.passo import Passo


class TarefaRepository:
    def listar_por_usuario(self, usuario_id, tipo=None):
        with SessionLocal() as session:
            comando = (
                select(Tarefa)
                .options(selectinload(Tarefa.passos))
                .where(Tarefa.usuario_id == usuario_id)
            )
            if tipo is not None:
                comando = comando.where(Tarefa.tipo == tipo)
            comando = comando.order_by(Tarefa.id)
            return list(session.scalars(comando))

    def buscar_por_id(self, tarefa_id):
        with SessionLocal() as session:
            comando = (
                select(Tarefa)
                .options(selectinload(Tarefa.passos))
                .where(Tarefa.id == tarefa_id)
            )
            return session.scalar(comando)

    def criar(self, usuario_id, tipo, titulo, descricao="", prioridade="media", prazo=None):
        with SessionLocal() as session:
            tarefa = Tarefa(
                usuario_id=usuario_id,
                tipo=tipo,
                titulo=titulo,
                descricao=descricao,
                prioridade=prioridade,
                prazo=prazo,
                concluida=False
            )
            session.add(tarefa)
            session.commit()
            session.refresh(tarefa)
            # Carrega a lista de passos (vazia, mas evita DetachedInstanceError depois)
            _ = tarefa.passos
            return tarefa

    def atualizar(self, tarefa_id, titulo=None, descricao=None, prioridade=None, prazo=None):
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
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

            session.commit()
            session.refresh(tarefa)
            _ = tarefa.passos
            return tarefa

    def alternar_status(self, tarefa_id):
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            if tarefa is None:
                return None

            tarefa.concluida = not tarefa.concluida
            session.commit()
            session.refresh(tarefa)
            _ = tarefa.passos
            return tarefa

    def excluir(self, tarefa_id):
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            if tarefa is None:
                return False

            session.delete(tarefa)
            session.commit()
            return True

    def definir_passos(self, tarefa_id, lista_textos):
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            if tarefa is None:
                return None

            for passo_antigo in list(tarefa.passos):
                session.delete(passo_antigo)
            session.flush()

            for ordem, texto in enumerate(lista_textos, start=1):
                session.add(Passo(tarefa_id=tarefa_id, texto=texto, concluido=False, ordem=ordem))

            session.commit()
            session.refresh(tarefa)
            _ = tarefa.passos
            return tarefa

    def alternar_status_passo(self, passo_id):
        with SessionLocal() as session:
            passo = session.get(Passo, passo_id)
            if passo is None:
                return None

            passo.concluido = not passo.concluido
            session.commit()
            session.refresh(passo)
            return passo

    def buscar_passo_por_id(self, passo_id):
        with SessionLocal() as session:
            return session.get(Passo, passo_id)

    def excluir_passo(self, passo_id):
        # Apaga o passo e renumera os que sobraram da mesma tarefa (1, 2, 3...),
        # tudo na mesma transacao: ou faz as duas coisas, ou nenhuma.
        # Devolve True se apagou e False se o passo nao existe.
        with SessionLocal() as session:
            passo = session.get(Passo, passo_id)
            if passo is None:
                return False

            tarefa = session.get(Tarefa, passo.tarefa_id)

            # Os que ficam, na ordem atual (em caso de empate, o mais antigo primeiro).
            restantes = sorted(
                [p for p in tarefa.passos if p.id != passo_id],
                key=lambda p: (p.ordem, p.id)
            )

            session.delete(passo)

            for nova_ordem, restante in enumerate(restantes, start=1):
                restante.ordem = nova_ordem

            session.commit()
            return True