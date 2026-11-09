from entidades.categoria import Categoria
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.enumerados import Rol
from excepciones.food_store_error import (
    DatoInvalidoError,
    EntidadNoEncontradaError,
    PrecioInvalidoError,
    StockInvalidoError,
)
from servicios.autorizacion import validar_administrador, validar_rol
from servicios.categoria_servicio import CategoriaServicio


class ProductoServicio:
    def __init__(self, categoria_servicio: CategoriaServicio) -> None:
        self.__productos: list[Producto] = []
        self.__categoria_servicio = categoria_servicio

    def crear_producto(
        self,
        actor: Usuario,
        categoria: Categoria,
        nombre: str,
        precio: float,
        descripcion: str,
        stock: int,
        imagen: str,
        disponible: bool,
    ) -> Producto:
        validar_administrador(actor)
        if (
            not isinstance(categoria, Categoria)
            or categoria.eliminado
            or not self.__categoria_servicio.contiene(categoria)
        ):
            raise DatoInvalidoError("La categoría del producto no es válida")
        producto = Producto(nombre, precio, descripcion, stock, imagen, disponible)
        categoria.agregar_producto(producto)
        self.__productos.append(producto)
        return producto

    def listar(self, actor: Usuario) -> list[Producto]:
        validar_administrador(actor)
        return [producto for producto in self.__productos if not producto.eliminado]

    def listar_disponibles_clientes(self, actor: Usuario) -> list[Producto]:
        validar_rol(actor, Rol.ADMIN, Rol.USUARIO)
        return [
            producto
            for producto in self.__productos
            if not producto.eliminado and producto.disponible and producto.stock > 0
        ]

    def buscar_por_id(self, id_producto: int, actor: Usuario) -> Producto:
        validar_administrador(actor)
        for producto in self.__productos:
            if producto.id == id_producto and not producto.eliminado:
                return producto
        raise EntidadNoEncontradaError(
            f"No se encontró el producto con id: {id_producto}"
        )

    def contiene(self, producto: Producto) -> bool:
        return any(registrado is producto for registrado in self.__productos)

    def editar(
        self,
        actor: Usuario,
        id_producto: int,
        nombre: str | None = None,
        precio: float | None = None,
        descripcion: str | None = None,
        stock: int | None = None,
        imagen: str | None = None,
        disponible: bool | None = None,
        categoria: Categoria | None = None,
    ) -> Producto:
        validar_administrador(actor)
        producto = self.buscar_por_id(id_producto, actor)
        if categoria is not None and (
            not isinstance(categoria, Categoria)
            or categoria.eliminado
            or not self.__categoria_servicio.contiene(categoria)
        ):
            raise DatoInvalidoError("La categoría del producto no es válida")
        if nombre is not None and (
            not isinstance(nombre, str) or not nombre.strip()
        ):
            raise DatoInvalidoError("El nombre del producto no puede quedar vacío")
        if precio is not None:
            if not isinstance(precio, (int, float)) or isinstance(precio, bool):
                raise DatoInvalidoError("El precio del producto debe ser un número")
            if precio < 0:
                raise PrecioInvalidoError("El precio del producto no puede ser negativo")
        if descripcion is not None and (
            not isinstance(descripcion, str) or not descripcion.strip()
        ):
            raise DatoInvalidoError("La descripción del producto no puede quedar vacía")
        if stock is not None:
            if not isinstance(stock, int) or isinstance(stock, bool):
                raise DatoInvalidoError("El stock del producto debe ser un entero")
            if stock < 0:
                raise StockInvalidoError("El stock del producto no puede ser negativo")
        if imagen is not None and not isinstance(imagen, str):
            raise DatoInvalidoError("La imagen debe ser una ruta de texto")
        if disponible is not None and not isinstance(disponible, bool):
            raise DatoInvalidoError("La disponibilidad debe ser un booleano")
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        if descripcion is not None:
            producto.descripcion = descripcion
        if stock is not None:
            producto.stock = stock
        if imagen is not None:
            producto.imagen = imagen
        if disponible is not None:
            producto.disponible = disponible
        if categoria is not None:
            categoria.agregar_producto(producto)
        return producto

    def eliminar(self, actor: Usuario, id_producto: int) -> None:
        validar_administrador(actor)
        producto = self.buscar_por_id(id_producto, actor)
        producto.eliminar()
