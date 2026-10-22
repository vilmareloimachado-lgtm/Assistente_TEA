from contextlib import contextmanager

from sqlalchemy import func, select

from config.database import SessionLocal
from models.material import Material, MaterialDestinatario
from models.usuario import Usuario
from models.vinculo import Vinculo


class MaterialRepository:
    def __init__(self, session=None, session_factory=None):
        self.session = session
        self.session_factory = session_factory or SessionLocal

    @contextmanager
    def transacao(self):
        with self.session_factory() as session:
            with session.begin():
                yield MaterialRepository(session=session, session_factory=self.session_factory)

    def usuario(self, usuario_id):
        return self.session.get(Usuario, usuario_id)

    def vinculo(self, cuidador_id, usuario_id):
        return self.session.scalar(select(Vinculo).where(
            Vinculo.cuidador_id == cuidador_id, Vinculo.usuario_id == usuario_id
        ))

    def novo_material(self, **dados):
        material = Material(**dados)
        self.session.add(material)
        self.session.flush()
        return material

    def novo_destinatario(self, material, **dados):
        destinatario = MaterialDestinatario(material=material, **dados)
        self.session.add(destinatario)
        self.session.flush()
        return destinatario

    def destinatario(self, destinatario_id, usuario_id, bloquear=False):
        comando = select(MaterialDestinatario).where(
            MaterialDestinatario.id == destinatario_id,
            MaterialDestinatario.usuario_id == usuario_id
        )
        if bloquear:
            comando = comando.with_for_update()
        return self.session.scalar(comando)

    def listar(self, usuario_id, cuidador_id=None, principal=False, limite=50, inicio=0):
        comando = select(MaterialDestinatario).join(Material).where(
            MaterialDestinatario.usuario_id == usuario_id
        )
        if cuidador_id is None:
            comando = comando.where(
                MaterialDestinatario.situacao == "aprovado",
                MaterialDestinatario.removido_em.is_(None)
            )
        elif not principal:
            comando = comando.where(
                (MaterialDestinatario.situacao == "aprovado") | (Material.autor_id == cuidador_id)
            )
        total = self.session.scalar(select(func.count()).select_from(comando.subquery()))
        comando = comando.order_by(
            MaterialDestinatario.criado_em.desc(), MaterialDestinatario.id.desc()
        ).offset(inicio).limit(limite)
        return list(self.session.scalars(comando)), total

    def tipos(self, usuario_id, cuidador_id=None, principal=False):
        comando = select(Material.tipo).join(MaterialDestinatario).where(
            MaterialDestinatario.usuario_id == usuario_id
        )
        if cuidador_id is None:
            comando = comando.where(
                MaterialDestinatario.situacao == "aprovado",
                MaterialDestinatario.removido_em.is_(None)
            )
        elif not principal:
            comando = comando.where(
                (MaterialDestinatario.situacao == "aprovado") | (Material.autor_id == cuidador_id)
            )
        return list(self.session.scalars(comando.distinct().order_by(Material.tipo).limit(100)))

    def substituir_material(self, destinatario, **dados):
        # A edição vale somente para este destinatário. Os outros preservam sua cópia.
        antigo_id = destinatario.material_id
        destinatario.material = self.novo_material(**dados)
        self.session.flush()
        self._limpar_material_sem_destinatarios(antigo_id)

    def excluir(self, destinatario):
        material_id = destinatario.material_id
        self.session.delete(destinatario)
        self.session.flush()
        self._limpar_material_sem_destinatarios(material_id)

    def _limpar_material_sem_destinatarios(self, material_id):
        existe = self.session.scalar(select(MaterialDestinatario.id).where(
            MaterialDestinatario.material_id == material_id
        ).limit(1))
        if existe is None:
            material = self.session.get(Material, material_id)
            if material is not None:
                self.session.delete(material)
