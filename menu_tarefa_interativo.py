"""
Menu interativo para testar de verdade a camada fatiada de tarefas/passos
(controller -> service -> repository -> MySQL), com entrada de dados
digitada pelo usuário via terminal.

Rode este arquivo na raiz do projeto (mesmo nível do main.py):
    python menu_tarefa_interativo.py

Requer que o MySQL esteja rodando e configurado no .env, e que já exista
pelo menos um perfil de usuário criado (use o menu_usuario_interativo.py).
"""

from datetime import datetime

from controllers.usuario_controller import UsuarioController
from controllers.tarefa_controller import TarefaController
from controllers.ia_controller import IaController

usuario_controller = UsuarioController()
tarefa_controller = TarefaController()
ia_controller = IaController()


# ---------- helpers de entrada validada ----------

def _pedir_titulo():
    while True:
        titulo = input("Título da tarefa: ").strip()
        if titulo:
            return titulo
        print(">> O título não pode ficar vazio.\n")


def _pedir_tipo():
    while True:
        print("Tipo: 1) tarefas_diarias  2) tarefas_educacionais")
        op = input("Opção: ").strip()
        if op == "1":
            return "tarefas_diarias"
        if op == "2":
            return "tarefas_educacionais"
        print(">> Opção inválida. Digite 1 ou 2.\n")


def _pedir_prioridade():
    mapa = {"1": "baixa", "2": "media", "3": "alta"}
    while True:
        print("Prioridade: 1) baixa  2) media  3) alta")
        op = input("Opção: ").strip()
        if op in mapa:
            return mapa[op]
        print(">> Opção inválida. Digite 1, 2 ou 3.\n")


def _pedir_prazo_opcional():
    while True:
        prazo = input("Prazo (DD/MM/AAAA, Enter para não definir): ").strip()
        if prazo == "":
            return ""
        try:
            datetime.strptime(prazo, "%d/%m/%Y")
            return prazo
        except ValueError:
            print(">> Data inválida. Utilize o formato DD/MM/AAAA.\n")


def _pedir_passos():
    print("Digite os passos um por um. Deixe em branco e aperte Enter para terminar.")
    passos = []
    while True:
        passo = input(f"Passo {len(passos) + 1} (ou Enter para terminar): ").strip()
        if passo == "":
            break
        passos.append(passo)
    return passos


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


def _selecionar_tarefa_do_usuario(usuario_id):
    tarefas = tarefa_controller.listar_tarefas(usuario_id)
    if not tarefas:
        print(">> Esse perfil não tem tarefas cadastradas.")
        return None

    print("\nTarefas do perfil:")
    for t in tarefas:
        status = "[X]" if t["concluida"] else "[ ]"
        print(f"{status} {t['tarefa_id']} - {t['titulo']} ({t['prioridade']})")

    while True:
        valor = input("Digite o id da tarefa: ").strip()
        if valor.isdigit() and any(t["tarefa_id"] == int(valor) for t in tarefas):
            return int(valor)
        print(">> Id inválido. Tente novamente.\n")


# ---------- ações do menu ----------

def criar_tarefa(usuario_id):
    print("\n--- Criar tarefa ---")
    titulo = _pedir_titulo()
    descricao = input("Descrição (opcional): ").strip()
    tipo = _pedir_tipo()
    prioridade = _pedir_prioridade()
    prazo = _pedir_prazo_opcional()

    resultado = tarefa_controller.criar_tarefa(usuario_id, tipo, titulo, descricao, prioridade, prazo)
    print("\n" + resultado["mensagem"])


def listar_tarefas(usuario_id):
    print("\n--- Tarefas do perfil ---")
    tarefas = tarefa_controller.listar_tarefas(usuario_id)
    if not tarefas:
        print("(nenhuma tarefa cadastrada ainda)")
    for t in tarefas:
        status = "[X]" if t["concluida"] else "[ ]"
        print(f"\n{status} {t['tarefa_id']}. {t['titulo']} ({t['tipo']}, prioridade={t['prioridade']})")
        if t["descricao"]:
            print("   Descrição:", t["descricao"])
        if t["prazo"]:
            print("   Prazo:", t["prazo"])
        if t["passos"]:
            print("   Passos:")
            for i, p in enumerate(t["passos"], start=1):
                marcador = "✓" if p["concluido"] else " "
                print(f"     {i}. [{marcador}] {p['texto']}")


def definir_passos(usuario_id):
    print("\n--- Definir passos de uma tarefa ---")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return
    passos = _pedir_passos()
    if not passos:
        print(">> Nenhum passo digitado, nada foi alterado.")
        return
    resultado = tarefa_controller.definir_passos_ia(tarefa_id, passos)
    print("\n" + resultado["mensagem"])


def marcar_passo(usuario_id):
    print("\n--- Marcar passo como concluído/pendente ---")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return
    tarefa = tarefa_controller.buscar_tarefa(tarefa_id)
    if not tarefa.get("passos"):
        print(">> Essa tarefa não tem passos definidos.")
        return

    print("\nPassos:")
    for idx, p in enumerate(tarefa["passos"], start=1):
        marcador = "✓" if p["concluido"] else " "
        print(f"{idx}. [{marcador}] {p['texto']}")

    # Para marcar, precisamos do id real do passo no banco
    from repositories.tarefa_repository import TarefaRepository
    tarefa_no_banco = TarefaRepository().buscar_por_id(tarefa_id)

    while True:
        valor = input("Número do passo a alternar: ").strip()
        if valor.isdigit() and 1 <= int(valor) <= len(tarefa_no_banco.passos):
            passo_id = tarefa_no_banco.passos[int(valor) - 1].id
            break
        print(">> Número inválido. Tente novamente.\n")

    resultado = tarefa_controller.alternar_status_passo(passo_id)
    print("\n" + resultado["mensagem"])


def alternar_status_tarefa(usuario_id):
    print("\n--- Marcar tarefa como concluída/pendente ---")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return
    resultado = tarefa_controller.alternar_status_tarefa(tarefa_id)
    print("\n" + resultado["mensagem"])


def editar_tarefa(usuario_id):
    print("\n--- Editar tarefa ---")
    print("(deixe em branco e aperte Enter para não alterar o campo)")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return

    titulo = input("Novo título: ").strip() or None
    descricao = input("Nova descrição: ").strip() or None

    op_prioridade = input("Nova prioridade — 1) baixa  2) media  3) alta  (Enter = não alterar): ").strip()
    prioridade = {"1": "baixa", "2": "media", "3": "alta"}.get(op_prioridade)

    prazo = input("Novo prazo (DD/MM/AAAA, Enter = não alterar): ").strip() or None

    resultado = tarefa_controller.editar_tarefa(tarefa_id, titulo, descricao, prioridade, prazo)
    print("\n" + resultado["mensagem"])


def excluir_tarefa(usuario_id):
    print("\n--- Excluir tarefa ---")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return
    resultado = tarefa_controller.excluir_tarefa(tarefa_id)
    print("\n" + resultado["mensagem"])


def _barra_progresso(concluidos, total, largura=15):
    if total == 0:
        return "[" + "-" * largura + "]", 0
    percentual = round((concluidos / total) * 100)
    preenchido = round((concluidos / total) * largura)
    barra = "[" + "=" * preenchido + "-" * (largura - preenchido) + "]"
    return barra, percentual


def resumo(usuario_id):
    dados = tarefa_controller.resumo_tarefas(usuario_id)

    print("\n" + "=" * 52)
    print("DASHBOARD".center(52))
    print("=" * 52)

    if dados["total"] == 0:
        print("Nenhuma tarefa cadastrada ainda.")
        print("=" * 52)
        input("\nPressione Enter para voltar.")
        return

    barra_geral, pct_geral = _barra_progresso(dados["concluidas"], dados["total"])
    print(f"Progresso geral: {dados['concluidas']}/{dados['total']} tarefas concluídas ({pct_geral}%)")
    print(barra_geral)

    print("\n--- Por tipo ---")
    nomes_tipo = {
        "tarefas_diarias": "Rotina diária",
        "tarefas_educacionais": "Estudos e atividades",
    }
    for tipo, nome in nomes_tipo.items():
        info = dados["por_tipo"].get(tipo, {"total": 0, "concluidas": 0})
        barra, pct = _barra_progresso(info["concluidas"], info["total"])
        print(f"{nome:<22} {barra} {pct}% ({info['concluidas']}/{info['total']})")

    print("\n--- Por prioridade ---")
    nomes_prioridade = {"alta": "Alta", "media": "Média", "baixa": "Baixa"}
    for prioridade, nome in nomes_prioridade.items():
        info = dados["por_prioridade"].get(prioridade, {"total": 0, "concluidas": 0})
        print(f"{nome:<8} {info['total']} tarefa(s) ({info['concluidas']} concluída(s))")

    print("\n--- Atenção ---")
    print(f"Tarefas com prazo vencido: {dados['vencidas']}")

    print("\n--- Passos ---")
    passos = dados["passos"]
    barra_passos, pct_passos = _barra_progresso(passos["concluidos"], passos["total"])
    print(f"Progresso de passos: {passos['concluidos']}/{passos['total']} concluídos ({pct_passos}%)")
    print(barra_passos)

    print("=" * 52)
    input("\nPressione Enter para voltar.")


def desmembrar_com_ia(usuario_id):
    print("\n--- Desmembrar tarefa com IA ---")
    tarefa_id = _selecionar_tarefa_do_usuario(usuario_id)
    if tarefa_id is None:
        return

    while True:
        resultado = ia_controller.sugerir_passos(tarefa_id)
        if not resultado["sucesso"]:
            print("\n" + resultado["mensagem"])
            return

        print("\nPassos sugeridos pela IA:")
        for i, p in enumerate(resultado["passos"], start=1):
            print(f"  {i}. {p}")

        print("\n1. Aceitar sugestão")
        print("2. Gerar novamente")
        print("3. Cancelar")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            confirmacao = tarefa_controller.definir_passos_ia(tarefa_id, resultado["passos"])
            print("\n" + confirmacao["mensagem"])
            return
        elif opcao == "2":
            continue
        else:
            print("\nSugestão descartada. Nenhum passo foi alterado.")
            return


def main():
    selecao = _selecionar_perfil()
    if selecao is None:
        return
    nome, usuario_id = selecao

    while True:
        print("\n" + "=" * 55)
        print(f"TAREFAS DE: {nome}".center(55))
        print("=" * 55)
        print("1. Criar tarefa")
        print("2. Listar tarefas")
        print("3. Definir passos de uma tarefa")
        print("4. Marcar passo como concluído/pendente")
        print("5. Marcar tarefa como concluída/pendente")
        print("6. Editar tarefa")
        print("7. Excluir tarefa")
        print("8. Ver Dashboard")
        print("9. Trocar de perfil")
        print("10. Desmembrar tarefa com IA")
        print("11. Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            criar_tarefa(usuario_id)
        elif opcao == "2":
            listar_tarefas(usuario_id)
        elif opcao == "3":
            definir_passos(usuario_id)
        elif opcao == "4":
            marcar_passo(usuario_id)
        elif opcao == "5":
            alternar_status_tarefa(usuario_id)
        elif opcao == "6":
            editar_tarefa(usuario_id)
        elif opcao == "7":
            excluir_tarefa(usuario_id)
        elif opcao == "8":
            resumo(usuario_id)
        elif opcao == "9":
            selecao = _selecionar_perfil()
            if selecao is None:
                break
            nome, usuario_id = selecao
        elif opcao == "10":
            desmembrar_com_ia(usuario_id)
        elif opcao == "11":
            print("Até logo!")
            break
        else:
            print(">> Opção inválida.")


if __name__ == "__main__":
    main()
