from entidades.base import Base
from entidades.producto import Producto
from excepciones.food_store_error import DatoInvalidoError

class DetallePedido(Base):
    def __init__(self,cantidad:int,producto:Producto):
        super().__init__()
        self.cantidad = cantidad
        self.__subtotal = 0.0
        self.producto = producto

    @property
    def cantidad(self)->int:
        return self.__cantidad
    @property
    def producto(self)->Producto:
        return self.__producto
    @property
    def subtotal(self)->float:
        return self.__subtotal

    @cantidad.setter
    def cantidad(self,cantidad:int)->None:
        if not isinstance(cantidad,int) or isinstance(cantidad,bool):
            raise DatoInvalidoError("La cantidad debe ser un numero entero")
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad no puede ser negativa")
        self.__cantidad = cantidad

    @producto.setter
    def producto(self,producto:Producto)->None:
        if not isinstance(producto,Producto):
            raise DatoInvalidoError("El producto debe ser una instancia de la clase Producto")
        self.__producto = producto
        self.actualizar_subtotal()

    def actualizar_subtotal(self)->None:
        self.__subtotal = self.cantidad * self.producto.precio

    def __str__(self)->str:
        return f"ID: {self.id} | {self.producto.nombre} | Cantidad: {self.cantidad} | Subtotal: ${self.__subtotal}"
    