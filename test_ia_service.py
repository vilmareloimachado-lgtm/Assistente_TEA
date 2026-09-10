import unittest
from datetime import date

from services.ia_service import IaService


class UsuarioFake:
    def __init__(self, data_nascimento=None, estilo_instrucao="direto", nivel_suporte="Leve"):
        self.data_nascimento = data_nascimento
        self.estilo_instrucao = estilo_instrucao
        self.nivel_suporte = nivel_suporte


class RespostaFake:
    def __init__(self, text):
        self.text = text


class GeminiClientFake:
    """Substitui o client do Gemini para capturar o que foi enviado, sem chamar a API de verdade."""

    def __init__(self, texto_resposta="Passo 1\nPasso 2\nPasso 3"):
        self.texto_resposta = texto_resposta
        self.ultima_system_instruction = None

        class _Models:
            def generate_content(_self, model, contents, config):
                self.ultima_system_instruction = config.system_instruction
                return RespostaFake(self.texto_resposta)

        self.models = _Models()


class TestIaService(unittest.TestCase):
    def test_sem_client_configurado_gera_erro_no_chat(self):
        service = IaService(gemini_client=None)
        with self.assertRaises(ValueError):
            service.obter_resposta_chat("Como organizo meu dia?")

    def test_sem_client_configurado_gera_erro_ao_gerar_passos(self):
        service = IaService(gemini_client=None)
        with self.assertRaises(ValueError):
            service.gerar_passos_tarefa("Estudar matemática")

    def test_contexto_usuario_inclui_idade_estilo_e_suporte(self):
        client = GeminiClientFake()
        service = IaService(gemini_client=client)
        usuario = UsuarioFake(
            data_nascimento=date(2015, 1, 1),
            estilo_instrucao="detalhado",
            nivel_suporte="Moderado",
        )

        service.obter_resposta_chat("Oi", usuario)

        instrucao = client.ultima_system_instruction
        self.assertIn("anos", instrucao)
        self.assertIn("detalhado", instrucao)
        self.assertIn("Moderado", instrucao)

    def test_gerar_passos_limpa_marcadores_numericos(self):
        client = GeminiClientFake(texto_resposta="1. Abrir o caderno\n2. Ler o capítulo")
        service = IaService(gemini_client=client)

        passos = service.gerar_passos_tarefa("Estudar", UsuarioFake())

        self.assertEqual(passos, ["Abrir o caderno", "Ler o capítulo"])


if __name__ == "__main__":
    unittest.main()
