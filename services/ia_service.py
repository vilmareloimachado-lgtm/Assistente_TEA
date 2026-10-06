import os
import re
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ------------------------------------------------------------
# Carrega as variáveis do arquivo .env
# ------------------------------------------------------------
load_dotenv()


# ------------------------------------------------------------
# Configuração do Gemini
# ------------------------------------------------------------
API_KEY = os.environ.get("GEMINI_API_KEY")

_client_padrao = (
    genai.Client(api_key=API_KEY)
    if API_KEY
    else None
)


# Modelo utilizado para respostas rápidas de texto
MODELO_GEMINI = "gemini-2.5-flash"


class IaService:
    """Camada de serviço para as chamadas à IA (Gemini).

    Não tem repository/model porque não persiste nada no banco.
    Quem guarda os dados, como passos aceitos, é o TarefaService
    através do IaController.
    """

    def __init__(self, gemini_client=None):
        self.client = (
            gemini_client
            if gemini_client is not None
            else _client_padrao
        )

        # Guarda uma sessão de chat por usuário para manter
        # a memória da conversa entre uma pergunta e outra.
        # chave = usuario.id
        self._chats = {}

    # --------------------------------------------------------
    # Montagem de contexto do usuário
    # --------------------------------------------------------
    def _calcular_idade(self, data_nascimento):
        if not data_nascimento:
            return None

        hoje = date.today()

        nascimento = (
            data_nascimento.date()
            if hasattr(data_nascimento, "date")
            else data_nascimento
        )

        idade = hoje.year - nascimento.year

        if (hoje.month, hoje.day) < (
            nascimento.month,
            nascimento.day
        ):
            idade -= 1

        return idade

    def _montar_contexto_usuario(self, usuario):
        """Monta informações usadas pela IA para personalizar
        a resposta de acordo com o usuário.
        """

        if usuario is None:
            return (
                "Nenhuma informação adicional "
                "do usuário disponível."
            )

        idade = self._calcular_idade(
            getattr(
                usuario,
                "data_nascimento",
                None
            )
        )

        linhas = [
            "Informações do usuário, "
            "para adaptar a resposta:"
        ]

        if idade is not None:
            linhas.append(
                f"- Idade: {idade} anos"
            )

        if getattr(
            usuario,
            "estilo_instrucao",
            None
        ):
            linhas.append(
                "- Estilo de comunicação preferido: "
                f"{usuario.estilo_instrucao}"
            )

        if getattr(
            usuario,
            "nivel_suporte",
            None
        ):
            linhas.append(
                "- Nível de suporte necessário: "
                f"{usuario.nivel_suporte}"
            )

        return "\n".join(linhas)

    def _instrucao_base_tea(self, usuario):
        base_prompt = (
            "Você é um assistente especializado em "
            "acessibilidade para pessoas com TEA "
            "(Transtorno do Espectro Autista).\n"

            "Seu papel é reduzir a carga cognitiva, "
            "cansaço mental e ambiguidade.\n"

            "Diretrizes obrigatórias:\n"

            "- Nunca use parágrafos longos, blocos densos "
            "de texto ou jargões complexos.\n"

            "- Use frases curtas, ordem direta "
            "(Sujeito + Verbo + Objeto).\n"

            "- Divida as respostas visualmente usando "
            "tópicos/bullets claros.\n"
        )

        estilo = (
            getattr(
                usuario,
                "estilo_instrucao",
                None
            )
            if usuario
            else None
        )

        if estilo == "direto":
            base_prompt += (
                "- Seja extremamente conciso. "
                "Vá direto ao ponto, use o mínimo "
                "de palavras possível.\n"
            )
        else:
            base_prompt += (
                "- Se precisar explicar um conceito, "
                "faça-o em etapas lógicas e "
                "sequenciais simples.\n"
            )

        base_prompt += (
            "\n"
            + self._montar_contexto_usuario(
                usuario
            )
        )

        return base_prompt

    # --------------------------------------------------------
    # Limpeza das respostas
    # --------------------------------------------------------
    def _limpar_marcadores(
        self,
        linha: str
    ) -> str:

        sem_marcador_inicial = linha.lstrip(
            "0123456789.-*• "
        )

        sem_negrito = re.sub(
            r"\*+",
            "",
            sem_marcador_inicial
        )

        return sem_negrito.strip()

    # --------------------------------------------------------
    # Controle do chat
    # --------------------------------------------------------
    def _obter_chat(self, usuario):
        usuario_id = (
            getattr(
                usuario,
                "id",
                None
            )
            if usuario
            else "anonimo"
        )

        if usuario_id not in self._chats:
            system_instruction = (
                self._instrucao_base_tea(
                    usuario
                )
            )

            self._chats[usuario_id] = (
                self.client.chats.create(
                    model=MODELO_GEMINI,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            system_instruction
                        ),
                        temperature=0.3,
                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        ),
                    ),
                )
            )

        return self._chats[usuario_id]

    def reiniciar_chat(
        self,
        usuario
    ) -> None:

        usuario_id = (
            getattr(
                usuario,
                "id",
                None
            )
            if usuario
            else "anonimo"
        )

        self._chats.pop(
            usuario_id,
            None
        )

    # --------------------------------------------------------
    # Chat livre
    # --------------------------------------------------------
    def obter_resposta_chat(
        self,
        pergunta: str,
        usuario=None
    ) -> list:

        if not self.client:
            raise ValueError(
                "IA indisponível: configure a variável "
                "de ambiente GEMINI_API_KEY."
            )

        chat = self._obter_chat(
            usuario
        )

        try:
            response = chat.send_message(
                pergunta
            )

            linhas = [
                linha.strip()
                for linha
                in response.text.split("\n")
                if linha.strip()
            ]

            return [
                self._limpar_marcadores(
                    linha
                )
                for linha in linhas
                if self._limpar_marcadores(
                    linha
                )
            ]

        except Exception as e:
            raise ValueError(
                "Erro ao nos comunicarmos com a IA: "
                f"{str(e)}"
            )

    # --------------------------------------------------------
    # Gerar passos para tarefa
    # --------------------------------------------------------
    def gerar_passos_tarefa(
        self,
        titulo_tarefa: str,
        usuario=None
    ) -> list:

        """Usa o Gemini para quebrar uma tarefa macro
        em micro-ações sequenciais, levando em conta
        o contexto do usuário.
        """

        if not self.client:
            raise ValueError(
                "IA indisponível: configure a variável "
                "de ambiente GEMINI_API_KEY."
            )

        prompt = (
            "Quebre a seguinte tarefa em exatamente "
            "3 ou 4 passos sequenciais, "
            "curtos e fáceis de focar: "
            f"'{titulo_tarefa}'. "
            "Escreva apenas os passos, um por linha, "
            "sem introduções ou numeração manual."
        )

        system_instruction = (
            "Você é um especialista em produtividade "
            "para neurodivergentes. "
            "Crie checklists limpos, com verbos de ação "
            "claros e livres de poluição textual.\n\n"
            + self._montar_contexto_usuario(
                usuario
            )
        )

        try:
            response = (
                self.client.models.generate_content(
                    model=MODELO_GEMINI,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            system_instruction
                        ),
                        temperature=0.2,
                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        ),
                    ),
                )
            )

            passos = [
                linha.strip()
                for linha
                in response.text.split("\n")
                if linha.strip()
            ]

            passos_limpos = []

            for passo in passos:
                passo_limpo = (
                    self._limpar_marcadores(
                        passo
                    )
                )

                if passo_limpo:
                    passos_limpos.append(
                        passo_limpo
                    )

            if not passos_limpos:
                raise ValueError(
                    "A IA não retornou nenhum "
                    "passo aproveitável."
                )

            return passos_limpos

        except ValueError:
            raise

        except Exception as e:
            raise ValueError(
                "Não foi possível gerar os passos: "
                f"{str(e)}"
            )