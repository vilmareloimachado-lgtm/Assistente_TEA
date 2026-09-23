
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
 
    def buscar_por_id(self, usuario_id):
        with SessionLocal() as session:
            return session.get(Usuario, usuario_id)

    def buscar_por_email(self, email):
        with SessionLocal() as session:
            comando = select(Usuario).where(Usuario.email == email)
            return session.scalar(comando)

    def criar(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login, email, tipo_usuario="cuidador", criado_em=None): 
        with SessionLocal() as session: 
            usuario = Usuario( 
                nome=nome, 
                estilo_instrucao=estilo_instrucao, 
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento,
                senha_login=senha_login,
                email=email,
                tipo_usuario=tipo_usuario   
            )
            if criado_em is not None:
                usuario.criado_em = criado_em
            session.add(usuario) 
            session.commit() 
            session.refresh(usuario) 
            return usuario
            
    def atualizar_por_nome(self, nome, novo_nome=None, estilo_instrucao=None,
                        nivel_suporte=None, data_nascimento=None, senha_login=None,
                        email=None, tipo_usuario=None):
        with SessionLocal() as session:
            usuario = session.scalar(
                select(Usuario).where(Usuario.nome == nome)
            )
            if usuario is None:
                return None

            if novo_nome is not None:
                usuario.nome = novo_nome
            if estilo_instrucao is not None:
                usuario.estilo_instrucao = estilo_instrucao
            if nivel_suporte is not None:
                usuario.nivel_suporte = nivel_suporte
            if data_nascimento is not None:
                usuario.data_nascimento = data_nascimento
            if senha_login is not None:
                usuario.senha_login = senha_login
            if email is not None:
                usuario.email = email
            if tipo_usuario is not None:
                usuario.tipo_usuario = tipo_usuario

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