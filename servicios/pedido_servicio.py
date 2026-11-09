from entidades.pedido import Pedido
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.enumerados import Estado, FormaPago, Rol
from excepciones.food_store_error import (
    DatoInvalidoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    StockInsuficienteError,
)
from servicios.autorizacion import validar_administrador, validar_rol
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


class PedidoServicio:
    def __init__(
        self, producto_servicio: ProductoServicio, usuario_servicio: UsuarioServicio
    ) -> None:
        self.__pedidos: list[Pedido] = []
        self.__producto_servicio = producto_servicio
        self.__usuario_servicio = usuario_servicio

    def listar(self, actor: Usuario) -> list[Pedido]:
        validar_rol(actor, Rol.ADMIN, Rol.USUARIO)
        if actor.rol == Rol.ADMIN:
            return [pedido for pedido in self.__pedidos if not pedido.eliminado]
        return self.listar_por_usuario(actor)

    def listar_por_usuario(self, actor: Usuario) -> list[Pedido]:
        validar_rol(actor, Rol.USUARIO)
        return [
            pedido
            for pedido in self.__pedidos
            if not pedido.eliminado and pedido.usuario.id == actor.id
        ]

    def buscar_por_id(self, id_pedido: int, actor: Usuario) -> Pedido:
        validar_rol(actor, Rol.ADMIN, Rol.USUARIO)
        for pedido in self.__pedidos:
            if pedido.id == id_pedido and not pedido.eliminado:
                if actor.rol == Rol.USUARIO and pedido.usuario.id != actor.id:
                    break
                return pedido
        raise EntidadNoEncontradaError(
            f"No se encontró el pedido con id: {id_pedido}"
        )

    def crear_pedido_con_detalles(
        self,
        actor: Usuario,
        forma_pago: FormaPago,
        usuario: Usuario,
        items: list[tuple[int, Producto]],
    ) -> Pedido:
        validar_administrador(actor)
        if not isinstance(forma_pago, FormaPago):
            raise DatoInvalidoError("La forma de pago no es válida")
        if not isinstance(usuario, Usuario) or usuario.eliminado:
            raise OperacionNoPermitidaError(
                "No se puede crear un pedido con un usuario inexistente o eliminado"
            )
        if not self.__usuario_servicio.contiene(usuario):
            raise EntidadNoEncontradaError("El usuario no está registrado")
        if not isinstance(items, list) or not items:
            raise DatoInvalidoError("El pedido debe contener al menos un producto")

        cantidades: dict[int, tuple[Producto, int]] = {}
        for item in items:
            if not isinstance(item, tuple) or len(item) != 2:
                raise DatoInvalidoError("Cada producto debe incluir cantidad y producto")
            cantidad, producto = item
            if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
                raise DatoInvalidoError("La cantidad debe ser un entero mayor que cero")
            if not isinstance(producto, Producto):
                raise DatoInvalidoError("El producto del pedido no es válido")
            if not self.__producto_servicio.contiene(producto) or producto.eliminado:
                raise EntidadNoEncontradaError(
                    f"El producto {producto.nombre} no existe o fue eliminado"
                )
            if not producto.disponible:
                raise DatoInvalidoError(f"El producto {producto.nombre} no está disponible")
            producto_existente, cantidad_existente = cantidades.get(
                producto.id, (producto, 0)
            )
            if producto_existente is not producto:
                raise DatoInvalidoError("Hay productos distintos con el mismo ID")
            cantidades[producto.id] = (producto, cantidad_existente + cantidad)

        for producto, cantidad in cantidades.values():
            if cantidad > producto.stock:
                raise StockInsuficienteError(
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Disponible: {producto.stock}"
                )

        pedido = Pedido(forma_pago, usuario)
        for producto, cantidad in cantidades.values():
            pedido.agregar_detalle(cantidad, producto)
        pedido.calcular_total()

        stock_anterior = {
            producto.id: (producto, producto.stock, producto.disponible)
            for producto, _ in cantidades.values()
        }
        try:
            for producto, cantidad in cantidades.values():
                producto.stock -= cantidad
            self.__pedidos.append(pedido)
        except Exception:
            for producto, stock, disponible in stock_anterior.values():
                producto.stock = stock
                producto.disponible = disponible
            if pedido in self.__pedidos:
                self.__pedidos.remove(pedido)
            raise

        return pedido

    def cambiar_estado(
        self, actor: Usuario, id_pedido: int, nuevo_estado: Estado
    ) -> Pedido:
        validar_administrador(actor)
        if not isinstance(nuevo_estado, Estado):
            raise DatoInvalidoError("El estado del pedido no es válido")
        pedido = self.buscar_por_id(id_pedido, actor)
        estado_actual = pedido.estado
        if estado_actual == nuevo_estado:
            return pedido

        transiciones = {
            Estado.PENDIENTE: {Estado.CONFIRMADO, Estado.CANCELADO},
            Estado.CONFIRMADO: {Estado.TERMINADO, Estado.CANCELADO},
        }
        if nuevo_estado not in transiciones.get(estado_actual, set()):
            raise OperacionNoPermitidaError(
                f"Transición de estado inválida de {estado_actual.name} a {nuevo_estado.name}"
            )

        if nuevo_estado == Estado.CANCELADO:
            for detalle in pedido.detalles_pedidos:
                detalle.producto.stock += detalle.cantidad
        pedido.estado = nuevo_estado
        return pedido

    def cambiar_forma_pago(
        self, actor: Usuario, id_pedido: int, nueva_forma: FormaPago
    ) -> Pedido:
        validar_administrador(actor)
        pedido = self.buscar_por_id(id_pedido, actor)
        if pedido.estado in {Estado.TERMINADO, Estado.CANCELADO}:
            raise OperacionNoPermitidaError(
                "No se puede modificar la forma de pago de un pedido terminado o cancelado"
            )
        pedido.forma_pago = nueva_forma
        return pedido

    def eliminar(self, actor: Usuario, id_pedido: int) -> None:
        validar_administrador(actor)
        pedido = self.buscar_por_id(id_pedido, actor)
        if pedido.estado not in {Estado.TERMINADO, Estado.CANCELADO}:
            for detalle in pedido.detalles_pedidos:
                detalle.producto.stock += detalle.cantidad
        pedido.eliminar()
        for detalle in pedido.detalles_pedidos:
            detalle.eliminar()
