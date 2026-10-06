from controllers.ia_controller import IaController
from controllers.tarefa_controller import TarefaController


controller = IaController()
tarefa_controller = TarefaController()


# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def ler_id(mensagem):
    while True:
        valor = input(mensagem).strip()

        if valor.isdigit():
            return int(valor)

        print("Digite um ID numérico válido.")


def mostrar_resposta_chat(resposta):
    if not isinstance(resposta, dict):
        print(resposta)
        return

    if not resposta.get("sucesso"):
        print(resposta.get("mensagem", "Erro desconhecido."))
        return

    respostas = resposta.get("respostas", [])

    if not respostas:
        print("A IA não retornou nenhuma resposta.")
        return

    if isinstance(respostas, list):
        for linha in respostas:
            print(linha)
    else:
        print(respostas)


def mostrar_passos(resposta):
    if not isinstance(resposta, dict):
        print(resposta)
        return

    if not resposta.get("sucesso"):
        print(resposta.get("mensagem", "Erro desconhecido."))
        return

    passos = resposta.get("passos", [])

    if not passos:
        print("A IA não retornou nenhum passo.")
        return

    for numero, passo in enumerate(passos, start=1):
        print(f"{numero}. {passo}")


# ------------------------------------------------------------
# Fluxo de sugestão de passos
# ------------------------------------------------------------
def testar_sugestao_passos(tarefa_id):
    while True:
        try:
            resposta = controller.sugerir_passos(
                tarefa_id
            )

        except Exception as erro:
            print(f"\nErro ao gerar sugestão: {erro}")
            return

        if not isinstance(resposta, dict):
            print("\nResposta inesperada da IA:")
            print(resposta)
            return

        if not resposta.get("sucesso"):
            print(
                "\n" +
                resposta.get(
                    "mensagem",
                    "Não foi possível gerar a sugestão."
                )
            )
            return

        passos = resposta.get("passos", [])

        if not passos:
            print("\nA IA não retornou nenhum passo.")
            return

        print("\nSugestão da IA:")
        mostrar_passos(resposta)

        # ----------------------------------------------------
        # Decisão sobre a sugestão
        # ----------------------------------------------------
        while True:
            print("\nO que deseja fazer?")
            print("1 - Aceitar sugestão")
            print("2 - Gerar nova sugestão")
            print("3 - Cancelar")

            decisao = input(
                "\nEscolha uma opção: "
            ).strip()

            # ------------------------------------------------
            # 1 - Aceitar sugestão
            # ------------------------------------------------
            if decisao == "1":
                try:
                    resultado = tarefa_controller.definir_passos_ia(
                        tarefa_id,
                        passos
                    )

                    if resultado.get("sucesso"):
                        print(
                            "\n" +
                            resultado.get(
                                "mensagem",
                                "Passos gravados com sucesso."
                            )
                        )
                    else:
                        print(
                            "\n" +
                            resultado.get(
                                "mensagem",
                                "Não foi possível gravar os passos."
                            )
                        )

                except Exception as erro:
                    print(
                        f"\nErro ao gravar os passos: {erro}"
                    )

                return

            # ------------------------------------------------
            # 2 - Gerar nova sugestão
            # ------------------------------------------------
            elif decisao == "2":
                print(
                    "\nGerando uma nova sugestão..."
                )

                # Não grava a sugestão atual.
                # Volta ao início do laço e solicita
                # uma nova sugestão ao Gemini.
                break

            # ------------------------------------------------
            # 3 - Cancelar
            # ------------------------------------------------
            elif decisao == "3":
                print(
                    "\nOperação cancelada. "
                    "Nenhuma alteração foi feita na tarefa."
                )
                return

            else:
                print("Opção inválida.")


# ------------------------------------------------------------
# Menu principal
# ------------------------------------------------------------
while True:
    print("\n" + "=" * 60)
    print("MENU DE TESTE - INTELIGÊNCIA ARTIFICIAL")
    print("=" * 60)

    print("1 - Chat livre com usuário TEA")
    print("2 - Sugerir passos para uma tarefa")
    print("0 - Sair")

    opcao = input(
        "\nEscolha uma opção: "
    ).strip()

    # --------------------------------------------------------
    # 1 - Chat livre
    # --------------------------------------------------------
    if opcao == "1":
        print("\n--- CHAT LIVRE ---")

        usuario_id = ler_id(
            "ID do usuário TEA: "
        )

        pergunta = input(
            "Digite a pergunta para a IA: "
        ).strip()

        if not pergunta:
            print("A pergunta não pode ficar vazia.")
            continue

        try:
            resposta = controller.chat_livre(
                usuario_id,
                pergunta
            )

            print("\nResposta da IA:")
            mostrar_resposta_chat(resposta)

        except Exception as erro:
            print(f"\nErro: {erro}")

    # --------------------------------------------------------
    # 2 - Sugerir passos
    # --------------------------------------------------------
    elif opcao == "2":
        print("\n--- SUGERIR PASSOS PARA TAREFA ---")

        tarefa_id = ler_id(
            "ID da tarefa: "
        )

        testar_sugestao_passos(
            tarefa_id
        )

    # --------------------------------------------------------
    # 0 - Sair
    # --------------------------------------------------------
    elif opcao == "0":
        print("\nEncerrando menu de teste da IA.")
        break

    else:
        print("Opção inválida.")