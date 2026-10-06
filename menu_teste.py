from controllers.usuario_controller import UsuarioController


controller = UsuarioController()


def ler_id(mensagem):
    """
    Lê um ID numérico sem encerrar o programa
    caso seja digitado um valor inválido.
    """
    valor = input(mensagem).strip()

    try:
        return int(valor)
    except ValueError:
        print("\nID inválido. Digite apenas números.")
        return None


def cadastrar_cuidador():
    print("\n--- CADASTRAR CUIDADOR ---")

    nome = input("Nome completo: ").strip()
    email = input("E-mail: ").strip()
    senha = input("Senha (mínimo 6 caracteres): ").strip()
    data_nascimento = input(
        "Data de nascimento (DD/MM/AAAA): "
    ).strip()

    resultado = controller.cadastrar_cuidador(
        nome,
        email,
        senha,
        data_nascimento
    )

    print("\n" + resultado["mensagem"])

    if resultado["sucesso"]:
        print("ID do cuidador:", resultado["usuario_id"])


def cadastrar_usuario_tea():
    print("\n--- CADASTRAR USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador responsável: "
    )

    if cuidador_id is None:
        return

    nome = input("Nome completo do usuário TEA: ").strip()

    print("\nEstilo de instrução:")
    print("1 - Direto")
    print("2 - Detalhado")

    opcao_estilo = input("Escolha: ").strip()

    if opcao_estilo == "1":
        estilo_instrucao = "direto"
    elif opcao_estilo == "2":
        estilo_instrucao = "detalhado"
    else:
        print("\nEstilo inválido.")
        return

    print("\nNível de suporte:")
    print("1 - Leve")
    print("2 - Moderado")
    print("3 - Severo")

    opcao_nivel = input("Escolha: ").strip()

    if opcao_nivel == "1":
        nivel_suporte = "Leve"
    elif opcao_nivel == "2":
        nivel_suporte = "Moderado"
    elif opcao_nivel == "3":
        nivel_suporte = "Severo"
    else:
        print("\nNível de suporte inválido.")
        return

    data_nascimento = input(
        "Data de nascimento (DD/MM/AAAA): "
    ).strip()

    pin = input(
        "PIN de acesso (Enter para não utilizar): "
    ).strip()

    if pin == "":
        pin = None

    resultado = controller.criar_usuario_tea(
        cuidador_id,
        nome,
        estilo_instrucao,
        nivel_suporte,
        data_nascimento,
        pin
    )

    print("\n" + resultado["mensagem"])

    if resultado["sucesso"]:
        print("ID do usuário TEA:", resultado["usuario_id"])


def listar_usuarios_cuidador():
    print("\n--- USUÁRIOS TEA DO CUIDADOR ---")

    cuidador_id = ler_id(
        "ID do cuidador: "
    )

    if cuidador_id is None:
        return

    resultado = controller.listar_usuarios_do_cuidador(
        cuidador_id
    )

    if not resultado["sucesso"]:
        print("\n" + resultado["mensagem"])
        return

    usuarios = resultado["usuarios"]

    if not usuarios:
        print(
            "\nEste cuidador não possui usuários TEA "
            "vinculados no momento."
        )
        return

    print("\n" + resultado["mensagem"])
    print("-" * 40)

    for usuario in usuarios:
        print("ID:", usuario["usuario_id"])
        print("Nome:", usuario["nome"])
        print("Tipo:", usuario["tipo_usuario"])
        print("Estilo de instrução:", usuario["estilo_instrucao"])
        print("Nível de suporte:", usuario["nivel_suporte"])
        print("Data de nascimento:", usuario["data_nascimento"])

        if usuario["tem_pin"]:
            print("PIN de acesso: configurado")
        else:
            print("PIN de acesso: não configurado")

        print("-" * 40)


def adicionar_cuidador():
    print("\n--- ADICIONAR CUIDADOR AO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador que está realizando a operação: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    email_novo_cuidador = input(
        "E-mail do novo cuidador: "
    ).strip()

    resultado = controller.adicionar_cuidador(
        cuidador_id,
        usuario_id,
        email_novo_cuidador
    )

    print("\n" + resultado["mensagem"])


def listar_cuidadores_usuario():
    print("\n--- CUIDADORES DO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador que está realizando a consulta: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    resultado = controller.listar_cuidadores_do_usuario(
        cuidador_id,
        usuario_id
    )

    if not resultado["sucesso"]:
        print("\n" + resultado["mensagem"])
        return

    cuidadores = resultado["cuidadores"]

    if not cuidadores:
        print("\nNenhum cuidador vinculado a este usuário TEA.")
        return

    print("\n" + resultado["mensagem"])
    print("-" * 40)

    for cuidador in cuidadores:
        print("ID:", cuidador["usuario_id"])
        print("Nome:", cuidador["nome"])
        print("Tipo:", cuidador["tipo_usuario"])
        print("Data de nascimento:", cuidador["data_nascimento"])
        print("E-mail:", cuidador["email"])
        print("-" * 40)


def transferir_cuidador_principal():
    print("\n--- TRANSFERIR CUIDADOR PRINCIPAL ---")

    cuidador_id = ler_id(
        "ID do cuidador principal atual: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    novo_principal_id = ler_id(
        "ID do novo cuidador principal: "
    )

    if novo_principal_id is None:
        return

    print("\nDados da transferência:")
    print("Cuidador principal atual:", cuidador_id)
    print("Usuário TEA:", usuario_id)
    print("Novo cuidador principal:", novo_principal_id)

    confirmacao = input(
        "\nConfirma a transferência? (S/N): "
    ).strip().upper()

    if confirmacao != "S":
        print("\nTransferência cancelada.")
        return

    resultado = controller.transferir_principal(
        cuidador_id,
        usuario_id,
        novo_principal_id
    )

    print("\n" + resultado["mensagem"])


def remover_cuidador_usuario():
    print("\n--- REMOVER CUIDADOR DO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador principal que está realizando a operação: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    cuidador_removido_id = ler_id(
        "ID do cuidador que será removido: "
    )

    if cuidador_removido_id is None:
        return

    print("\nDados da remoção:")
    print("Cuidador principal:", cuidador_id)
    print("Usuário TEA:", usuario_id)
    print("Cuidador que será removido:", cuidador_removido_id)

    confirmacao = input(
        "\nConfirma a remoção do vínculo? (S/N): "
    ).strip().upper()

    if confirmacao != "S":
        print("\nRemoção cancelada.")
        return

    resultado = controller.remover_cuidador(
        cuidador_id,
        usuario_id,
        cuidador_removido_id
    )

    print("\n" + resultado["mensagem"])


def atualizar_usuario_tea():
    print("\n--- ATUALIZAR USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador que está realizando a alteração: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    print("\nPreencha somente os campos que deseja alterar.")
    print("Pressione Enter para manter o valor atual.\n")

    nome = input("Novo nome: ").strip()

    if nome == "":
        nome = None

    print("\nNovo estilo de instrução:")
    print("1 - Direto")
    print("2 - Detalhado")
    print("Enter - Manter atual")

    opcao_estilo = input("Escolha: ").strip()

    if opcao_estilo == "1":
        estilo_instrucao = "direto"
    elif opcao_estilo == "2":
        estilo_instrucao = "detalhado"
    elif opcao_estilo == "":
        estilo_instrucao = None
    else:
        print("\nEstilo inválido.")
        return

    print("\nNovo nível de suporte:")
    print("1 - Leve")
    print("2 - Moderado")
    print("3 - Severo")
    print("Enter - Manter atual")

    opcao_nivel = input("Escolha: ").strip()

    if opcao_nivel == "1":
        nivel_suporte = "Leve"
    elif opcao_nivel == "2":
        nivel_suporte = "Moderado"
    elif opcao_nivel == "3":
        nivel_suporte = "Severo"
    elif opcao_nivel == "":
        nivel_suporte = None
    else:
        print("\nNível de suporte inválido.")
        return

    data_nascimento = input(
        "\nNova data de nascimento "
        "(DD/MM/AAAA ou Enter para manter): "
    ).strip()

    if data_nascimento == "":
        data_nascimento = None

    resultado = controller.atualizar_usuario_tea(
        cuidador_id,
        usuario_id,
        nome,
        estilo_instrucao,
        nivel_suporte,
        data_nascimento
    )

    print("\n" + resultado["mensagem"])


def definir_alterar_pin():
    print("\n--- DEFINIR / ALTERAR PIN DO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador que está realizando a operação: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    pin = input("Digite o novo PIN: ").strip()

    if pin == "":
        print("\nO PIN não pode ficar vazio.")
        return

    confirmacao_pin = input(
        "Digite novamente o novo PIN: "
    ).strip()

    if pin != confirmacao_pin:
        print("\nOs PINs informados são diferentes.")
        return

    resultado = controller.definir_pin(
        cuidador_id,
        usuario_id,
        pin
    )

    print("\n" + resultado["mensagem"])


def entrar_perfil_usuario_tea():
    print("\n--- ENTRAR NO PERFIL DO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    pin = input(
        "PIN do usuário TEA (Enter se não possuir PIN): "
    ).strip()

    if pin == "":
        pin = None

    resultado = controller.login_usuario_tea(
        cuidador_id,
        usuario_id,
        pin
    )

    print("\n" + resultado["mensagem"])


def remover_pin_usuario_tea():
    print("\n--- REMOVER PIN DO USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador que está realizando a operação: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA: "
    )

    if usuario_id is None:
        return

    print("\nDados da operação:")
    print("Cuidador:", cuidador_id)
    print("Usuário TEA:", usuario_id)

    confirmacao = input(
        "\nConfirma a remoção do PIN? (S/N): "
    ).strip().upper()

    if confirmacao != "S":
        print("\nRemoção do PIN cancelada.")
        return

    resultado = controller.remover_pin(
        cuidador_id,
        usuario_id
    )

    print("\n" + resultado["mensagem"])


def excluir_usuario_tea():
    print("\n--- EXCLUIR USUÁRIO TEA ---")

    cuidador_id = ler_id(
        "ID do cuidador principal: "
    )

    if cuidador_id is None:
        return

    usuario_id = ler_id(
        "ID do usuário TEA que será excluído: "
    )

    if usuario_id is None:
        return

    print("\nATENÇÃO!")
    print("Esta operação excluirá o perfil do usuário TEA.")
    print("A exclusão não poderá ser desfeita.")
    print("\nCuidador principal:", cuidador_id)
    print("Usuário TEA:", usuario_id)

    confirmacao = input(
        "\nConfirma a exclusão do usuário TEA? (S/N): "
    ).strip().upper()

    if confirmacao != "S":
        print("\nExclusão cancelada.")
        return

    resultado = controller.excluir_usuario_tea(
        cuidador_id,
        usuario_id
    )

    print("\n" + resultado["mensagem"])


def excluir_cuidador():
    print("\n--- EXCLUIR CONTA DO CUIDADOR ---")

    cuidador_id = ler_id(
        "ID do cuidador que será excluído: "
    )

    if cuidador_id is None:
        return

    senha = input(
        "Digite a senha do cuidador: "
    ).strip()

    if senha == "":
        print("\nA senha é obrigatória para excluir a conta.")
        return

    print("\nATENÇÃO!")
    print("Esta operação excluirá a conta do cuidador.")
    print("A exclusão não poderá ser desfeita.")
    print("Cuidador:", cuidador_id)

    confirmacao = input(
        "\nConfirma a exclusão da conta? (S/N): "
    ).strip().upper()

    if confirmacao != "S":
        print("\nExclusão cancelada.")
        return

    resultado = controller.excluir_cuidador(
        cuidador_id,
        senha
    )

    print("\n" + resultado["mensagem"])


def login_cuidador():
    print("\n--- LOGIN DO CUIDADOR ---")

    email = input("E-mail: ").strip()
    senha = input("Senha: ").strip()

    if email == "":
        print("\nO e-mail não pode ficar vazio.")
        return

    if senha == "":
        print("\nA senha não pode ficar vazia.")
        return

    resultado = controller.login(
        email,
        senha
    )

    print("\n" + resultado["mensagem"])


def main():
    while True:
        print("\n" + "=" * 40)
        print("ASSISTENTE TEA - MENU DE TESTE".center(40))
        print("=" * 40)

        print("1 - Cadastrar cuidador")
        print("2 - Cadastrar usuário TEA")
        print("3 - Listar usuários TEA do cuidador")
        print("4 - Adicionar cuidador ao usuário TEA")
        print("5 - Listar cuidadores do usuário TEA")
        print("6 - Transferir cuidador principal")
        print("7 - Remover cuidador do usuário TEA")
        print("8 - Atualizar usuário TEA")
        print("9 - Definir/alterar PIN do usuário TEA")
        print("10 - Entrar no perfil do usuário TEA")
        print("11 - Remover PIN do usuário TEA")
        print("12 - Excluir usuário TEA")
        print("13 - Excluir conta do cuidador")
        print("14 - Login do cuidador")
        print("0 - Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            cadastrar_cuidador()

        elif opcao == "2":
            cadastrar_usuario_tea()

        elif opcao == "3":
            listar_usuarios_cuidador()

        elif opcao == "4":
            adicionar_cuidador()

        elif opcao == "5":
            listar_cuidadores_usuario()

        elif opcao == "6":
            transferir_cuidador_principal()

        elif opcao == "7":
            remover_cuidador_usuario()

        elif opcao == "8":
            atualizar_usuario_tea()

        elif opcao == "9":
            definir_alterar_pin()

        elif opcao == "10":
            entrar_perfil_usuario_tea()

        elif opcao == "11":
            remover_pin_usuario_tea()

        elif opcao == "12":
            excluir_usuario_tea()

        elif opcao == "13":
            excluir_cuidador()

        elif opcao == "14":
            login_cuidador()

        elif opcao == "0":
            print("\nEncerrando menu de teste.")
            break

        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    main()