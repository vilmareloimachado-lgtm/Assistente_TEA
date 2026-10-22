from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base
from models.usuario import Usuario  # registra a tabela referenciada pelas chaves estrangeiras


class Material(Base):
    __tablename__ = "materiais"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False, default="")
    tipo = Column(String(100), nullable=False)
    link = Column(String(2048), nullable=False)
    imagem_url = Column(String(2048), nullable=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"))
    autor_nome = Column(String(100), nullable=False)
    criado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), server_default=func.now())


class MaterialDestinatario(Base):
    __tablename__ = "materiais_destinatarios"
    __table_args__ = (
        UniqueConstraint("material_id", "usuario_id", name="uq_material_destinatario"),
    )

    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey("materiais.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    situacao = Column(String(20), nullable=False, default="pendente")
    aprovado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"))
    aprovado_em = Column(DateTime)
    aberto_em = Column(DateTime)
    visto_em = Column(DateTime)
    removido_em = Column(DateTime)
    criado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), server_default=func.now())

    material = relationship(Material, lazy="joined")
