import os
import re
from datetime import date

from google import genai
from google.genai import types

# Inicializa o cliente se a chave de API estiver presente
API_KEY = os.environ.get("GEMINI_API_KEY")
_client_padrao = genai.Client() if API_KEY else None

# Modelo ideal para tarefas rápidas de texto e resumos no terminal
MODELO_GEMINI = "gemini-2.5-flash"


class IaService:
    """Camada de serviço para as chamadas à IA (Gemini).

    Não tem repository/model porque não persiste nada no banco — quem
    guarda os dados (ex: passos aceitos) é o TarefaService, através do
    IaController.
    """

    def __init__(self, gemini_client=None):
        self.client = gemini_client if gemini_client is not None else _client_padrao
        # Guarda uma sessão de chat por usuário, para manter a memória
        # da conversa entre uma pergunta e outra (chave = usuario.id).
        self._chats = {}

    # ---------- montagem de contexto do usuário ----------

    def _calcular_idade(self, data_nascimento):
        if not data_nascimento:
            return None
        hoje = date.today()
        nascimento = data_nascimento.date() if hasattr(data_nascimento, "date") else data_nascimento
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return idade

    def _montar_contexto_usuario(self, usuario):
        """Monta um bloco de texto com dados do usuário relevantes para a IA
        personalizar a resposta (idade, estilo de comunicação, nível de suporte)."""
        if usuario is None:
            return "Nenhuma informação adicional do usuário disponível."

        idade = self._calcular_idade(getattr(usuario, "data_nascimento", None))
        linhas = ["Informações do usuário, para adaptar a resposta:"]

        if idade is not None:
            linhas.append(f"- Idade: {idade} anos")
        if getattr(usuario, "estilo_instrucao", None):
            linhas.append(f"- Estilo de comunicação preferido: {usuario.estilo_instrucao}")
        if getattr(usuario, "nivel_suporte", None):
            linhas.append(f"- Nível de suporte necessário: {usuario.nivel_suporte}")

        return "\n".join(linhas)

    def _instrucao_base_tea(self, usuario):
        base_prompt = (
            "Você é um assistente especializado em acessibilidade para pessoas com TEA "
            "(Transtorno do Espectro Autista).\n"
            "Seu papel é reduzir a carga cognitiva, cansaço mental e ambiguidade.\n"
            "Diretrizes obrigatórias:\n"
            "- Nunca use parágrafos longos, blocos densos de texto ou jargões complexos.\n"
            "- Use frases curtas, ordem direta (Sujeito + Verbo + Objeto).\n"
            "- Divida as respostas visualmente usando tópicos/bullets claros.\n"
        )

        estilo = getattr(usuario, "estilo_instrucao", None) if usuario else None
        if estilo == "direto":
            base_prompt += "- Seja extremamente conciso. Vá direto ao ponto, use o mínimo de palavras possível.\n"
        else:
            base_prompt += "- Se precisar explicar um conceito, faça-o em etapas lógicas e sequenciais simples.\n"

        base_prompt += "\n" + self._montar_contexto_usuario(usuario)
        return base_prompt

    def _limpar_marcadores(self, linha: str) -> str:
        sem_marcador_inicial = linha.lstrip("0123456789.-*• ")
        sem_negrito = re.sub(r"\*+", "", sem_marcador_inicial)
        return sem_negrito.strip()

    def _obter_chat(self, usuario):
        usuario_id = getattr(usuario, "id", None) if usuario else "anonimo"

        if usuario_id not in self._chats:
            system_instruction = self._instrucao_base_tea(usuario)
            self._chats[usuario_id] = self.client.chats.create(
                model=MODELO_GEMINI,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )

        return self._chats[usuario_id]

    def reiniciar_chat(self, usuario) -> None:
        usuario_id = getattr(usuario, "id", None) if usuario else "anonimo"
        self._chats.pop(usuario_id, None)

    # ---------- funções expostas ----------

    def obter_resposta_chat(self, pergunta: str, usuario=None) -> list:
        if not self.client:
            raise ValueError(
            "IA indisponível: configure a variável de ambiente GEMINI_API_KEY."
        )

        chat = self._obter_chat(usuario)

        try:
            response = chat.send_message(pergunta)
            linhas = [linha.strip() for linha in response.text.split("\n") if linha.strip()]
            return [self._limpar_marcadores(linha) for linha in linhas if self._limpar_marcadores(linha)]
        except Exception as e:
            raise ValueError(f"Erro ao nos comunicarmos com a IA: {str(e)}")

    def gerar_passos_tarefa(self, titulo_tarefa: str, usuario=None) -> list:
        """Usa o Gemini para quebrar uma tarefa macro em micro-ações sequenciais,
        levando em conta o contexto do usuário (idade, estilo, nível de suporte)."""
        if not self.client:
            raise ValueError(
                "IA indisponível: configure a variável de ambiente GEMINI_API_KEY."
            )

        prompt = (
            f"Quebre a seguinte tarefa em exatamente 3 ou 4 passos sequenciais, "
            f"curtos e fáceis de focar: '{titulo_tarefa}'. "
            f"Escreva apenas os passos, um por linha, sem introduções ou numeração manual."
        )

        system_instruction = (
            "Você é um especialista em produtividade para neurodivergentes. "
            "Crie checklists limpos, com verbos de ação claros e livres de poluição textual.\n\n"
            + self._montar_contexto_usuario(usuario)
        )

        try:
            response = self.client.models.generate_content(
                model=MODELO_GEMINI,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )

            # Limpa e filtra linhas vazias
            passos = [linha.strip() for linha in response.text.split("\n") if linha.strip()]

            # Remove marcadores comuns caso o modelo acabe gerando por teimosia (ex: "-", "*", "1.")
            passos_limpos = []
            for p in passos:
                p_limpo = self._limpar_marcadores(p)
                if p_limpo:
                    passos_limpos.append(p_limpo)

            if not passos_limpos:
                raise ValueError("A IA não retornou nenhum passo aproveitável.")

            return passos_limpos
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Não foi possível gerar os passos: {str(e)}")
