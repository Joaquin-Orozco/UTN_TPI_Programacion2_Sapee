import unittest

from entidades.base import Base
from entidades.pedido import Pedido
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.enumerados import Estado, FormaPago, Rol
from excepciones.food_store_error import (
    CredencialesInvalidasError,
    DatoInvalidoError,
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    PrecioInvalidoError,
    StockInvalidoError,
    StockInsuficienteError,
)
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


class FoodStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.categorias = CategoriaServicio()
        self.productos = ProductoServicio(self.categorias)
        self.usuarios = UsuarioServicio()
        self.admin = self.usuarios.crear_administrador_inicial(
            "Ana", "Admin", "admin@example.com", "111", "admin123"
        )
        self.cliente = self.usuarios.crear_usuario(
            self.admin,
            "Juan",
            "Cliente",
            "juan@example.com",
            "222",
            "client123",
            Rol.USUARIO,
        )
        self.otro_cliente = self.usuarios.crear_usuario(
            self.admin,
            "Eva",
            "Otra",
            "eva@example.com",
            "333",
            "client123",
            Rol.USUARIO,
        )
        self.pedidos = PedidoServicio(self.productos, self.usuarios)
        self.categoria = self.categorias.crear_categoria(
            self.admin, "Comidas", "Comidas principales"
        )
        self.producto = self.productos.crear_producto(
            self.admin,
            self.categoria,
            "Hamburguesa",
            1000,
            "Con queso",
            10,
            "hamburguesa.png",
            True,
        )

    def crear_producto(
        self,
        nombre: str,
        stock: int = 10,
        disponible: bool = True,
        precio: float = 1000,
    ) -> Producto:
        return self.productos.crear_producto(
            self.admin,
            self.categoria,
            nombre,
            precio,
            "Producto de prueba",
            stock,
            "",
            disponible,
        )

    def crear_pedido(
        self, productos: list[tuple[int, Producto]] | None = None
    ) -> Pedido:
        return self.pedidos.crear_pedido_con_detalles(
            self.admin,
            FormaPago.EFECTIVO,
            self.cliente,
            productos if productos is not None else [(2, self.producto)],
        )

    def test_base_is_abstract_and_ids_are_shared(self) -> None:
        with self.assertRaises(TypeError):
            Base()
        self.assertNotEqual(self.admin.id, self.producto.id)
        self.assertIsNotNone(self.producto.creado_en)

    def test_category_create_duplicate_edit_and_logical_delete(self) -> None:
        with self.assertRaises(DuplicadoError):
            self.categorias.crear_categoria(self.admin, "COMIDAS", "Duplicada")
        self.categorias.editar(
            self.admin, self.categoria.id, descripcion="Actualizada"
        )
        self.assertEqual(self.categoria.descripcion, "Actualizada")
        with self.assertRaises(OperacionNoPermitidaError):
            self.categorias.eliminar(self.admin, self.categoria.id)
        self.productos.eliminar(self.admin, self.producto.id)
        self.categorias.eliminar(self.admin, self.categoria.id)
        self.assertEqual(self.categorias.listar(self.admin), [])

    def test_category_association_moves_product_without_stale_links(self) -> None:
        otra = self.categorias.crear_categoria(self.admin, "Postres", "Dulces")
        self.categorias.asociar_producto_a_categoria(
            self.admin, otra.id, self.producto
        )
        self.assertIs(
            self.categorias.buscar_categoria_de_producto(self.producto), otra
        )
        self.assertNotIn(self.producto, self.categoria.productos)
        self.assertIn(self.producto, otra.productos)
        self.assertFalse(hasattr(self.producto, "categoria"))
        self.assertFalse(hasattr(self.producto, "_Producto__categoria"))

    def test_category_service_can_disassociate_product(self) -> None:
        self.categorias.desasociar_producto_de_categoria(
            self.admin, self.categoria.id, self.producto
        )
        self.assertNotIn(self.producto, self.categoria.productos)
        self.assertIsNone(self.categorias.buscar_categoria_de_producto(self.producto))

    def test_product_edit_includes_image_and_category(self) -> None:
        otra = self.categorias.crear_categoria(self.admin, "Bebidas", "Bebidas")
        self.productos.editar(
            self.admin,
            self.producto.id,
            imagen="nueva.png",
            categoria=otra,
        )
        self.assertEqual(self.producto.imagen, "nueva.png")
        self.assertIs(
            self.categorias.buscar_categoria_de_producto(self.producto), otra
        )
        self.assertNotIn("Bebidas", str(self.producto))

    def test_invalid_product_edit_does_not_partially_update(self) -> None:
        with self.assertRaises(PrecioInvalidoError):
            self.productos.editar(
                self.admin, self.producto.id, nombre="Cambio parcial", precio=-1
            )
        self.assertEqual(self.producto.nombre, "Hamburguesa")
        self.assertEqual(self.producto.precio, 1000)

    def test_product_service_lists_active_catalog_and_available_products(self) -> None:
        sin_stock = self.crear_producto("Agotado", stock=0)
        no_disponible = self.crear_producto("Pausado", disponible=False)
        self.assertEqual(
            self.productos.listar(self.admin),
            [self.producto, sin_stock, no_disponible],
        )
        self.assertEqual(
            self.productos.listar_disponibles_clientes(self.cliente),
            [self.producto],
        )

    def test_product_invalid_price_and_stock_are_rejected(self) -> None:
        with self.assertRaises(PrecioInvalidoError):
            self.producto.precio = -1
        with self.assertRaises(StockInvalidoError):
            self.producto.stock = -1

    def test_deleted_products_are_hidden_and_not_orderable(self) -> None:
        self.productos.eliminar(self.admin, self.producto.id)
        self.assertEqual(self.productos.listar(self.admin), [])
        with self.assertRaises(EntidadNoEncontradaError):
            self.crear_pedido()

    def test_user_authentication_duplicates_and_self_delete(self) -> None:
        self.assertIs(
            self.usuarios.autenticar("JUAN@example.com", "client123"),
            self.cliente,
        )
        with self.assertRaises(CredencialesInvalidasError):
            self.usuarios.autenticar("juan@example.com", "wrong")
        with self.assertRaises(DuplicadoError):
            self.usuarios.crear_usuario(
                self.admin,
                "Otro",
                "Usuario",
                "JUAN@example.com",
                "444",
                "password",
                Rol.USUARIO,
            )
        with self.assertRaises(OperacionNoPermitidaError):
            self.usuarios.eliminar(self.admin, self.admin.id)

    def test_user_can_be_created_and_edited_by_admin(self) -> None:
        creado = self.usuarios.crear_usuario(
            self.admin,
            "Nuevo",
            "Cliente",
            "nuevo@example.com",
            "555",
            "secret",
            Rol.USUARIO,
        )
        self.usuarios.editar(
            self.admin,
            creado.id,
            nombre="Actualizado",
            mail="actualizado@example.com",
        )
        self.assertEqual(creado.nombre, "Actualizado")
        self.assertEqual(creado.mail, "actualizado@example.com")
        self.assertIs(
            self.usuarios.autenticar("actualizado@example.com", "secret"), creado
        )
        with self.assertRaises(DuplicadoError):
            self.usuarios.editar(
                self.admin, creado.id, mail=self.cliente.mail
            )
        self.assertEqual(creado.nombre, "Actualizado")

    def test_admin_cannot_remove_own_role_during_session(self) -> None:
        with self.assertRaises(OperacionNoPermitidaError):
            self.usuarios.editar(self.admin, self.admin.id, rol=Rol.USUARIO)
        self.assertEqual(self.admin.rol, Rol.ADMIN)

    def test_deleted_user_cannot_authenticate_or_be_used_in_order(self) -> None:
        self.usuarios.eliminar(self.admin, self.cliente.id)
        with self.assertRaises(CredencialesInvalidasError):
            self.usuarios.autenticar("juan@example.com", "client123")
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedidos.crear_pedido_con_detalles(
                self.admin,
                FormaPago.EFECTIVO,
                self.cliente,
                [(1, self.producto)],
            )

    def test_non_admin_cannot_mutate_services(self) -> None:
        with self.assertRaises(OperacionNoPermitidaError):
            self.categorias.crear_categoria(
                self.cliente, "No permitido", "No permitido"
            )
        with self.assertRaises(OperacionNoPermitidaError):
            self.productos.eliminar(self.cliente, self.producto.id)
        with self.assertRaises(OperacionNoPermitidaError):
            self.usuarios.crear_usuario(
                self.cliente,
                "No",
                "Admin",
                "no@example.com",
                "555",
                "password",
                Rol.USUARIO,
            )
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedidos.crear_pedido_con_detalles(
                self.cliente,
                FormaPago.EFECTIVO,
                self.cliente,
                [(1, self.producto)],
            )

    def test_repeated_products_are_accumulated_and_stock_changes_once(self) -> None:
        pedido = self.crear_pedido([(2, self.producto), (3, self.producto)])
        self.assertEqual(len(pedido.detalles_pedidos), 1)
        self.assertEqual(pedido.detalles_pedidos[0].cantidad, 5)
        self.assertEqual(pedido.total, 5000)
        self.assertEqual(self.producto.stock, 5)

    def test_insufficient_duplicate_product_leaves_all_stock_unchanged(self) -> None:
        with self.assertRaises(StockInsuficienteError):
            self.crear_pedido([(6, self.producto), (5, self.producto)])
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.pedidos.listar(self.admin), [])

    def test_insufficient_later_product_does_not_discount_first_product(self) -> None:
        second = self.crear_producto("Segundo producto", stock=1)
        with self.assertRaises(StockInsuficienteError):
            self.crear_pedido([(2, self.producto), (2, second)])
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(second.stock, 1)
        self.assertEqual(self.pedidos.listar(self.admin), [])

    def test_failure_on_later_unavailable_product_is_atomic(self) -> None:
        no_disponible = self.crear_producto("No disponible", disponible=False)
        with self.assertRaises(DatoInvalidoError):
            self.crear_pedido([(2, self.producto), (1, no_disponible)])
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(no_disponible.stock, 10)
        self.assertEqual(self.pedidos.listar(self.admin), [])

    def test_invalid_quantity_does_not_change_stock(self) -> None:
        with self.assertRaises(DatoInvalidoError):
            self.crear_pedido([(0, self.producto)])
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.pedidos.listar(self.admin), [])

    def test_unregistered_user_or_product_is_rejected(self) -> None:
        externo = Producto("Externo", 1, "Externo", 3, "", True)
        with self.assertRaises(EntidadNoEncontradaError):
            self.crear_pedido([(1, externo)])
        usuario_externo = Usuario(
            "Externo", "Usuario", "ext@example.com", "999", "password", Rol.USUARIO
        )
        with self.assertRaises(EntidadNoEncontradaError):
            self.pedidos.crear_pedido_con_detalles(
                self.admin,
                FormaPago.EFECTIVO,
                usuario_externo,
                [(1, self.producto)],
            )

    def test_order_keeps_historical_unit_price_after_catalog_edit(self) -> None:
        pedido = self.crear_pedido([(2, self.producto)])
        self.producto.precio = 2500
        pedido.calcular_total()
        self.assertEqual(pedido.detalles_pedidos[0].precio_unitario, 1000)
        self.assertEqual(pedido.detalles_pedidos[0].subtotal, 2000)
        self.assertEqual(pedido.total, 2000)

    def test_client_can_only_list_and_read_own_orders(self) -> None:
        propio = self.crear_pedido()
        otro_producto = self.crear_producto("Otra comida")
        otro = self.pedidos.crear_pedido_con_detalles(
            self.admin, FormaPago.TARJETA, self.otro_cliente, [(1, otro_producto)]
        )
        self.assertEqual(self.pedidos.listar(self.cliente), [propio])
        with self.assertRaises(EntidadNoEncontradaError):
            self.pedidos.buscar_por_id(otro.id, self.cliente)

    def test_cancel_and_delete_return_stock_exactly_once(self) -> None:
        pedido = self.crear_pedido([(3, self.producto)])
        self.assertEqual(self.producto.stock, 7)
        self.pedidos.cambiar_estado(
            self.admin, pedido.id, Estado.CANCELADO
        )
        self.assertEqual(self.producto.stock, 10)
        self.pedidos.cambiar_estado(
            self.admin, pedido.id, Estado.CANCELADO
        )
        self.pedidos.eliminar(self.admin, pedido.id)
        self.assertEqual(self.producto.stock, 10)
        self.assertTrue(pedido.eliminado)
        self.assertTrue(pedido.detalles_pedidos[0].eliminado)

    def test_deleting_nonterminal_order_returns_stock_once(self) -> None:
        pedido = self.crear_pedido()
        self.assertEqual(self.producto.stock, 8)
        self.pedidos.eliminar(self.admin, pedido.id)
        self.assertEqual(self.producto.stock, 10)

    def test_valid_state_transitions_and_terminal_states(self) -> None:
        pedido = self.crear_pedido()
        self.pedidos.cambiar_estado(
            self.admin, pedido.id, Estado.CONFIRMADO
        )
        self.pedidos.cambiar_estado(self.admin, pedido.id, Estado.TERMINADO)
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedidos.cambiar_estado(
                self.admin, pedido.id, Estado.CANCELADO
            )
        self.assertEqual(self.producto.stock, 8)

    def test_admin_can_change_payment_and_cancel_pending_order(self) -> None:
        pedido = self.crear_pedido()
        self.pedidos.cambiar_forma_pago(
            self.admin, pedido.id, FormaPago.TRANSFERENCIA
        )
        self.assertEqual(pedido.forma_pago, FormaPago.TRANSFERENCIA)
        self.pedidos.cambiar_estado(
            self.admin, pedido.id, Estado.CANCELADO
        )
        self.assertEqual(self.producto.stock, 10)
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedidos.cambiar_forma_pago(
                self.admin, pedido.id, FormaPago.TARJETA
            )

    def test_user_cannot_list_all_users(self) -> None:
        with self.assertRaises(OperacionNoPermitidaError):
            self.usuarios.listar(self.cliente)


if __name__ == "__main__":
    unittest.main(verbosity=2)
