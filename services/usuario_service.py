import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config.auth import ALGORITMO, horas_de_expiracao, obter_chave_secreta
from repositories.usuario_repository import UsuarioRepository


ESTILOS = {"direto", "detalhado"}
NIVEIS_SUPORTE = {"Leve", "Moderado", "Severo"}
TIPOS_USUARIO = {"cuidador", "usuario_tea"}


class UsuarioService:
    def __init__(self, repository=None):
        self.repository = repository or UsuarioRepository()

    # ------------------------------------------------------------
    # Validacoes
    # ------------------------------------------------------------
    def validar_nome(self, nome):
        nome = nome.strip()
        return bool(re.fullmatch(r"[A-Za-zÀ-ÿ\s]+", nome))

    def _validar_nome_completo(self, nome):
        # Valida e devolve o nome ja sem espacos nas pontas.
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("O nome não pode ficar vazio.")
        if not self.validar_nome(nome):
            raise ValueError("Nome inválido! Digite apenas letras e espaços.")
        if len(nome) < 3:
            raise ValueError("O nome precisa ter pelo menos 3 caracteres.")
        return nome

    def validar_data_nascimento(self, data_nascimento):
        if not data_nascimento:
            return None
        try:
            return datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError(
                "Data de nascimento inválida. Utilize o formato DD/MM/AAAA."
            )

    def _exigir_data_nascimento(self, data_nascimento):
        # O banco exige a data; aqui devolvemos uma mensagem clara em vez de um erro técnico.
        data = self.validar_data_nascimento(data_nascimento)
        if data is None:
            raise ValueError("Informe a data de nascimento (DD/MM/AAAA).")
        return data

    def validar_senha(self, senha):
        if not senha or len(senha) < 6:
            raise ValueError("A senha precisa ter pelo menos 6 caracteres.")
        # O bcrypt só usa os primeiros 72 bytes; melhor recusar do que ignorar o resto.
        if len(senha.encode("utf-8")) > 72:
            raise ValueError("A senha pode ter no máximo 72 caracteres.")

    def validar_pin(self, pin):
        if not pin or not re.fullmatch(r"\d{4,6}", pin):
            raise ValueError("O PIN precisa ter de 4 a 6 números.")

    def validar_email(self, email):
        if not email or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Email inválido.")

    def _validar_estilo(self, estilo_instrucao):
        if estilo_instrucao not in ESTILOS:
            raise ValueError("O estilo deve ser 'direto' ou 'detalhado'.")

    def _validar_nivel(self, nivel_suporte):
        if nivel_suporte not in NIVEIS_SUPORTE:
            raise ValueError(
                "O nível de suporte deve ser 'Leve', 'Moderado' ou 'Severo'."
            )

    # ------------------------------------------------------------
    # Hash de senha e PIN (bcrypt)
    # ------------------------------------------------------------
    def _preparar_para_bcrypt(self, texto):
        # O bcrypt só usa os primeiros 72 bytes. Cortamos aqui para o comportamento
        # ser o mesmo em qualquer versão da biblioteca (as mais novas dão erro se passar disso).
        return texto.encode("utf-8")[:72]

    def _gerar_hash(self, texto):
        return bcrypt.hashpw(self._preparar_para_bcrypt(texto), bcrypt.gensalt()).decode("utf-8")

    def _e_hash_legado(self, hash_salvo):
        # Hash antigo do sistema: SHA-256 em hexadecimal (64 caracteres).
        return bool(hash_salvo) and re.fullmatch(r"[0-9a-f]{64}", hash_salvo) is not None

    def _conferir_hash(self, texto, hash_salvo):
        if not texto or not hash_salvo:
            return False

        if self._e_hash_legado(hash_salvo):
            calculado = hashlib.sha256(texto.encode("utf-8")).hexdigest()
            return hmac.compare_digest(calculado, hash_salvo)

        try:
            return bcrypt.checkpw(self._preparar_para_bcrypt(texto), hash_salvo.encode("utf-8"))
        except ValueError:
            return False

    def criptografar_senha(self, senha):
        # Mantido com o mesmo nome para não quebrar quem já chama, mas agora usa bcrypt.
        return self._gerar_hash(senha)

    def verificar_senha(self, senha, hash_salvo):
        return self._conferir_hash(senha, hash_salvo)

    def _gastar_tempo_de_hash(self, texto):
        # Quando o email não existe, ainda fazemos uma conta de bcrypt para a
        # resposta demorar parecido e não revelar quais emails estão cadastrados.
        self._gerar_hash(texto or "x")

    # ------------------------------------------------------------
    # Consultas simples
    # ------------------------------------------------------------
    def listar_usuarios(self):
        return self.repository.listar()

    def buscar_usuario(self, nome):
        nome = nome.strip()
        usuario = self.repository.buscar_por_nome(nome)
        if usuario is None:
            raise ValueError("Perfil não encontrado.")
        return usuario

    def buscar_usuario_por_id(self, usuario_id):
        return self.repository.buscar_por_id(usuario_id)

    def listar_usuarios_do_cuidador(self, cuidador_id):
        return self.repository.listar_usuarios_do_cuidador(cuidador_id)

    def listar_cuidadores_do_usuario(self, cuidador_id, usuario_id):
        self._exigir_vinculo(cuidador_id, usuario_id)
        return self.repository.listar_cuidadores_do_usuario(usuario_id)

    # ------------------------------------------------------------
    # Login e token
    # ------------------------------------------------------------
    def autenticar(self, email, senha):
        # Login do cuidador: email + senha.
        email = (email or "").strip()
        usuario = self.repository.buscar_por_email(email) if email else None

        if usuario is None or usuario.tipo_usuario != "cuidador":
            self._gastar_tempo_de_hash(senha)
            raise ValueError("Email ou senha inválidos.")

        if not self._conferir_hash(senha, usuario.senha_login):
            raise ValueError("Email ou senha inválidos.")

        # Conta antiga (SHA-256): troca para bcrypt no primeiro login bem-sucedido.
        if self._e_hash_legado(usuario.senha_login):
            self.repository.atualizar_por_id(
                usuario.id, senha_login=self._gerar_hash(senha)
            )

        return usuario

    def entrar_no_perfil(self, cuidador_id, usuario_id, pin=None):
        # O cuidador logado escolhe o perfil de um usuario TEA que ELE acompanha.
        # Use este método nas rotas: ele confere o vínculo antes de olhar o PIN.
        self._exigir_vinculo(cuidador_id, usuario_id)
        return self.autenticar_usuario_tea(usuario_id, pin)

    def autenticar_usuario_tea(self, usuario_id, pin=None):
        # Confere o perfil usuario_tea e o PIN (sem PIN cadastrado, entra sem PIN).
        # Não confere o vínculo com o cuidador: por isso as rotas devem usar entrar_no_perfil.
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None or usuario.tipo_usuario != "usuario_tea":
            self._gastar_tempo_de_hash(pin)
            raise ValueError("Perfil ou PIN inválidos.")

        if usuario.pin_hash is None:
            return usuario

        if not self._conferir_hash(pin, usuario.pin_hash):
            raise ValueError("Perfil ou PIN inválidos.")

        return usuario

    def gerar_token(self, usuario):
        horas = horas_de_expiracao(usuario.tipo_usuario)
        expira_em = datetime.now(timezone.utc) + timedelta(hours=horas)

        payload = {
            "usuario_id": usuario.id,
            "tipo_usuario": usuario.tipo_usuario,
            "exp": expira_em
        }

        return jwt.encode(payload, obter_chave_secreta(), algorithm=ALGORITMO)

    # ------------------------------------------------------------
    # Cadastro
    # ------------------------------------------------------------
    def criar_cuidador(self, nome, email, senha, data_nascimento=None):
        # "Criar conta": não exige login, porque quem cadastra ainda não tem conta.
        nome = self._validar_nome_completo(nome)

        email = (email or "").strip()
        self.validar_email(email)
        if self.repository.buscar_por_email(email) is not None:
            raise ValueError("Já existe um usuário com esse email.")

        self.validar_senha(senha)
        data = self._exigir_data_nascimento(data_nascimento)

        return self.repository.criar(
            nome,
            "direto",
            "Leve",
            data,
            self._gerar_hash(senha),
            email,
            "cuidador"
        )

    def criar_usuario_tea(self, cuidador_id, nome, estilo_instrucao, nivel_suporte,
                          data_nascimento=None, pin=None):
        cuidador = self.repository.buscar_por_id(cuidador_id)
        if cuidador is None or cuidador.tipo_usuario != "cuidador":
            raise ValueError("Cuidador não encontrado.")

        nome = self._validar_nome_completo(nome)
        self._validar_estilo(estilo_instrucao)
        self._validar_nivel(nivel_suporte)

        # O nome só não pode repetir entre os usuarios DESTE cuidador.
        if self.repository.nome_existe_para_cuidador(cuidador_id, nome):
            raise ValueError("Você já tem um perfil com esse nome.")

        pin_hash = None
        if pin:
            self.validar_pin(pin)
            pin_hash = self._gerar_hash(pin)

        data = self._exigir_data_nascimento(data_nascimento)

        return self.repository.criar_usuario_tea_com_vinculo(
            cuidador_id,
            nome,
            estilo_instrucao,
            nivel_suporte,
            data,
            pin_hash
        )

    # ------------------------------------------------------------
    # Vinculos entre cuidadores e usuarios TEA
    # ------------------------------------------------------------
    def _exigir_vinculo(self, cuidador_id, usuario_id):
        vinculo = self.repository.buscar_vinculo(cuidador_id, usuario_id)
        if vinculo is None:
            raise ValueError("Você não acompanha esse perfil.")
        return vinculo

    def _exigir_principal(self, cuidador_id, usuario_id):
        vinculo = self._exigir_vinculo(cuidador_id, usuario_id)
        if not vinculo.principal:
            raise ValueError("Apenas o cuidador principal pode fazer isso.")
        return vinculo

    def adicionar_cuidador(self, cuidador_id, usuario_id, email_novo_cuidador):
        self._exigir_principal(cuidador_id, usuario_id)

        email = (email_novo_cuidador or "").strip()
        novo = self.repository.buscar_por_email(email) if email else None
        if novo is None or novo.tipo_usuario != "cuidador":
            raise ValueError("Cuidador não encontrado.")

        if self.repository.buscar_vinculo(novo.id, usuario_id) is not None:
            raise ValueError("Esse cuidador já acompanha esse perfil.")

        return self.repository.criar_vinculo(novo.id, usuario_id, principal=False)

    def remover_cuidador(self, cuidador_id, usuario_id, cuidador_removido_id):
        self._exigir_principal(cuidador_id, usuario_id)

        if cuidador_removido_id == cuidador_id:
            raise ValueError(
                "O cuidador principal não pode se remover. "
                "Passe o papel de principal para outro cuidador antes."
            )

        if not self.repository.remover_vinculo(cuidador_removido_id, usuario_id):
            raise ValueError("Esse cuidador não acompanha esse perfil.")
        return True

    def transferir_principal(self, cuidador_id, usuario_id, novo_principal_id):
        self._exigir_principal(cuidador_id, usuario_id)

        if self.repository.buscar_vinculo(novo_principal_id, usuario_id) is None:
            raise ValueError("Esse cuidador não acompanha esse perfil.")

        return self.repository.definir_principal(novo_principal_id, usuario_id)

    # ------------------------------------------------------------
    # Alteracoes em perfis de usuario TEA
    # ------------------------------------------------------------
    def atualizar_usuario_tea(self, cuidador_id, usuario_id, nome=None,
                              estilo_instrucao=None, nivel_suporte=None,
                              data_nascimento=None):
        self._exigir_vinculo(cuidador_id, usuario_id)

        if nome is not None:
            nome = self._validar_nome_completo(nome)
            if self.repository.nome_existe_para_cuidador(
                cuidador_id, nome, ignorar_usuario_id=usuario_id
            ):
                raise ValueError("Você já tem um perfil com esse nome.")

        if estilo_instrucao is not None:
            self._validar_estilo(estilo_instrucao)
        if nivel_suporte is not None:
            self._validar_nivel(nivel_suporte)
        if data_nascimento is not None:
            data_nascimento = self.validar_data_nascimento(data_nascimento)

        return self.repository.atualizar_por_id(
            usuario_id,
            nome=nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento
        )

    def definir_pin(self, cuidador_id, usuario_id, pin):
        self._exigir_vinculo(cuidador_id, usuario_id)
        self.validar_pin(pin)
        return self.repository.definir_pin_hash(usuario_id, self._gerar_hash(pin))

    def remover_pin(self, cuidador_id, usuario_id):
        self._exigir_vinculo(cuidador_id, usuario_id)
        return self.repository.definir_pin_hash(usuario_id, None)

    def excluir_usuario_tea(self, cuidador_id, usuario_id):
        # Só o principal apaga o perfil, porque isso apaga também tarefas e passos.
        self._exigir_principal(cuidador_id, usuario_id)
        return self.repository.excluir_por_id(usuario_id)

    def excluir_cuidador(self, cuidador_id, senha):
        # Exclusão da própria conta: pede a senha e aplica a exclusão em cadeia.
        cuidador = self.repository.buscar_por_id(cuidador_id)
        if cuidador is None or cuidador.tipo_usuario != "cuidador":
            raise ValueError("Cuidador não encontrado.")

        if not self._conferir_hash(senha, cuidador.senha_login):
            raise ValueError("Senha incorreta.")

        return self.repository.excluir_cuidador_em_cadeia(cuidador_id)

    # ------------------------------------------------------------
    # Metodos antigos (usados pelos menus do terminal e pelas rotas atuais)
    # Continuam por nome. As rotas novas devem usar os métodos por id acima.
    # ------------------------------------------------------------
    def atualizar_usuario(self, nome, novo_nome=None, estilo_instrucao=None,
                          nivel_suporte=None, data_nascimento=None, senha_login=None,
                          email=None, tipo_usuario=None):
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

        if estilo_instrucao is not None:
            self._validar_estilo(estilo_instrucao)

        if nivel_suporte is not None:
            self._validar_nivel(nivel_suporte)

        if senha_login is not None:
            self.validar_senha(senha_login)
            senha_login = self._gerar_hash(senha_login)

        if data_nascimento is not None:
            data_nascimento = self.validar_data_nascimento(data_nascimento)

        if email is not None:
            self.validar_email(email)
            usuario_com_email = self.repository.buscar_por_email(email)
            if usuario_com_email is not None and usuario_com_email.id != usuario_atual.id:
                raise ValueError("Já existe um usuário com esse email.")

        if tipo_usuario is not None and tipo_usuario not in TIPOS_USUARIO:
            raise ValueError("O tipo de usuário deve ser 'cuidador' ou 'usuario_tea'.")

        return self.repository.atualizar_por_nome(
            nome,
            novo_nome=novo_nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento,
            senha_login=senha_login,
            email=email,
            tipo_usuario=tipo_usuario
        )

    def excluir_usuario(self, nome):
        nome = nome.strip()
        excluido = self.repository.excluir_por_nome(nome)
        if not excluido:
            raise ValueError("Perfil não encontrado.")
        return True

    def criar_usuario(self, nome, estilo_instrucao, nivel_suporte, data_nascimento,
                      senha_login, email, tipo_usuario="cuidador", criado_em=None):
        nome = self._validar_nome_completo(nome)
        self._validar_estilo(estilo_instrucao)
        self._validar_nivel(nivel_suporte)

        if self.repository.buscar_por_nome(nome) is not None:
            raise ValueError("Já existe um perfil com esse nome.")

        self.validar_email(email)
        if self.repository.buscar_por_email(email) is not None:
            raise ValueError("Já existe um usuário com esse email.")

        if tipo_usuario not in TIPOS_USUARIO:
            raise ValueError("O tipo de usuário deve ser 'cuidador' ou 'usuario_tea'.")

        self.validar_senha(senha_login)
        senha_login = self._gerar_hash(senha_login)
        data_nascimento = self.validar_data_nascimento(data_nascimento)

        return self.repository.criar(
            nome,
            estilo_instrucao,
            nivel_suporte,
            data_nascimento,
            senha_login,
            email,
            tipo_usuario,
            criado_em
        )