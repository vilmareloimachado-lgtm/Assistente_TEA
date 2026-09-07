from sqlalchemy import select 
 
from config.database import SessionLocal 
from models.usuario import Usuario 
 
 
class UsuarioRepository: 
    def listar(self): 
        with SessionLocal() as session: 
            comando = select(Usuario).order_by(Usuario.nome) 
            return list(session.scalars(comando)) 
 
    def buscar_por_nome(self, nome): 
        with SessionLocal() as session: 
            comando = select(Usuario).where(Usuario.nome == nome) 
            return session.scalar(comando) 
 
    def criar(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login, criado_em=None): 
        with SessionLocal() as session: 
            usuario = Usuario( 
                nome=nome, 
                estilo_instrucao=estilo_instrucao, 
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento,
                senha_login=senha_login
            )
            if criado_em is not None:
                usuario.criado_em = criado_em
            session.add(usuario) 
            session.commit() 
            session.refresh(usuario) 
            return usuario
            
    def excluir_por_nome(self, nome): 
        with SessionLocal() as session: 
            usuario = session.scalar( 
                select(Usuario).where(Usuario.nome == nome) 
            ) 
            if usuario is None: 
                return False 
 
            session.delete(usuario) 
            session.commit() 
            return True 