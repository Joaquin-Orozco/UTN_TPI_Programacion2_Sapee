from entidades.usuario import Usuario
from enums.enumerados import Rol
from excepciones.food_store_error import (
    CredencialesInvalidasError,
    DatoInvalidoError,
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from servicios.autorizacion import validar_administrador


class UsuarioServicio:
    def __init__(self) -> None:
        self.__usuarios: list[Usuario] = []

    def crear_administrador_inicial(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
    ) -> Usuario:
        if self.__usuarios:
            raise OperacionNoPermitidaError(
                "El administrador inicial solo puede crearse al iniciar el sistema"
            )
        return self.__crear_usuario(
            nombre, apellido, mail, celular, contrasenia, Rol.ADMIN
        )

    def listar(self, actor: Usuario) -> list[Usuario]:
        validar_administrador(actor)
        return [usuario for usuario in self.__usuarios if not usuario.eliminado]

    def buscar_por_id(self, id_usuario: int, actor: Usuario) -> Usuario:
        validar_administrador(actor)
        for usuario in self.__usuarios:
            if id_usuario == usuario.id and not usuario.eliminado:
                return usuario
        raise EntidadNoEncontradaError(
            f"No se encontró el usuario con id: {id_usuario}"
        )

    def crear_usuario(
        self,
        actor: Usuario,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> Usuario:
        validar_administrador(actor)
        return self.__crear_usuario(nombre, apellido, mail, celular, contrasenia, rol)

    def __crear_usuario(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> Usuario:
        if not isinstance(mail, str):
            raise DatoInvalidoError("El mail debe ser texto")
        mail_limpio = mail.strip().lower()
        for usuario in self.__usuarios:
            if mail_limpio == usuario.mail and not usuario.eliminado:
                raise DuplicadoError("El mail ingresado ya se encuentra registrado")
        usuario = Usuario(nombre, apellido, mail_limpio, celular, contrasenia, rol)
        self.__usuarios.append(usuario)
        return usuario

    def contiene(self, usuario: Usuario) -> bool:
        return any(registrado is usuario for registrado in self.__usuarios)

    def autenticar(self, mail: str, contrasenia: str) -> Usuario:
        if not isinstance(mail, str) or not isinstance(contrasenia, str):
            raise CredencialesInvalidasError("Mail o contraseña incorrectos")
        mail_limpio = mail.strip().lower()
        for usuario in self.__usuarios:
            if mail_limpio == usuario.mail and not usuario.eliminado:
                if usuario.verificar_contrasenia(contrasenia):
                    return usuario
        raise CredencialesInvalidasError("Mail o contraseña incorrectos")

    def editar(
        self,
        actor: Usuario,
        id_usuario: int,
        nombre: str | None = None,
        apellido: str | None = None,
        mail: str | None = None,
        celular: str | None = None,
        contrasenia: str | None = None,
        rol: Rol | None = None,
    ) -> Usuario:
        validar_administrador(actor)
        usuario = self.buscar_por_id(id_usuario, actor)
        if id_usuario == actor.id and rol is not None and rol != Rol.ADMIN:
            raise OperacionNoPermitidaError(
                "Un administrador no puede quitarse el rol mientras tiene la sesión iniciada"
            )
        self.__validar_edicion(nombre, apellido, mail, celular, contrasenia, rol)
        mail_limpio: str | None = None
        if mail is not None:
            mail_limpio = mail.strip().lower()
            for existente in self.__usuarios:
                if (
                    id_usuario != existente.id
                    and mail_limpio == existente.mail
                    and not existente.eliminado
                ):
                    raise DuplicadoError("El mail ya pertenece a otro usuario")
        if nombre is not None:
            usuario.nombre = nombre
        if apellido is not None:
            usuario.apellido = apellido
        if mail_limpio is not None:
            usuario.mail = mail_limpio
        if celular is not None:
            usuario.celular = celular
        if contrasenia is not None:
            usuario.actualizar_contrasenia(contrasenia)
        if rol is not None:
            usuario.rol = rol
        return usuario

    @staticmethod
    def __validar_edicion(
        nombre: str | None,
        apellido: str | None,
        mail: str | None,
        celular: str | None,
        contrasenia: str | None,
        rol: Rol | None,
    ) -> None:
        for campo, valor in (
            ("nombre", nombre),
            ("apellido", apellido),
            ("mail", mail),
            ("celular", celular),
        ):
            if valor is not None and (
                not isinstance(valor, str) or not valor.strip()
            ):
                raise DatoInvalidoError(f"El {campo} no puede estar vacío")
        if mail is not None and ("@" not in mail or "." not in mail):
            raise DatoInvalidoError("El mail ingresado no tiene un formato válido")
        if contrasenia is not None and (
            not isinstance(contrasenia, str) or len(contrasenia.strip()) < 3
        ):
            raise DatoInvalidoError("La contraseña es muy corta")
        if rol is not None and not isinstance(rol, Rol):
            raise DatoInvalidoError("El rol del usuario no es válido")

    def eliminar(self, actor: Usuario, id_usuario: int) -> None:
        validar_administrador(actor)
        usuario = self.buscar_por_id(id_usuario, actor)
        if usuario.id == actor.id:
            raise OperacionNoPermitidaError(
                "Un administrador no puede eliminarse a sí mismo mientras tiene su sesión iniciada"
            )
        usuario.eliminar()
