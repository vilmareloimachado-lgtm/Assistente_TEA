import hashlib
import re
from datetime import datetime
from repositories.usuario_repository import UsuarioRepository 
 
class UsuarioService: 
    def __init__(self, repository=None): 
        self.repository = repository or UsuarioRepository() 
 
    def listar_usuarios(self): 
        return self.repository.listar()

    def validar_nome(self, nome):
        nome = nome.strip()
        return bool(re.fullmatch(r"[A-Za-zÀ-ÿ\s]+", nome))

    def validar_data_nascimento(self, data_nascimento):
        if not data_nascimento:
            return None
        try:
            return datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError(
                "Data de nascimento inválida. Utilize o formato DD/MM/AAAA."
        )

    def validar_senha(self, senha):
        if not senha or len(senha) < 6:
            raise ValueError("A senha precisa ter pelo menos 6 caracteres.")

    def criptografar_senha(self, senha):
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()

    def buscar_usuario(self, nome):
        nome = nome.strip()
        usuario = self.repository.buscar_por_nome(nome)
        if usuario is None:
            raise ValueError("Perfil não encontrado.")
        return usuario

    def buscar_usuario_por_id(self, usuario_id):
        return self.repository.buscar_por_id(usuario_id)

    def atualizar_usuario(self, nome, novo_nome=None, estilo_instrucao=None,
                           nivel_suporte=None, data_nascimento=None, senha_login=None):
        nome = nome.strip()

        usuario_atual = self.repository.buscar_por_nome(nome)
        if usuario_atual is None:
            raise ValueError("Perfil não encontrado.")

        if novo_nome is not None:
            novo_nome = novo_nome.strip()
            if not self.validar_nome(novo_nome):
                raise ValueError("Nome inválido! Digite apenas letras e espaços.")
            if len(novo_nome) < 3:
                raise ValueError("O nome precisa ter pelo menos 3 caracteres.")
            if novo_nome != nome and self.repository.buscar_por_nome(novo_nome) is not None:
                raise ValueError("Já existe um perfil com esse nome.")

        if estilo_instrucao is not None and estilo_instrucao not in {"direto", "detalhado"}:
            raise ValueError("O estilo deve ser 'direto' ou 'detalhado'.")

        if nivel_suporte is not None and nivel_suporte not in {"Leve", "Moderado", "Severo"}:
            raise ValueError("O nível de suporte deve ser 'Leve', 'Moderado' ou 'Severo'.")

        if senha_login is not None:
            self.validar_senha(senha_login)
            senha_login = self.criptografar_senha(senha_login)

        if data_nascimento is not None:
            data_nascimento = self.validar_data_nascimento(data_nascimento)

        return self.repository.atualizar_por_nome(
            nome,
            novo_nome=novo_nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento,
            senha_login=senha_login
        )

    def excluir_usuario(self, nome):
        nome = nome.strip()
        excluido = self.repository.excluir_por_nome(nome)
        if not excluido:
            raise ValueError("Perfil não encontrado.")
        return True

    def criar_usuario(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login, criado_em=None):
        nome = nome.strip()

        if not self.validar_nome(nome):
            raise ValueError("Nome inválido! Digite apenas letras e espaços.")

        if not nome: 
            raise ValueError("O nome não pode ficar vazio.") 

        if len(nome) < 3: 
            raise ValueError( 
                "O nome precisa ter pelo menos 3 caracteres." 
            )

        if estilo_instrucao not in {"direto", "detalhado"}: 
            raise ValueError( 
                "O estilo deve ser 'direto' ou 'detalhado'." 
            )

        if nivel_suporte not in {"Leve", "Moderado", "Severo"}:
            raise ValueError(
                "O nível de suporte deve ser 'Leve', 'Moderado' ou 'Severo'."
            )

        existente = self.repository.buscar_por_nome(nome) 
        if existente is not None: 
            raise ValueError("Já existe um perfil com esse nome.") 

        self.validar_senha(senha_login)
        senha_login = self.criptografar_senha(senha_login)

        data_nascimento = self.validar_data_nascimento(data_nascimento)
        return self.repository.criar( 
            nome, 
            estilo_instrucao,
            nivel_suporte,
            data_nascimento,
            senha_login,
            criado_em
        )