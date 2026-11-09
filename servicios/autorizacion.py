from entidades.usuario import Usuario
from enums.enumerados import Rol
from excepciones.food_store_error import OperacionNoPermitidaError


def validar_rol(usuario: Usuario, *roles: Rol) -> None:
    if not isinstance(usuario, Usuario) or usuario.eliminado or usuario.rol not in roles:
        raise OperacionNoPermitidaError("No tiene permisos para realizar esta operación")


def validar_administrador(usuario: Usuario) -> None:
    validar_rol(usuario, Rol.ADMIN)


def validar_cliente(usuario: Usuario) -> None:
    validar_rol(usuario, Rol.USUARIO)
