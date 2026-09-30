from sqlalchemy import select

from config.database import SessionLocal
from models.usuario import Usuario
from models.vinculo import Vinculo


class UsuarioRepository:
    # ------------------------------------------------------------
    # Metodos que ja existiam
    # ------------------------------------------------------------
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

    def criar(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login,
              email, tipo_usuario="cuidador", criado_em=None, pin_hash=None):
        with SessionLocal() as session:
            usuario = Usuario(
                nome=nome,
                estilo_instrucao=estilo_instrucao,
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento,
                senha_login=senha_login,
                email=email,
                pin_hash=pin_hash,
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

    # ------------------------------------------------------------
    # Novos: usuarios TEA e vinculos com cuidadores
    # ------------------------------------------------------------
    def criar_usuario_tea_com_vinculo(self, cuidador_id, nome, estilo_instrucao,
                                      nivel_suporte, data_nascimento, pin_hash=None):
        # Cria o usuario TEA e o vinculo (cuidador principal) na MESMA transacao:
        # ou grava os dois, ou nao grava nenhum.
        with SessionLocal() as session:
            usuario = Usuario(
                nome=nome,
                estilo_instrucao=estilo_instrucao,
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento,
                pin_hash=pin_hash,
                tipo_usuario="usuario_tea"
            )
            session.add(usuario)
            session.flush()  # gera o id do usuario sem finalizar a transacao

            session.add(Vinculo(
                cuidador_id=cuidador_id,
                usuario_id=usuario.id,
                principal=True
            ))
            session.commit()
            session.refresh(usuario)
            return usuario

    def listar_usuarios_do_cuidador(self, cuidador_id):
        with SessionLocal() as session:
            comando = (
                select(Usuario)
                .join(Vinculo, Vinculo.usuario_id == Usuario.id)
                .where(Vinculo.cuidador_id == cuidador_id)
                .order_by(Usuario.nome)
            )
            return list(session.scalars(comando))

    def listar_cuidadores_do_usuario(self, usuario_id):
        # O principal aparece primeiro; depois os adicionais, do mais antigo ao mais novo.
        with SessionLocal() as session:
            comando = (
                select(Usuario)
                .join(Vinculo, Vinculo.cuidador_id == Usuario.id)
                .where(Vinculo.usuario_id == usuario_id)
                .order_by(Vinculo.principal.desc(), Vinculo.id)
            )
            return list(session.scalars(comando))

    def nome_existe_para_cuidador(self, cuidador_id, nome, ignorar_usuario_id=None):
        # Diz se o cuidador ja tem, entre os usuarios dele, alguem com esse nome.
        with SessionLocal() as session:
            comando = (
                select(Usuario.id)
                .join(Vinculo, Vinculo.usuario_id == Usuario.id)
                .where(Vinculo.cuidador_id == cuidador_id, Usuario.nome == nome)
            )
            if ignorar_usuario_id is not None:
                comando = comando.where(Usuario.id != ignorar_usuario_id)
            return session.scalar(comando) is not None

    def buscar_vinculo(self, cuidador_id, usuario_id):
        with SessionLocal() as session:
            comando = select(Vinculo).where(
                Vinculo.cuidador_id == cuidador_id,
                Vinculo.usuario_id == usuario_id
            )
            return session.scalar(comando)

    def criar_vinculo(self, cuidador_id, usuario_id, principal=False):
        with SessionLocal() as session:
            vinculo = Vinculo(
                cuidador_id=cuidador_id,
                usuario_id=usuario_id,
                principal=principal
            )
            session.add(vinculo)
            session.commit()
            session.refresh(vinculo)
            return vinculo

    def remover_vinculo(self, cuidador_id, usuario_id):
        with SessionLocal() as session:
            vinculo = session.scalar(
                select(Vinculo).where(
                    Vinculo.cuidador_id == cuidador_id,
                    Vinculo.usuario_id == usuario_id
                )
            )
            if vinculo is None:
                return False

            session.delete(vinculo)
            session.commit()
            return True

    def definir_principal(self, cuidador_id, usuario_id):
        # Deixa este cuidador como o unico principal do usuario TEA.
        with SessionLocal() as session:
            vinculos = list(session.scalars(
                select(Vinculo).where(Vinculo.usuario_id == usuario_id)
            ))

            escolhido = None
            for vinculo in vinculos:
                vinculo.principal = (vinculo.cuidador_id == cuidador_id)
                if vinculo.principal:
                    escolhido = vinculo

            if escolhido is None:
                session.rollback()
                return False

            session.commit()
            return True

    def atualizar_por_id(self, usuario_id, nome=None, estilo_instrucao=None,
                         nivel_suporte=None, data_nascimento=None, senha_login=None,
                         email=None):
        # Nao muda o tipo do usuario: cuidador nao vira usuario_tea nem o contrario.
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if usuario is None:
                return None

            if nome is not None:
                usuario.nome = nome
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

            session.commit()
            session.refresh(usuario)
            return usuario

    def definir_pin_hash(self, usuario_id, pin_hash):
        # pin_hash = None remove o PIN do usuario.
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if usuario is None:
                return None

            usuario.pin_hash = pin_hash
            session.commit()
            session.refresh(usuario)
            return usuario

    def excluir_por_id(self, usuario_id):
        # O banco apaga junto as tarefas, os passos e os vinculos do usuario.
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if usuario is None:
                return False

            session.delete(usuario)
            session.commit()
            return True

    def excluir_cuidador_em_cadeia(self, cuidador_id):
        # Tudo acontece numa unica transacao: ou faz tudo, ou nao faz nada.
        # Para cada usuario TEA que este cuidador acompanha:
        #   - se ele tem outros cuidadores, continua existindo; se o cuidador
        #     que sai era o principal, o vinculo mais antigo vira o principal;
        #   - se este era o unico cuidador, o usuario TEA e apagado
        #     (o banco apaga junto as tarefas e os passos dele).
        # No fim, o cuidador e apagado (o banco apaga os vinculos e as tarefas dele).
        with SessionLocal() as session:
            cuidador = session.get(Usuario, cuidador_id)
            if cuidador is None:
                return False

            meus_vinculos = list(session.scalars(
                select(Vinculo).where(Vinculo.cuidador_id == cuidador_id)
            ))

            for meu_vinculo in meus_vinculos:
                outros = list(session.scalars(
                    select(Vinculo)
                    .where(
                        Vinculo.usuario_id == meu_vinculo.usuario_id,
                        Vinculo.cuidador_id != cuidador_id
                    )
                    .order_by(Vinculo.id)
                ))

                if not outros:
                    usuario_tea = session.get(Usuario, meu_vinculo.usuario_id)
                    if usuario_tea is not None:
                        session.delete(usuario_tea)
                elif meu_vinculo.principal:
                    outros[0].principal = True

            session.delete(cuidador)
            session.commit()
            return True