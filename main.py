from servicios.categoria_servicio import CategoriaServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio
from servicios.pedido_servicio import PedidoServicio
from enums.enumerados import Rol
from consola.menu import crear_menu
from excepciones.food_store_error import CredencialesInvalidasError
from colorama import Fore,init
from consola.menu import limpiar_consola,continuar
from entidades.usuario import Usuario
import getpass
init(autoreset=True)

def main()->None:
    cat_servicio = CategoriaServicio()
    producto_servicio = ProductoServicio(cat_servicio)
    usuario_servicio = UsuarioServicio()
    usuario_admin = usuario_servicio.crear_administrador_inicial(
        "Ana", "Perez", "admin@foodstore.com", "2615555555", "admin123"
    )
    usuario_servicio.crear_usuario(
        usuario_admin,
        "Juan",
        "Gomez",
        "cliente@foodstore.com",
        "2614444444",
        "cliente123",
        Rol.USUARIO,
    )
    pedido_servicio = PedidoServicio(producto_servicio, usuario_servicio)

    c1 = cat_servicio.crear_categoria(
        usuario_admin, "Hamburguesas", "Hamburguesas completas"
    )
    c2 = cat_servicio.crear_categoria(
        usuario_admin, "Bebidas", "Gaseosas, jugos naturales y aguas"
    )
    producto_servicio.crear_producto(
        usuario_admin,
        c1,
        "Hamburguesa completa",
        8000,
        "Medallón de carne, lechuga, tomate, queso y pan de papa",
        15,
        "",
        True,
    )
    producto_servicio.crear_producto(
        usuario_admin,
        c2,
        "Coca-Cola 1.5L",
        4300,
        "Gaseosa sabor original fría",
        30,
        "",
        True,
    )

    
    while True:
        intentos = 3
        usuario_actual: Usuario | None = None

        while intentos > 0:
            limpiar_consola()
            print("=== BIENVENIDO A FOOD STORE ===")
            print(f"--- INICIO DE SESION (Intentos restantes {intentos}) ---")
            mail = input("Mail: ")
            contrasenia = getpass.getpass("Contraseña: ")

            try:
                usuario_actual = usuario_servicio.autenticar(mail,contrasenia)
                print(Fore.GREEN + f"¡Bienvenido/a, {usuario_actual.nombre} {usuario_actual.apellido} ({usuario_actual.rol.name})!")
                continuar()
                print()
                break
            except CredencialesInvalidasError as e:
                print(Fore.YELLOW + f"! {e}")
                continuar()
                intentos -= 1
                print()

        if usuario_actual is None:
            print(Fore.RED + "Se ha superado el numero maximo de intentos. El programa ha finalizado")
            break

        menu = crear_menu(usuario_actual,cat_servicio,pedido_servicio,producto_servicio,usuario_servicio)
        cerrar_sesion = menu.mostrar()

        if not cerrar_sesion:
            print("Saliendo de Food Store ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()