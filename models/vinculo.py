from sqlalchemy import Boolean, Column, ForeignKey, Integer, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func

from config.database import Base
from models.usuario import Usuario  # garante que a tabela "usuarios" esteja registrada


class Vinculo(Base):
    __tablename__ = "vinculos"
    __table_args__ = (
        UniqueConstraint("cuidador_id", "usuario_id", name="uq_vinculos_cuidador_usuario"),
    )

    id = Column(Integer, primary_key=True)
    cuidador_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    principal = Column(Boolean, nullable=False, default=False)
    criado_em = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return (
            f"Vinculo(id={self.id}, "
            f"cuidador_id={self.cuidador_id}, "
            f"usuario_id={self.usuario_id}, "
            f"principal={self.principal})"
        )