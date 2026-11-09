# Food Store — TPI Programación II

Sistema de consola para gestionar categorías, productos, usuarios y pedidos,
desarrollado para Programación II de la Universidad Tecnológica Nacional. Los
datos se guardan en memoria durante la ejecución; al cerrar el programa se
pierden.

## Requisitos

- Python 3.12 o superior.
- Dependencias de consola: `questionary` y `colorama`.

Instalación de dependencias:

```powershell
python -m pip install questionary colorama
```

## Ejecución

Desde la carpeta del proyecto:

```powershell
python main.py
```

Para ejecutar las pruebas automatizadas:

```powershell
python pruebas.py
```

## Credenciales de ejemplo

`main.py` carga estos usuarios al iniciar:

- Administrador: `admin@foodstore.com` / `admin123`
- Cliente: `cliente@foodstore.com` / `cliente123`

## Funcionalidades

- Inicio de sesión con límite de tres intentos y menús diferenciados por rol.
- ABM lógico de categorías, productos y usuarios para ADMIN.
- Consulta de categorías, productos disponibles y pedidos propios para USUARIO.
- Creación y administración de pedidos con validación y actualización transaccional
  del stock.
- Conservación del precio unitario histórico de cada detalle de pedido.
- Validaciones y excepciones propias en las entidades y los servicios.

## Organización

- `entidades/`: modelo del dominio y validaciones.
- `servicios/`: colecciones, reglas de negocio y autorización.
- `consola/`: menús de administrador y cliente.
- `enums/`: roles, estados y formas de pago.
- `excepciones/`: excepciones del dominio.
- `main.py`: inicialización y ciclo de sesión.
- `pruebas.py`: pruebas automatizadas con `unittest`.

El ejecutable `FoodStore.exe` también se incluye en la carpeta raíz.

Repositorio: <https://github.com/Isma54/UTN_TPI_Programacion2>

Video demostrativo: pendiente.
