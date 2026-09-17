import re
from datetime import datetime

from controllers.usuario_controller import UsuarioController

controller = UsuarioController()


def _validar_formato_nome(nome):
    return bool(re.fullmatch(r"[A-Za-zÀ-ÿ\s]+", nome))


def _pedir_nome_novo():
    """Pede o nome de um perfil NOVO, validando formato e duplicidade na hora."""
    while True:
        nome = input("Nome (apenas letras e espaços): ").strip()
        if not nome:
            print(">> O nome não pode ficar vazio. Tente novamente.\n")
            continue
        if not _validar_formato_nome(nome):
            print(">> Nome inválido! Digite apenas letras e espaços.\n")
            continue
        if len(nome) < 3:
            print(">> O nome precisa ter pelo menos 3 caracteres.\n")
            continue
        if nome in controller.listar_perfis():
            print(">> Já existe um perfil com esse nome. Escolha outro.\n")
            continue
        return nome


def _pedir_estilo():
    while True:
        print("Estilo de instrução: 1) direto  2) detalhado")
        op = input("Opção: ").strip()
        if op == "1":
            return "direto"
        if op == "2":
            return "detalhado"
        print(">> Opção inválida. Digite 1 ou 2.\n")


def _pedir_nivel():
    mapa = {"1": "Leve", "2": "Moderado", "3": "Severo"}
    while True:
        print("Nível de suporte: 1) Leve  2) Moderado  3) Severo")
        op = input("Opção: ").strip()
        if op in mapa:
            return mapa[op]
        print(">> Opção inválida. Digite 1, 2 ou 3.\n")


def _pedir_data_nascimento():
    while True:
        data_str = input("Data de nascimento (DD/MM/AAAA): ").strip()
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return data_str
        except ValueError:
            print(">> Data inválida. Utilize o formato DD/MM/AAAA.\n")


def _pedir_senha_nova():
    while True:
        senha = input("Senha de login (mín. 6 caracteres): ").strip()
        if len(senha) < 6:
            print(">> A senha precisa ter pelo menos 6 caracteres.\n")
            continue
        return senha


def criar():
    print("\n--- Criar novo perfil ---")
    nome = _pedir_nome_novo()
    estilo = _pedir_estilo()
    nivel = _pedir_nivel()
    data_nasc = _pedir_data_nascimento()
    senha = _pedir_senha_nova()

    resultado = controller.criar_perfil(nome, estilo, nivel, data_nasc, senha)
    print("\n" + resultado["mensagem"])


def buscar():
    print("\n--- Buscar perfil ---")
    nome = input("Nome do perfil: ").strip()
    resultado = controller.buscar_perfil(nome)
    print("\n" + resultado["mensagem"])


def listar():
    print("\n--- Perfis cadastrados ---")
    nomes = controller.listar_perfis()
    if not nomes:
        print("(nenhum perfil cadastrado ainda)")
    for n in nomes:
        print("-", n)


def _pedir_nome_para_localizar():
    """Nome do perfil que já existe e vai ser editado — só confirma que existe."""
    while True:
        nome = input("Nome atual do perfil: ").strip()
        if not nome:
            print(">> Digite um nome.\n")
            continue
        if nome not in controller.listar_perfis():
            print(">> Nenhum perfil encontrado com esse nome.\n")
            continue
        return nome


def _pedir_novo_nome_opcional(nome_atual):
    while True:
        novo_nome = input("Novo nome (Enter = não alterar): ").strip()
        if not novo_nome:
            return None
        if not _validar_formato_nome(novo_nome):
            print(">> Nome inválido! Digite apenas letras e espaços.\n")
            continue
        if len(novo_nome) < 3:
            print(">> O nome precisa ter pelo menos 3 caracteres.\n")
            continue
        if novo_nome != nome_atual and novo_nome in controller.listar_perfis():
            print(">> Já existe um perfil com esse nome. Escolha outro.\n")
            continue
        return novo_nome


def _pedir_estilo_opcional():
    while True:
        op = input("Novo estilo — 1) direto  2) detalhado  (Enter = não alterar): ").strip()
        if op == "":
            return None
        if op == "1":
            return "direto"
        if op == "2":
            return "detalhado"
        print(">> Opção inválida. Digite 1, 2 ou Enter.\n")


def _pedir_nivel_opcional():
    mapa = {"1": "Leve", "2": "Moderado", "3": "Severo"}
    while True:
        op = input("Novo nível — 1) Leve  2) Moderado  3) Severo  (Enter = não alterar): ").strip()
        if op == "":
            return None
        if op in mapa:
            return mapa[op]
        print(">> Opção inválida. Digite 1, 2, 3 ou Enter.\n")


def _pedir_data_opcional():
    while True:
        data_str = input("Nova data de nascimento (DD/MM/AAAA, Enter = não alterar): ").strip()
        if data_str == "":
            return None
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return data_str
        except ValueError:
            print(">> Data inválida. Utilize o formato DD/MM/AAAA.\n")


def _pedir_senha_opcional():
    while True:
        senha = input("Nova senha (mín. 6 caracteres, Enter = não alterar): ").strip()
        if senha == "":
            return None
        if len(senha) < 6:
            print(">> A senha precisa ter pelo menos 6 caracteres.\n")
            continue
        return senha


def atualizar():
    print("\n--- Atualizar perfil ---")
    print("(deixe em branco e aperte Enter para não alterar o campo)")
    nome = _pedir_nome_para_localizar()
    novo_nome = _pedir_novo_nome_opcional(nome)
    estilo = _pedir_estilo_opcional()
    nivel = _pedir_nivel_opcional()
    data_nasc = _pedir_data_opcional()
    senha = _pedir_senha_opcional()

    resultado = controller.atualizar_perfil(
        nome,
        novo_nome=novo_nome,
        estilo_instrucao=estilo,
        nivel_suporte=nivel,
        data_nascimento=data_nasc,
        senha_login=senha
    )
    print("\n" + resultado["mensagem"])


def excluir():
    print("\n--- Excluir perfil ---")
    nome = input("Nome do perfil a excluir: ").strip()
    resultado = controller.excluir_perfil(nome)
    print("\n" + resultado["mensagem"])


def main():
    while True:
        print("\n" + "=" * 50)
        print("TESTE REAL - CAMADA FATIADA (USUÁRIO)".center(50))
        print("=" * 50)
        print("1. Criar perfil")
        print("2. Buscar perfil")
        print("3. Listar perfis")
        print("4. Atualizar perfil")
        print("5. Excluir perfil")
        print("6. Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            criar()
        elif opcao == "2":
            buscar()
        elif opcao == "3":
            listar()
        elif opcao == "4":
            atualizar()
        elif opcao == "5":
            excluir()
        elif opcao == "6":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
