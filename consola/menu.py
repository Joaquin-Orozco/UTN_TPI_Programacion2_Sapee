from abc import ABC, abstractmethod
from enum import Enum
import os
from typing import TypeVar
import questionary
from entidades.usuario import Usuario
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio

Enumerado = TypeVar("Enumerado", bound=Enum)


class Menu(ABC):
    def __init__(
        self,
        usuario: Usuario,
        cat_servicio: CategoriaServicio,
        ped_servicio: PedidoServicio,
        prod_servicio: ProductoServicio,
        usu_servicio: UsuarioServicio,
    ) -> None:
        self._usuario: Usuario = usuario
        self._cat_servicio: CategoriaServicio = cat_servicio
        self._ped_servicio: PedidoServicio = ped_servicio
        self._prod_servicio: ProductoServicio = prod_servicio
        self._usu_servicio: UsuarioServicio = usu_servicio

    @abstractmethod
    def mostrar(self) -> bool:
        pass


def crear_menu(
    usuario: Usuario,
    cat_servicio: CategoriaServicio,
    ped_servicio: PedidoServicio,
    prod_servicio: ProductoServicio,
    usu_servicio: UsuarioServicio,
) -> Menu:
    from consola.menu_administrador import MenuAdministrador
    from consola.menu_cliente import MenuCliente
    from enums.enumerados import Rol
    if usuario.rol == Rol.ADMIN:
        return MenuAdministrador(
            usuario, cat_servicio, ped_servicio, prod_servicio, usu_servicio
        )
    else:
        return MenuCliente(
            usuario, cat_servicio, ped_servicio, prod_servicio, usu_servicio
        )


def seleccionar_enumerado(
    mensaje: str, enumerado: type[Enumerado]
) -> Enumerado | None:
    opciones = list(enumerado)
    seleccion = questionary.select(
        message=mensaje,
        choices=[f"{indice}. {opcion.name}" for indice, opcion in enumerate(opciones, 1)],
    ).ask()
    if seleccion is None:
        return None
    try:
        indice = int(seleccion.split(".", maxsplit=1)[0]) - 1
    except ValueError:
        return None
    if not 0 <= indice < len(opciones):
        return None
    return opciones[indice]


def limpiar_consola() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def continuar() -> None:
    input("Presione cualquier tecla para continuar ")