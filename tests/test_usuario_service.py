import unittest 
 
from services.usuario_service import UsuarioService 
 
 
class UsuarioFake: 
    def __init__(self, nome, estilo_instrucao="direto", nivel_suporte="Leve", data_nascimento="1980/01/01", senha_login="123456", criado_em="2026/09/02"): 
        self.id = 1 
        self.nome = nome 
        self.estilo_instrucao = estilo_instrucao 
        self.nivel_suporte = nivel_suporte
        self.data_nascimento = data_nascimento
        self.senha_login = senha_login
        self.criado_em = criado_em  
 
class UsuarioRepositoryFake: 
    def __init__(self): 
        self.usuarios = {} 
 
    def listar(self): 
        return list(self.usuarios.values()) 
 
    def buscar_por_nome(self, nome): 
        return self.usuarios.get(nome) 
 
    def criar(self, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login, criado_em): 
        usuario = UsuarioFake( 
            nome, 
            estilo_instrucao, 
            nivel_suporte,
            data_nascimento,
            senha_login,
            criado_em
    
        ) 
        self.usuarios[nome] = usuario 
        return usuario 
 
 
class TestUsuarioService(unittest.TestCase): 
    def setUp(self): 
        self.repo = UsuarioRepositoryFake() 
        self.service = UsuarioService(self.repo) 
 
    def test_cria_usuario_valido(self): 
        usuario = self.service.criar_usuario( 
            "Ana", 
            "direto",
            "Moderado",
            "01/01/1990",
            "123456",
            "02/09/2026" 
 ) 
        self.assertEqual(usuario.nome, "Ana") 
 
    def test_nao_aceita_nome_vazio(self): 
        with self.assertRaises(ValueError): 
            self.service.criar_usuario( 
                "   ", 
                "direto",
                "Moderado",
                "01/01/1990",
                "123456",
                "02/09/2026" 
 
            ) 
 
    def test_nao_aceita_usuario_duplicado(self): 
        self.service.criar_usuario( 
            "Leo", 
            "direto",
            "Moderado",
            "01/01/1990",
            "123456",
            "02/09/2026" 

        ) 
 
        with self.assertRaises(ValueError): 
            self.service.criar_usuario( 
                "Leo", 
                "direto",
                "Moderado",
                "01/01/1990",
                "123456",
                "02/09/2026" 
            ) 
 
    def test_nao_aceita_estilo_invalido(self): 
        with self.assertRaises(ValueError): 
            self.service.criar_usuario( 
                "Bia", 
                "gigante",
                "Moderado",
                "01/01/1990",
                "123456",
                "02/09/2026" 
 
            ) 
    def test_nao_aceita_nome_muito_curto(self): 
        with self.assertRaises(ValueError): 
            self.service.criar_usuario( 
                "Al", 
                "direto",
                "Moderado",
                "01/01/1990",
                "123456",
                "02/09/2026" 
            )
 
if __name__ == "__main__": 
    unittest.main() 