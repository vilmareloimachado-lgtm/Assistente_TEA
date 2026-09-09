from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from config.database import Base


class Passo(Base):
    __tablename__ = "passos"

    id = Column(Integer, primary_key=True)
    tarefa_id = Column(Integer, ForeignKey("tarefas.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)
    concluido = Column(Boolean, nullable=False, default=False)
    ordem = Column(Integer, nullable=False, default=1)

    tarefa = relationship("Tarefa", back_populates="passos")

    def __repr__(self):
        return f"Passo(id={self.id}, texto='{self.texto}', concluido={self.concluido})"
