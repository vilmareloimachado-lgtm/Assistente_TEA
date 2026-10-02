import unittest
from types import SimpleNamespace

from services.usuario_service import UsuarioService


class UsuarioRepositoryFake:
    def __init__(self):
        self.usuarios = {}
        self.vinculos = {}
        self.proximo_id = 1

    # ------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------
    def _novo_id(self):
        novo_id = self.proximo_id
        self.proximo_id += 1
        return novo_id

    def _criar_usuario(
        self,
        nome,
        estilo_instrucao,
        nivel_suporte,
        data_nascimento,
        senha_login,
        email,
        tipo_usuario,
        pin_hash=None
    ):
        usuario_id = self._novo_id()

        usuario = SimpleNamespace(
            id=usuario_id,
            nome=nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento,
            senha_login=senha_login,
            email=email,
            tipo_usuario=tipo_usuario,
            pin_hash=pin_hash
        )

        self.usuarios[usuario_id] = usuario
        return usuario

    # ------------------------------------------------------------
    # Buscas
    # ------------------------------------------------------------
    def buscar_por_id(self, usuario_id):
        return self.usuarios.get(usuario_id)

    def buscar_por_email(self, email):
        if email is None:
            return None

        for usuario in self.usuarios.values():
            if usuario.email == email:
                return usuario

        return None

    def buscar_por_nome(self, nome):
        for usuario in self.usuarios.values():
            if usuario.nome == nome:
                return usuario

        return None

    # ------------------------------------------------------------
    # Cuidador
    # ------------------------------------------------------------
    
    def criar(
        self,
        nome,
        estilo_instrucao,
        nivel_suporte,
        data_nascimento,
        senha_login,
        email,
        tipo_usuario,
        criado_em=None,
        pin_hash=None
    ):
        return self._criar_usuario(
            nome=nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento,
            senha_login=senha_login,
            email=email,
            tipo_usuario=tipo_usuario,
            pin_hash=pin_hash
        )
    
    
    
    def criar_cuidador(
        self,
        nome,
        data_nascimento,
        senha_login,
        email,
        criado_em=None
    ):
        return self._criar_usuario(
            nome=nome,
            estilo_instrucao="direto",
            nivel_suporte="Leve",
            data_nascimento=data_nascimento,
            senha_login=senha_login,
            email=email,
            tipo_usuario="cuidador"
        )

    # ------------------------------------------------------------
    # Usuário TEA
    # ------------------------------------------------------------
    def criar_usuario_tea_com_vinculo(
        self,
        cuidador_id,
        nome,
        estilo_instrucao,
        nivel_suporte,
        data_nascimento,
        pin_hash=None,
        criado_em=None
    ):
        usuario = self._criar_usuario(
            nome=nome,
            estilo_instrucao=estilo_instrucao,
            nivel_suporte=nivel_suporte,
            data_nascimento=data_nascimento,
            senha_login=None,
            email=None,
            tipo_usuario="usuario_tea",
            pin_hash=pin_hash
        )

        self.criar_vinculo(
            cuidador_id,
            usuario.id,
            principal=True
        )

        return usuario

    def nome_existe_para_cuidador(
        self,
        cuidador_id,
        nome,
        ignorar_usuario_id=None
    ):
        for (id_cuidador, id_usuario), vinculo in self.vinculos.items():
            if id_cuidador != cuidador_id:
                continue

            if ignorar_usuario_id == id_usuario:
                continue

            usuario = self.buscar_por_id(id_usuario)

            if usuario and usuario.nome == nome:
                return True

        return False

    # ------------------------------------------------------------
    # Vínculos
    # ------------------------------------------------------------
    def buscar_vinculo(self, cuidador_id, usuario_id):
        return self.vinculos.get(
            (cuidador_id, usuario_id)
        )

    def criar_vinculo(
        self,
        cuidador_id,
        usuario_id,
        principal=False
    ):
        vinculo = SimpleNamespace(
            cuidador_id=cuidador_id,
            usuario_id=usuario_id,
            principal=principal
        )

        self.vinculos[(cuidador_id, usuario_id)] = vinculo
        return vinculo

    def remover_vinculo(self, cuidador_id, usuario_id):
        chave = (cuidador_id, usuario_id)

        if chave not in self.vinculos:
            return False

        del self.vinculos[chave]
        return True

    # ------------------------------------------------------------
    # PIN
    # ------------------------------------------------------------
    def definir_pin_hash(self, usuario_id, pin_hash):
        usuario = self.buscar_por_id(usuario_id)

        if usuario is None:
            return False

        usuario.pin_hash = pin_hash
        return True

    # ------------------------------------------------------------
    # Exclusão
    # ------------------------------------------------------------
    def excluir_por_id(self, usuario_id):
        if usuario_id not in self.usuarios:
            return False

        del self.usuarios[usuario_id]

        chaves_remover = [
            chave
            for chave in self.vinculos
            if chave[1] == usuario_id
        ]

        for chave in chaves_remover:
            del self.vinculos[chave]

        return True


class TestUsuarioService(unittest.TestCase):

    def setUp(self):
        self.repository = UsuarioRepositoryFake()
        self.service = UsuarioService(
            repository=self.repository
        )

    # ------------------------------------------------------------
    # Cuidador
    # ------------------------------------------------------------
    def test_cria_cuidador_valido(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        self.assertIsNotNone(cuidador.id)
        self.assertEqual(
            cuidador.tipo_usuario,
            "cuidador"
        )
        self.assertEqual(
            cuidador.email,
            "maria@email.com"
        )

    def test_nao_aceita_email_duplicado(self):
        self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        with self.assertRaises(ValueError):
            self.service.criar_cuidador(
                "Maria Souza",
                "maria@email.com",
                "654321",
                "15/08/1985"
            )

    def test_nao_aceita_senha_curta(self):
        with self.assertRaises(ValueError):
            self.service.criar_cuidador(
                "Maria Silva",
                "maria@email.com",
                "123",
                "10/05/1980"
            )

    # ------------------------------------------------------------
    # Usuário TEA
    # ------------------------------------------------------------
    def test_cria_usuario_tea_com_vinculo_principal(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        self.assertEqual(
            usuario.tipo_usuario,
            "usuario_tea"
        )

        vinculo = self.repository.buscar_vinculo(
            cuidador.id,
            usuario.id
        )

        self.assertIsNotNone(vinculo)
        self.assertTrue(vinculo.principal)

    def test_nao_aceita_nome_duplicado_para_mesmo_cuidador(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        with self.assertRaises(ValueError):
            self.service.criar_usuario_tea(
                cuidador.id,
                "Gabriel Silva",
                "detalhado",
                "Moderado",
                "20/04/2011"
            )

    def test_permite_mesmo_nome_para_cuidadores_diferentes(self):
        cuidador_1 = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        cuidador_2 = self.service.criar_cuidador(
            "Carlos Souza",
            "carlos@email.com",
            "654321",
            "20/06/1978"
        )

        usuario_1 = self.service.criar_usuario_tea(
            cuidador_1.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        usuario_2 = self.service.criar_usuario_tea(
            cuidador_2.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        self.assertNotEqual(
            usuario_1.id,
            usuario_2.id
        )

    # ------------------------------------------------------------
    # Segurança do vínculo
    # ------------------------------------------------------------
    def test_cuidador_sem_vinculo_nao_entra_no_perfil(self):
        cuidador_1 = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        cuidador_2 = self.service.criar_cuidador(
            "Carlos Souza",
            "carlos@email.com",
            "654321",
            "20/06/1978"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador_1.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        with self.assertRaises(ValueError):
            self.service.entrar_no_perfil(
                cuidador_2.id,
                usuario.id
            )

    def test_cuidador_com_vinculo_entra_no_perfil(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        resultado = self.service.entrar_no_perfil(
            cuidador.id,
            usuario.id
        )

        self.assertEqual(
            resultado.id,
            usuario.id
        )

    # ------------------------------------------------------------
    # PIN
    # ------------------------------------------------------------
    def test_pin_correto_permite_entrada(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010",
            "1234"
        )

        resultado = self.service.entrar_no_perfil(
            cuidador.id,
            usuario.id,
            "1234"
        )

        self.assertEqual(
            resultado.id,
            usuario.id
        )

    def test_pin_incorreto_bloqueia_entrada(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010",
            "1234"
        )

        with self.assertRaises(ValueError):
            self.service.entrar_no_perfil(
                cuidador.id,
                usuario.id,
                "9999"
            )

    # ------------------------------------------------------------
    # Exclusão
    # ------------------------------------------------------------
    def test_cuidador_principal_pode_excluir_usuario_tea(self):
        cuidador = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        resultado = self.service.excluir_usuario_tea(
            cuidador.id,
            usuario.id
        )

        self.assertTrue(resultado)

        self.assertIsNone(
            self.repository.buscar_por_id(usuario.id)
        )

    def test_cuidador_sem_vinculo_nao_pode_excluir_usuario_tea(self):
        cuidador_1 = self.service.criar_cuidador(
            "Maria Silva",
            "maria@email.com",
            "123456",
            "10/05/1980"
        )

        cuidador_2 = self.service.criar_cuidador(
            "Carlos Souza",
            "carlos@email.com",
            "654321",
            "20/06/1978"
        )

        usuario = self.service.criar_usuario_tea(
            cuidador_1.id,
            "Gabriel Silva",
            "direto",
            "Leve",
            "15/03/2010"
        )

        with self.assertRaises(ValueError):
            self.service.excluir_usuario_tea(
                cuidador_2.id,
                usuario.id
            )


if __name__ == "__main__":
    unittest.main()