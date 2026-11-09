from entidades.base import Base
from entidades.producto import Producto
from excepciones.food_store_error import DatoInvalidoError

class DetallePedido(Base):
    def __init__(self, cantidad: int, producto: Producto) -> None:
        super().__init__()
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("El producto debe ser una instancia de la clase Producto")
        self.__producto = producto
        self.__nombre_producto = producto.nombre
        self.__precio_unitario = producto.precio
        self.__cantidad: int
        self.__subtotal: float = 0.0
        self.__producto: Producto
        self.__nombre_producto: str
        self.__precio_unitario: float
        self.cantidad = cantidad
        self.actualizar_subtotal()

    @property
    def cantidad(self)->int:
        return self.__cantidad
    @property
    def producto(self)->Producto:
        return self.__producto
    @property
    def subtotal(self)->float:
        return self.__subtotal
    @property
    def precio_unitario(self) -> float:
        return self.__precio_unitario
    @property
    def nombre_producto(self) -> str:
        return self.__nombre_producto

    @cantidad.setter
    def cantidad(self,cantidad:int)->None:
        if not isinstance(cantidad,int) or isinstance(cantidad,bool):
            raise DatoInvalidoError("La cantidad debe ser un numero entero")
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad no puede ser negativa")
        self.__cantidad = cantidad

    def actualizar_subtotal(self)->None:
        self.__subtotal = self.cantidad * self.precio_unitario

    def __str__(self)->str:
        return (
            f"ID: {self.id} | {self.nombre_producto} | Cantidad: {self.cantidad} "
            f"| Precio unitario: ${self.precio_unitario:.2f} | Subtotal: ${self.subtotal:.2f}"
        )
    