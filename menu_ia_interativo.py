"""
Menu interativo para testar o Chat Livre com a IA
(controller -> service -> Gemini), usando o contexto do perfil selecionado
(idade, estilo de comunicação, nível de suporte) para personalizar as respostas.

Rode este arquivo na raiz do projeto (mesmo nível do main.py):
    python menu_ia_interativo.py

Requer GEMINI_API_KEY configurada no .env e pelo menos um perfil de usuário
criado (use o menu_usuario_interativo.py).
"""

from controllers.usuario_controller import UsuarioController
from controllers.ia_controller import IaController

usuario_controller = UsuarioController()
ia_controller = IaController()


def _selecionar_perfil():
    """Retorna (nome, usuario_id) de um perfil existente, ou None se não houver nenhum."""
    nomes = usuario_controller.listar_perfis()
    if not nomes:
        print(">> Nenhum perfil cadastrado ainda. Crie um primeiro com o menu_usuario_interativo.py.")
        return None

    while True:
        print("\nPerfis disponíveis:")
        for n in nomes:
            print("-", n)
        nome = input("Nome do perfil: ").strip()
        resultado = usuario_controller.buscar_perfil(nome)
        if resultado["sucesso"]:
            return nome, resultado["usuario_id"]
        print(">> Perfil não encontrado. Tente novamente.\n")


def chat_livre(usuario_id):
    print("\n--- Chat Livre com a IA ---")
    print("Peça ajuda para simplificar enunciados, organizar rotinas ou tirar dúvidas.")
    print("Digite 'sair' para voltar ao menu.\n")

    while True:
        pergunta = input("Você: ").strip()
        if pergunta.lower() == "sair":
            break
        if not pergunta:
            continue

        resultado = ia_controller.chat_livre(usuario_id, pergunta)
        if not resultado["sucesso"]:
            print("\n" + resultado["mensagem"])
            continue

        print("\nAssistente:")
        for linha in resultado["respostas"]:
            print(f"- {linha}")
        print("-" * 30)


def main():
    selecao = _selecionar_perfil()
    if selecao is None:
        return
    nome, usuario_id = selecao

    while True:
        print("\n" + "=" * 45)
        print(f"CHAT LIVRE - PERFIL: {nome}".center(45))
        print("=" * 45)
        print("1. Iniciar Chat Livre")
        print("2. Trocar de perfil")
        print("3. Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            chat_livre(usuario_id)
        elif opcao == "2":
            selecao = _selecionar_perfil()
            if selecao is None:
                break
            nome, usuario_id = selecao
        elif opcao == "3":
            print("Até logo!")
            break
        else:
            print(">> Opção inválida.")


if __name__ == "__main__":
    main()
