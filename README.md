# TPI_Programacion2
Sistema de gestión de pedidos de comida en consola. El programa aplica los conceptos de POO para procesar, validar y organizar el flujo de un comercio de comida rapida mediante el uso de python.<br>
<br>
Universidad Tecnológica Nacional<br>
Cátedra: 1PRO6, Comisión 6, Programacion 2<br>
Alumno: Nahuel Ismael Leyes Moyano<br>
Profesores:Cinthia Vanina Rigoni Guerra, Ariel Edgardo Enferrel<br>
<br>
Credenciales de Acceso<br>
Para iniciar sesion y evaluar el flujo del programa, utilice los siguientes datos precargados:<br>
-Usuario administrador: "admin@foodstore.com"/"admin123"<br>
-Usuario cliente: "cliente@foodstore.com"/"cliente123"<br>
<br>
El desarrollo del programa ha sido dividido en capas con responsabilidades aisladas:<br>
-'main.py': Ejecuta el inicio de sesión además de los respectivos menus<br>
-'pruebas.py': Ejecuta los test automaticos, validando calculos, stock, y la correcta captura de excepciones<br>
-'/entidades': Capa que contiene el modelo del dominio('base.py','calculable.py','categoria.py','producto.py','detalle_pedido.py','pedido.py','usuario.py'). Aplica encapsulamiento y relaciones de asociacion, agregacion y composicion<br>
-'/servicios': Capa encargada de las reglas de negocio aisladas de la consola ('categoria_servicio.py','producto_servicio.py','usuario_servicio.py','pedido_servicio.py')<br>
-'/consola': Capa que contiene las interfaces graficas de la consola mediante menus interactivos ('menu.py','menu_administrador.py','menu_cliente.py')<br>
-'/excepciones' y '/enums': Capas de soporte para tipado seguro y violaciones a las reglas de negocio personalizados bajo la clase padre 'FoodStoreError'<br>
<br>
Archivo ejecutable
En la carpeta "/ejecutable" se encuentran todos los archivos y carpetas de dependencia para que funcione dicho ejecutable. Este mismo tiene un acceso directo a la carpeta raiz con el nombre "FoodStore.exe", su funcionamiento es igual al usarlo en VStudio<br>
<br>
Librerías de terceros: Questionary, Colorama, PyInstaller<br>
GitHub repositorio: https://github.com/Isma54/UTN_TPI_Programacion2<br>
Video Demostración: PENDIENTE
