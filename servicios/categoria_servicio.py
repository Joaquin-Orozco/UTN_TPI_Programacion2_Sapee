from entidades.categoria import Categoria
from entidades.producto import Producto
from entidades.usuario import Usuario
from excepciones.food_store_error import (
    DatoInvalidoError,
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from servicios.autorizacion import validar_administrador, validar_rol
from enums.enumerados import Rol


class CategoriaServicio:
    def __init__(self) -> None:
        self.__categorias: list[Categoria] = []

    def listar(self, actor: Usuario) -> list[Categoria]:
        validar_rol(actor, Rol.ADMIN, Rol.USUARIO)
        return [categoria for categoria in self.__categorias if not categoria.eliminado]

    def contiene(self, categoria: Categoria) -> bool:
        return any(registrada is categoria for registrada in self.__categorias)

    def buscar_por_id(self, id_categoria: int, actor: Usuario) -> Categoria:
        validar_administrador(actor)
        for categoria in self.__categorias:
            if id_categoria == categoria.id and not categoria.eliminado:
                return categoria
        raise EntidadNoEncontradaError(
            f"No se encontró la categoría con id: {id_categoria}"
        )

    def crear_categoria(
        self, actor: Usuario, nombre: str, descripcion: str
    ) -> Categoria:
        validar_administrador(actor)
        if not isinstance(nombre, str):
            raise DatoInvalidoError("El nombre de la categoría debe ser texto")
        nombre_limpio = nombre.strip().capitalize()
        for categoria in self.__categorias:
            if nombre_limpio.lower() == categoria.nombre.lower() and not categoria.eliminado:
                raise DuplicadoError(
                    f"Ya existe una categoría con nombre {nombre_limpio}"
                )
        nueva_categoria = Categoria(nombre_limpio, descripcion)
        self.__categorias.append(nueva_categoria)
        return nueva_categoria

    def asociar_producto_a_categoria(
        self, actor: Usuario, id_categoria: int, producto: Producto
    ) -> None:
        validar_administrador(actor)
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("Solo se pueden asociar instancias de Producto")
        categoria = self.buscar_por_id(id_categoria, actor)
        categoria.agregar_producto(producto)
        for existente in self.__categorias:
            if existente is not categoria:
                existente.remover_producto(producto)

    def desasociar_producto_de_categoria(
        self, actor: Usuario, id_categoria: int, producto: Producto
    ) -> None:
        validar_administrador(actor)
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("Solo se pueden desasociar instancias de Producto")
        categoria = self.buscar_por_id(id_categoria, actor)
        if producto not in categoria.productos:
            raise EntidadNoEncontradaError(
                f"El producto {producto.id} no pertenece a la categoría {categoria.nombre}"
            )
        categoria.remover_producto(producto)

    def buscar_categoria_de_producto(
        self, producto: Producto
    ) -> Categoria | None:
        for categoria in self.__categorias:
            if producto in categoria.productos:
                return categoria
        return None

    def contar_activos_por_categoria(
        self, id_categoria: int, actor: Usuario
    ) -> int:
        categoria = self.buscar_por_id(id_categoria, actor)
        return sum(1 for producto in categoria.productos if not producto.eliminado)

    def editar(
        self,
        actor: Usuario,
        id_categoria: int,
        nombre: str | None = None,
        descripcion: str | None = None,
    ) -> Categoria:
        validar_administrador(actor)
        categoria = self.buscar_por_id(id_categoria, actor)
        if nombre is not None:
            if not isinstance(nombre, str):
                raise DatoInvalidoError("El nombre de la categoría debe ser texto")
            if not nombre.strip():
                raise DatoInvalidoError("El nombre de la categoría no puede quedar vacío")
            nombre_limpio = nombre.strip().capitalize()
            for existente in self.__categorias:
                if (
                    id_categoria != existente.id
                    and nombre_limpio.lower() == existente.nombre.lower()
                    and not existente.eliminado
                ):
                    raise DuplicadoError(
                        f"Ya existe una categoría con nombre {nombre_limpio}"
                    )
            categoria.nombre = nombre_limpio
        if descripcion is not None:
            categoria.descripcion = descripcion
        return categoria

    def eliminar(self, actor: Usuario, id_categoria: int) -> None:
        validar_administrador(actor)
        categoria = self.buscar_por_id(id_categoria, actor)
        activos = sum(
            1 for producto in categoria.productos if not producto.eliminado
        )
        if activos:
            raise OperacionNoPermitidaError(
                f"No se puede dar de baja la categoría {categoria.nombre}: "
                f"tiene {activos} producto(s) activo(s)"
            )
        categoria.eliminar()
