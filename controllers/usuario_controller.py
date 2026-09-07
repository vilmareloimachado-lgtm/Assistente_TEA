from services.usuario_service import UsuarioService 
 
 
class UsuarioController: 
    def __init__(self, service=None): 
        self.service = service or UsuarioService() 
 
    def listar_perfis(self): 
        usuarios = self.service.listar_usuarios() 
        return [usuario.nome for usuario in usuarios] 
    
    def buscar_perfil(self, nome):        # <- é este método aqui
        try:
            usuario = self.service.buscar_usuario(nome)
            return {
                "sucesso": True,
                "mensagem": f"Perfil {usuario.nome} encontrado.",
                "usuario_id": usuario.id,
                "usuario_nome": usuario.nome,
                "data_nascimento": self._formatar_data(usuario.data_nascimento)
            }
        except ValueError as erro:
            return {
                "sucesso": False,
                "mensagem": str(erro)
            }

    def excluir_perfil(self, nome):
        try:
            self.service.excluir_usuario(nome)
            return {
                "sucesso": True,
                "mensagem": f"Perfil {nome} excluído com sucesso."
            }
        except ValueError as erro:
            return {
                "sucesso": False,
                "mensagem": str(erro)
            }

    def _formatar_data(self, data):
        if not data:
            return ""
        return data.strftime("%d/%m/%Y")
    
    def criar_perfil(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login, criado_em=None):
        try: 
            usuario = self.service.criar_usuario( 
                nome, 
                estilo_instrucao,
                nivel_suporte,
                data_nascimento,
                senha_login,
                criado_em
             ) 
 
            return { 
                "sucesso": True, 
                "mensagem": f"Perfil {usuario.nome} criado.", 
                "usuario_id": usuario.id 
            } 
 
        except ValueError as erro: 
            return { 
                "sucesso": False, 
                "mensagem": str(erro) 
            } 