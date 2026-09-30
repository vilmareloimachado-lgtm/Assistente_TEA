from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from config.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    estilo_instrucao = Column(String(20), nullable=False, default="direto")
    nivel_suporte = Column(String(20), nullable=False, default="Leve")
    data_nascimento = Column(DateTime)
    senha_login = Column(String(255), nullable=True)
    email = Column(String(150), unique=True, nullable=True)
    pin_hash = Column(String(255), nullable=True)
    tipo_usuario = Column(String(20), nullable=False, default="cuidador")
    criado_em = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return (
            f"Usuario(id={self.id}, "
            f"nome='{self.nome}', "
            f"tipo='{self.tipo_usuario}', "
            f"estilo='{self.estilo_instrucao}', "
            f"suporte='{self.nivel_suporte}', "
            f"nascimento='{self.data_nascimento}')"
        )
    