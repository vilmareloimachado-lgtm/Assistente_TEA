from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum("tarefas_diarias", "tarefas_educacionais"), nullable=False)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    prioridade = Column(Enum("baixa", "media", "alta"), nullable=False, default="media")
    prazo = Column(Date)
    concluida = Column(Boolean, nullable=False, default=False)
    criado_em = Column(TIMESTAMP, server_default=func.now())

    passos = relationship(
        "Passo",
        back_populates="tarefa",
        cascade="all, delete-orphan",
        order_by="Passo.ordem"
    )

    def __repr__(self):
        return (
            f"Tarefa(id={self.id}, "
            f"titulo='{self.titulo}', "
            f"tipo='{self.tipo}', "
            f"concluida={self.concluida})"
        )
