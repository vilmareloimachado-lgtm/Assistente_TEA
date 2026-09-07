from controllers.usuario_controller import UsuarioController

controller = UsuarioController()

# Remove um teste anterior, se existir
controller.excluir_perfil("EXEMPLO_CONTROLLER")

# Criar
resultado = controller.criar_perfil(
    "EXEMPLO CONTROLLER",
    "direto",
    "Leve",
    "25/09/1990",
    "123456"
)
print("CRIAR:", resultado)

# Buscar
resultado = controller.buscar_perfil("EXEMPLO CONTROLLER")
print("BUSCAR:", resultado)

# Excluir
resultado = controller.excluir_perfil("EXEMPLO CONTROLLER")
print("EXCLUIR:", resultado)

# Buscar de novo — agora deve dar "não encontrado"
resultado = controller.buscar_perfil("EXEMPLO CONTROLLER")
print("BUSCAR APOS EXCLUSAO:", resultado)


