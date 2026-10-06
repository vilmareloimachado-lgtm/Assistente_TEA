from controllers.tarefa_controller import TarefaController


controller = TarefaController()


# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def ler_id(mensagem):
    while True:
        valor = input(mensagem).strip()

        if valor.isdigit():
            return int(valor)

        print("Digite um ID numérico válido.")


def mostrar_resultado(resposta):
    if isinstance(resposta, dict):
        mensagem = resposta.get("mensagem")

        if mensagem:
            print(mensagem)
        else:
            print(resposta)
    else:
        print(resposta)


def mostrar_tarefa(tarefa):
    if not tarefa:
        print("Tarefa não encontrada.")
        return

    tarefa_id = tarefa.get("tarefa_id", tarefa.get("id", "-"))

    print(f"\nID da tarefa: {tarefa_id}")
    print(f"Título: {tarefa.get('titulo', '')}")
    print(f"Descrição: {tarefa.get('descricao', '')}")
    print(f"Tipo: {tarefa.get('tipo', '')}")
    print(f"Prioridade: {tarefa.get('prioridade', '')}")
    print(f"Prazo: {tarefa.get('prazo') or 'Sem prazo'}")

    concluida = tarefa.get("concluida", False)
    print(f"Concluída: {'Sim' if concluida else 'Não'}")

    passos = tarefa.get("passos", [])

    if passos:
        print("\nPassos:")

        for passo in passos:
            passo_id = passo.get("passo_id", passo.get("id", "-"))
            texto = passo.get("texto", "")
            concluido = passo.get("concluido", False)

            status = "Concluído" if concluido else "Pendente"

            print(
                f"  ID {passo_id} - "
                f"{texto} - "
                f"{status}"
            )
    else:
        print("Passos: nenhum passo cadastrado.")


# ------------------------------------------------------------
# Menu principal
# ------------------------------------------------------------
while True:
    print("\n" + "=" * 60)
    print("MENU DE TESTE - TAREFAS / PASSOS / DASHBOARD")
    print("=" * 60)

    print("1 - Criar tarefa")
    print("2 - Listar tarefas")
    print("3 - Buscar tarefa")
    print("4 - Editar tarefa")
    print("5 - Alterar status da tarefa")
    print("6 - Excluir tarefa")
    print("7 - Definir passos da tarefa")
    print("8 - Alterar status de um passo")
    print("9 - Excluir passo")
    print("10 - Dashboard")
    print("0 - Sair")

    opcao = input("\nEscolha uma opção: ").strip()

    # --------------------------------------------------------
    # 1 - Criar tarefa
    # --------------------------------------------------------
    if opcao == "1":
        print("\n--- CRIAR TAREFA ---")

        usuario_id = ler_id("ID do usuário TEA: ")

        print("\nTipo da tarefa:")
        print("1 - Tarefa diária")
        print("2 - Tarefa educacional")

        escolha_tipo = input("Escolha: ").strip()

        if escolha_tipo == "1":
            tipo = "tarefas_diarias"
        elif escolha_tipo == "2":
            tipo = "tarefas_educacionais"
        else:
            print("Tipo inválido.")
            continue

        titulo = input("Título: ").strip()
        descricao = input("Descrição: ").strip()

        print("\nPrioridade:")
        print("1 - Baixa")
        print("2 - Média")
        print("3 - Alta")

        escolha_prioridade = input("Escolha: ").strip()

        if escolha_prioridade == "1":
            prioridade = "baixa"
        elif escolha_prioridade == "2":
            prioridade = "media"
        elif escolha_prioridade == "3":
            prioridade = "alta"
        else:
            print("Prioridade inválida.")
            continue

        prazo = input(
            "Prazo DD/MM/AAAA (Enter para deixar sem prazo): "
        ).strip()

        resposta = controller.criar_tarefa(
            usuario_id,
            tipo,
            titulo,
            descricao,
            prioridade,
            prazo
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 2 - Listar tarefas
    # --------------------------------------------------------
    elif opcao == "2":
        print("\n--- LISTAR TAREFAS ---")

        usuario_id = ler_id("ID do usuário TEA: ")

        print("\nFiltro:")
        print("1 - Todas")
        print("2 - Tarefas diárias")
        print("3 - Tarefas educacionais")

        escolha = input("Escolha: ").strip()

        if escolha == "1":
            tipo = None
        elif escolha == "2":
            tipo = "tarefas_diarias"
        elif escolha == "3":
            tipo = "tarefas_educacionais"
        else:
            print("Opção inválida.")
            continue

        tarefas = controller.listar_tarefas(
            usuario_id,
            tipo
        )

        if not tarefas:
            print("Nenhuma tarefa encontrada.")
        else:
            print(f"\nTotal de tarefas: {len(tarefas)}")

            for tarefa in tarefas:
                mostrar_tarefa(tarefa)
                print("-" * 40)

    # --------------------------------------------------------
    # 3 - Buscar tarefa
    # --------------------------------------------------------
    elif opcao == "3":
        print("\n--- BUSCAR TAREFA ---")

        tarefa_id = ler_id("ID da tarefa: ")

        resposta = controller.buscar_tarefa(tarefa_id)

        if (
            isinstance(resposta, dict)
            and resposta.get("sucesso") is False
        ):
            mostrar_resultado(resposta)
        else:
            mostrar_tarefa(resposta)

    # --------------------------------------------------------
    # 4 - Editar tarefa
    # --------------------------------------------------------
    elif opcao == "4":
        print("\n--- EDITAR TAREFA ---")

        tarefa_id = ler_id("ID da tarefa: ")

        print(
            "\nDeixe o campo vazio quando não quiser "
            "alterar o valor."
        )

        titulo = input("Novo título: ").strip()
        descricao = input("Nova descrição: ").strip()

        print("\nNova prioridade:")
        print("Enter - Não alterar")
        print("1 - Baixa")
        print("2 - Média")
        print("3 - Alta")

        escolha_prioridade = input("Escolha: ").strip()

        if escolha_prioridade == "":
            prioridade = None
        elif escolha_prioridade == "1":
            prioridade = "baixa"
        elif escolha_prioridade == "2":
            prioridade = "media"
        elif escolha_prioridade == "3":
            prioridade = "alta"
        else:
            print("Prioridade inválida.")
            continue

        prazo = input(
            "Novo prazo DD/MM/AAAA "
            "(Enter para não alterar): "
        ).strip()

        titulo = titulo if titulo else None
        descricao = descricao if descricao else None
        prazo = prazo if prazo else None

        resposta = controller.editar_tarefa(
            tarefa_id,
            titulo,
            descricao,
            prioridade,
            prazo
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 5 - Alterar status da tarefa
    # --------------------------------------------------------
    elif opcao == "5":
        print("\n--- ALTERAR STATUS DA TAREFA ---")

        tarefa_id = ler_id("ID da tarefa: ")

        resposta = controller.alternar_status_tarefa(
            tarefa_id
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 6 - Excluir tarefa
    # --------------------------------------------------------
    elif opcao == "6":
        print("\n--- EXCLUIR TAREFA ---")

        tarefa_id = ler_id("ID da tarefa: ")

        confirmacao = input(
            "Confirma a exclusão? (S/N): "
        ).strip().lower()

        if confirmacao != "s":
            print("Exclusão cancelada.")
            continue

        resposta = controller.excluir_tarefa(
            tarefa_id
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 7 - Definir passos da tarefa
    # --------------------------------------------------------
    elif opcao == "7":
        print("\n--- DEFINIR PASSOS DA TAREFA ---")

        tarefa_id = ler_id("ID da tarefa: ")

        quantidade = ler_id(
            "Quantidade de passos: "
        )

        if quantidade <= 0:
            print("Informe pelo menos 1 passo.")
            continue

        lista_textos = []

        for numero in range(1, quantidade + 1):
            texto_passo = input(
                f"Passo {numero}: "
            ).strip()

            if not texto_passo:
                print("O texto do passo não pode ficar vazio.")
                lista_textos = []
                break

            lista_textos.append(texto_passo)

        if not lista_textos:
            continue

        resposta = controller.definir_passos_ia(
            tarefa_id,
            lista_textos
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 8 - Alterar status de um passo
    # --------------------------------------------------------
    elif opcao == "8":
        print("\n--- ALTERAR STATUS DO PASSO ---")

        passo_id = ler_id("ID do passo: ")

        resposta = controller.alternar_status_passo(
            passo_id
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 9 - Excluir passo
    # --------------------------------------------------------
    elif opcao == "9":
        print("\n--- EXCLUIR PASSO ---")

        passo_id = ler_id("ID do passo: ")

        confirmacao = input(
            "Confirma a exclusão do passo? (S/N): "
        ).strip().lower()

        if confirmacao != "s":
            print("Exclusão cancelada.")
            continue

        resposta = controller.excluir_passo(
            passo_id
        )

        mostrar_resultado(resposta)

    # --------------------------------------------------------
    # 10 - Dashboard
    # --------------------------------------------------------
    elif opcao == "10":
        print("\n--- DASHBOARD ---")

        usuario_id = ler_id("ID do usuário TEA: ")

        resposta = controller.resumo_tarefas(
            usuario_id
        )

        if isinstance(resposta, dict):
            print("\nResumo:")

            for chave, valor in resposta.items():
                print(f"{chave}: {valor}")
        else:
            print(resposta)

    # --------------------------------------------------------
    # 0 - Sair
    # --------------------------------------------------------
    elif opcao == "0":
        print("\nEncerrando menu de teste.")
        break

    else:
        print("Opção inválida.")