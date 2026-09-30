from services.usuario_service import UsuarioService


class UsuarioController:
    def __init__(self, service=None):
        self.service = service or UsuarioService()

    # ------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------
    def _falha(self, erro):
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }

    def _formatar_data(self, data):
        if not data:
            return ""
        return data.strftime("%d/%m/%Y")

    def _resumo_usuario(self, usuario):
        # Só o que pode sair da API: nunca a senha nem o hash do PIN.
        return {
            "usuario_id": usuario.id,
            "nome": usuario.nome,
            "tipo_usuario": usuario.tipo_usuario,
            "estilo_instrucao": usuario.estilo_instrucao,
            "nivel_suporte": usuario.nivel_suporte,
            "data_nascimento": self._formatar_data(usuario.data_nascimento),
            "email": usuario.email,
            "tem_pin": usuario.pin_hash is not None
        }

    # ------------------------------------------------------------
    # Login
    # ------------------------------------------------------------
    def login(self, email, senha):
        try:
            usuario = self.service.autenticar(email, senha)
            token = self.service.gerar_token(usuario)
            return {
                "sucesso": True,
                "mensagem": "Login realizado com sucesso.",
                "usuario_id": usuario.id,
                "nome": usuario.nome,
                "tipo_usuario": usuario.tipo_usuario,
                "token": token
            }
        except ValueError as erro:
            return self._falha(erro)

    def login_usuario_tea(self, cuidador_id, usuario_id, pin=None):
        try:
            usuario = self.service.entrar_no_perfil(cuidador_id, usuario_id, pin)
            token = self.service.gerar_token(usuario)
            return {
                "sucesso": True,
                "mensagem": "Login realizado com sucesso.",
                "usuario_id": usuario.id,
                "nome": usuario.nome,
                "tipo_usuario": usuario.tipo_usuario,
                "token": token
            }
        except ValueError as erro:
            return self._falha(erro)

    # ------------------------------------------------------------
    # Cadastro
    # ------------------------------------------------------------
    def cadastrar_cuidador(self, nome, email, senha, data_nascimento=None):
        try:
            usuario = self.service.criar_cuidador(nome, email, senha, data_nascimento)
            return {
                "sucesso": True,
                "mensagem": f"Conta de {usuario.nome} criada.",
                "usuario_id": usuario.id
            }
        except ValueError as erro:
            return self._falha(erro)

    def criar_usuario_tea(self, cuidador_id, nome, estilo_instrucao, nivel_suporte,
                          data_nascimento=None, pin=None):
        try:
            usuario = self.service.criar_usuario_tea(
                cuidador_id,
                nome,
                estilo_instrucao,
                nivel_suporte,
                data_nascimento,
                pin
            )
            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} criado.",
                "usuario_id": usuario.id
            }
        except ValueError as erro:
            return self._falha(erro)

    # ------------------------------------------------------------
    # Consultas por id
    # ------------------------------------------------------------
    def buscar_perfil_por_id(self, usuario_id):
        usuario = self.service.buscar_usuario_por_id(usuario_id)
        if usuario is None:
            return self._falha("Perfil não encontrado.")

        resultado = self._resumo_usuario(usuario)
        resultado["sucesso"] = True
        resultado["mensagem"] = f"Perfil {usuario.nome} encontrado."
        return resultado

    def listar_usuarios_do_cuidador(self, cuidador_id):
        usuarios = self.service.listar_usuarios_do_cuidador(cuidador_id)
        return {
            "sucesso": True,
            "mensagem": f"{len(usuarios)} perfil(is) encontrado(s).",
            "usuarios": [self._resumo_usuario(usuario) for usuario in usuarios]
        }

    def listar_cuidadores_do_usuario(self, cuidador_id, usuario_id):
        try:
            cuidadores = self.service.listar_cuidadores_do_usuario(cuidador_id, usuario_id)
            return {
                "sucesso": True,
                "mensagem": f"{len(cuidadores)} cuidador(es) encontrado(s).",
                "cuidadores": [self._resumo_usuario(c) for c in cuidadores]
            }
        except ValueError as erro:
            return self._falha(erro)

    # ------------------------------------------------------------
    # Vinculos
    # ------------------------------------------------------------
    def adicionar_cuidador(self, cuidador_id, usuario_id, email_novo_cuidador):
        try:
            self.service.adicionar_cuidador(cuidador_id, usuario_id, email_novo_cuidador)
            return {
                "sucesso": True,
                "mensagem": "Cuidador adicionado."
            }
        except ValueError as erro:
            return self._falha(erro)

    def remover_cuidador(self, cuidador_id, usuario_id, cuidador_removido_id):
        try:
            self.service.remover_cuidador(cuidador_id, usuario_id, cuidador_removido_id)
            return {
                "sucesso": True,
                "mensagem": "Cuidador removido."
            }
        except ValueError as erro:
            return self._falha(erro)

    def transferir_principal(self, cuidador_id, usuario_id, novo_principal_id):
        try:
            self.service.transferir_principal(cuidador_id, usuario_id, novo_principal_id)
            return {
                "sucesso": True,
                "mensagem": "Cuidador principal alterado."
            }
        except ValueError as erro:
            return self._falha(erro)

    # ------------------------------------------------------------
    # Alteracoes em perfis de usuario TEA
    # ------------------------------------------------------------
    def atualizar_usuario_tea(self, cuidador_id, usuario_id, nome=None,
                              estilo_instrucao=None, nivel_suporte=None,
                              data_nascimento=None):
        try:
            usuario = self.service.atualizar_usuario_tea(
                cuidador_id,
                usuario_id,
                nome=nome,
                estilo_instrucao=estilo_instrucao,
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento
            )
            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} atualizado.",
                "usuario_id": usuario.id
            }
        except ValueError as erro:
            return self._falha(erro)

    def definir_pin(self, cuidador_id, usuario_id, pin):
        try:
            self.service.definir_pin(cuidador_id, usuario_id, pin)
            return {
                "sucesso": True,
                "mensagem": "PIN definido."
            }
        except ValueError as erro:
            return self._falha(erro)

    def remover_pin(self, cuidador_id, usuario_id):
        try:
            self.service.remover_pin(cuidador_id, usuario_id)
            return {
                "sucesso": True,
                "mensagem": "PIN removido."
            }
        except ValueError as erro:
            return self._falha(erro)

    def excluir_usuario_tea(self, cuidador_id, usuario_id):
        try:
            excluido = self.service.excluir_usuario_tea(cuidador_id, usuario_id)
            if not excluido:
                return self._falha("Perfil não encontrado.")
            return {
                "sucesso": True,
                "mensagem": "Perfil excluído com sucesso."
            }
        except ValueError as erro:
            return self._falha(erro)

    def excluir_cuidador(self, cuidador_id, senha):
        try:
            excluido = self.service.excluir_cuidador(cuidador_id, senha)
            if not excluido:
                return self._falha("Cuidador não encontrado.")
            return {
                "sucesso": True,
                "mensagem": "Conta excluída com sucesso."
            }
        except ValueError as erro:
            return self._falha(erro)

    # ------------------------------------------------------------
    # Metodos antigos (menus do terminal e rotas atuais, por nome)
    # ------------------------------------------------------------
    def listar_perfis(self):
        usuarios = self.service.listar_usuarios()
        return [usuario.nome for usuario in usuarios]

    def buscar_perfil(self, nome):
        try:
            usuario = self.service.buscar_usuario(nome)
            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} encontrado.",
                "usuario_id": usuario.id,
                "usuario_nome": usuario.nome,
                "data_nascimento": self._formatar_data(usuario.data_nascimento),
                "email": usuario.email,
                "tipo_usuario": usuario.tipo_usuario
            }
        except ValueError as erro:
            return self._falha(erro)

    def atualizar_perfil(self, nome, novo_nome=None, estilo_instrucao=None,
                         nivel_suporte=None, data_nascimento=None, senha_login=None,
                         email=None, tipo_usuario=None):
        try:
            usuario = self.service.atualizar_usuario(
                nome,
                novo_nome=novo_nome,
                estilo_instrucao=estilo_instrucao,
                nivel_suporte=nivel_suporte,
                data_nascimento=data_nascimento,
                senha_login=senha_login,
                email=email,
                tipo_usuario=tipo_usuario
            )
            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} atualizado.",
                "usuario_id": usuario.id
            }
        except ValueError as erro:
            return self._falha(erro)

    def excluir_perfil(self, nome):
        try:
            self.service.excluir_usuario(nome)
            return {
                "sucesso": True,
                "mensagem": f"Perfil {nome} excluído com sucesso."
            }
        except ValueError as erro:
            return self._falha(erro)

    def criar_perfil(self, nome, estilo_instrucao, nivel_suporte, data_nascimento,
                     senha_login, email, tipo_usuario="cuidador", criado_em=None):
        try:
            usuario = self.service.criar_usuario(
                nome,
                estilo_instrucao,
                nivel_suporte,
                data_nascimento,
                senha_login,
                email,
                tipo_usuario,
                criado_em
            )

            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} criado.",
                "usuario_id": usuario.id
            }

        except ValueError as erro:
            return self._falha(erro)
