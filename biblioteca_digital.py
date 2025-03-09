import json
import os

class Libro:
    def __init__(self, titulo, autor, categoria, isbn):
        # Almacena título y autor en una tupla para mantenerlos inmutables
        self.info = (titulo, autor)
        self.categoria = categoria
        self.isbn = isbn

    def __str__(self):
        return f"ISBN: {self.isbn} | Título: {self.info[0]} | Autor: {self.info[1]} | Categoría: {self.categoria}"


class Usuario:
    def __init__(self, nombre, id_usuario):
        self.nombre = nombre
        self.id_usuario = id_usuario
        # Lista de libros actualmente prestados (objetos Libro)
        self.libros_prestados = []
        # Multa acumulada (en dólares)
        self.multa = 0.0

    def __str__(self):
        libros = [libro.info[0] for libro in self.libros_prestados]
        multa_str = f" | Multa: ${self.multa:.2f}" if self.multa > 0 else ""
        return f"ID: {self.id_usuario} | Nombre: {self.nombre} | Libros Prestados: {libros if libros else 'Ninguno'}{multa_str}"


class Biblioteca:
    def __init__(self, archivo_estado="biblioteca_data.json"):
        # Diccionario para almacenar libros: clave = ISBN, valor = objeto Libro
        self.libros = {}
        # Diccionario para almacenar usuarios: clave = ID, valor = objeto Usuario
        self.usuarios = {}
        # Conjunto para asegurar IDs de usuario únicos
        self.ids_usuarios = set()
        self.archivo_estado = archivo_estado
        # Cargar el estado desde el archivo JSON (si existe)
        self.cargar_estado()

    def cargar_estado(self):
        """Carga el estado de la biblioteca desde un archivo JSON si existe."""
        if os.path.exists(self.archivo_estado):
            try:
                with open(self.archivo_estado, "r") as f:
                    estado = json.load(f)
                # Cargar libros
                for isbn, libro_data in estado.get("libros", {}).items():
                    libro = Libro(
                        libro_data["info"][0],
                        libro_data["info"][1],
                        libro_data["categoria"],
                        libro_data["isbn"]
                    )
                    self.libros[isbn] = libro
                # Cargar usuarios
                for id_usuario, usuario_data in estado.get("usuarios", {}).items():
                    usuario = Usuario(
                        usuario_data["nombre"],
                        usuario_data["id_usuario"]
                    )
                    for libro_data in usuario_data.get("libros_prestados", []):
                        libro = Libro(
                            libro_data["info"][0],
                            libro_data["info"][1],
                            libro_data["categoria"],
                            libro_data["isbn"]
                        )
                        usuario.libros_prestados.append(libro)
                    usuario.multa = usuario_data["multa"]
                    self.usuarios[id_usuario] = usuario
                    self.ids_usuarios.add(id_usuario)
                print(f"[INFO] Estado cargado desde '{self.archivo_estado}'.")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar el estado: {e}")
        else:
            print(f"[INFO] No se encontró el archivo '{self.archivo_estado}'. Se iniciará con un estado vacío.")

    # Métodos de Libros
    def agregar_libro(self, libro):
        if libro.isbn in self.libros:
            return f"[ERROR] El libro con ISBN {libro.isbn} ya existe."
        self.libros[libro.isbn] = libro
        return f"[OK] ¡El libro '{libro.info[0]}' ha sido agregado exitosamente!"

    def quitar_libro(self, isbn):
        if isbn in self.libros:
            del self.libros[isbn]
            return f"[OK] El libro con ISBN {isbn} ha sido eliminado."
        return f"[ERROR] No se encontró el libro con ISBN {isbn}."

    # Métodos de Usuarios
    def registrar_usuario(self, usuario):
        if usuario.id_usuario in self.ids_usuarios:
            return f"[ERROR] El ID de usuario {usuario.id_usuario} ya está registrado."
        self.usuarios[usuario.id_usuario] = usuario
        self.ids_usuarios.add(usuario.id_usuario)
        return f"[OK] ¡Bienvenido, {usuario.nombre}! Usuario registrado con éxito."

    def dar_de_baja_usuario(self, id_usuario):
        if id_usuario in self.usuarios:
            nombre = self.usuarios[id_usuario].nombre
            del self.usuarios[id_usuario]
            self.ids_usuarios.discard(id_usuario)
            return f"[OK] El usuario {nombre} (ID {id_usuario}) ha sido dado de baja."
        return f"[ERROR] Usuario con ID {id_usuario} no encontrado."

    # Métodos de Préstamos
    def prestar_libro(self, isbn, id_usuario):
        if isbn not in self.libros:
            return f"[ERROR] Libro con ISBN {isbn} no encontrado."
        if id_usuario not in self.usuarios:
            return f"[ERROR] Usuario con ID {id_usuario} no registrado."
        libro = self.libros[isbn]
        usuario = self.usuarios[id_usuario]
        if libro in usuario.libros_prestados:
            return f"[ERROR] {usuario.nombre} ya tiene prestado este libro."
        usuario.libros_prestados.append(libro)
        return f"[OK] ¡El libro '{libro.info[0]}' ha sido prestado a {usuario.nombre}!"

    def devolver_libro(self, isbn, id_usuario):
        if id_usuario not in self.usuarios:
            return f"[ERROR] Usuario con ID {id_usuario} no registrado."
        usuario = self.usuarios[id_usuario]
        for libro in usuario.libros_prestados:
            if libro.isbn == isbn:
                usuario.libros_prestados.remove(libro)
                return f"[OK] El libro '{libro.info[0]}' ha sido devuelto por {usuario.nombre}."
        return f"[ERROR] {usuario.nombre} no tiene prestado el libro con ISBN {isbn}."

    # Métodos de Búsqueda y Listado
    def buscar_libros(self, criterio, valor):
        resultados = []
        valor = valor.lower()
        for libro in self.libros.values():
            if criterio == "titulo" and valor in libro.info[0].lower():
                resultados.append(libro)
            elif criterio == "autor" and valor in libro.info[1].lower():
                resultados.append(libro)
            elif criterio == "categoria" and valor in libro.categoria.lower():
                resultados.append(libro)
        return resultados

    def listar_libros_prestados(self, id_usuario):
        if id_usuario not in self.usuarios:
            return f"[ERROR] Usuario con ID {id_usuario} no encontrado."
        usuario = self.usuarios[id_usuario]
        if not usuario.libros_prestados:
            return "[INFO] El usuario no tiene libros prestados."
        return "\n".join(str(libro) for libro in usuario.libros_prestados)

    # Métodos de Multas
    def ingresar_multa(self, id_usuario, monto):
        if id_usuario not in self.usuarios:
            return "[ERROR] Usuario no encontrado."
        try:
            monto = monto.replace(',', '.')
            monto = float(monto)
            if monto < 0:
                return "[ERROR] El monto de multa no puede ser negativo."
            self.usuarios[id_usuario].multa += monto
            return (f"[OK] Se ha ingresado una multa de ${monto:.2f} para {self.usuarios[id_usuario].nombre}. "
                    f"Multa total: ${self.usuarios[id_usuario].multa:.2f}")
        except ValueError:
            return "[ERROR] Monto de multa inválido."

    def pagar_multa(self, id_usuario, monto):
        if id_usuario not in self.usuarios:
            return "[ERROR] Usuario no encontrado."
        try:
            monto = monto.replace(',', '.')
            monto = float(monto)
            if monto < 0:
                return "[ERROR] El monto de pago no puede ser negativo."
            usuario = self.usuarios[id_usuario]
            if monto >= usuario.multa:
                usuario.multa = 0.0
                return f"[OK] La multa de {usuario.nombre} ha sido pagada completamente."
            else:
                usuario.multa -= monto
                return (f"[OK] Se ha pagado ${monto:.2f}. "
                        f"Saldo de multa de {usuario.nombre}: ${usuario.multa:.2f}")
        except ValueError:
            return "[ERROR] Monto de pago inválido."

    def consultar_multa(self, id_usuario):
        if id_usuario not in self.usuarios:
            return "[ERROR] Usuario no encontrado."
        usuario = self.usuarios[id_usuario]
        return f"[INFO] El usuario {usuario.nombre} tiene una multa de ${usuario.multa:.2f}"


def submenu_multas(biblioteca):
    while True:
        print("\n--- Gestión de Multas ---")
        print("1. Ingresar multa")
        print("2. Pagar multa")
        print("3. Consultar multa")
        print("4. Regresar al menú principal")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            id_usuario = input("Ingrese el ID del usuario: ")
            monto = input("Ingrese el monto de la multa (por ejemplo, 5,25): ")
            print(biblioteca.ingresar_multa(id_usuario, monto))
        elif opcion == "2":
            id_usuario = input("Ingrese el ID del usuario: ")
            monto = input("Ingrese el monto a pagar (por ejemplo, 2,50): ")
            print(biblioteca.pagar_multa(id_usuario, monto))
        elif opcion == "3":
            id_usuario = input("Ingrese el ID del usuario: ")
            print(biblioteca.consultar_multa(id_usuario))
        elif opcion == "4":
            return  # Regresa al menú principal
        elif opcion == "5":
            print("¡Gracias por usar el sistema! Hasta pronto.")
            exit(0)
        else:
            print("[ERROR] Opción no válida. Por favor, intente de nuevo.")


def exportar_estado(biblioteca, nombre_archivo="biblioteca_data.json"):
    """Exporta el estado actual de la biblioteca a un archivo JSON."""
    estado = {
        "libros": {},
        "usuarios": {}
    }
    for isbn, libro in biblioteca.libros.items():
        estado["libros"][isbn] = {
            "info": list(libro.info),
            "categoria": libro.categoria,
            "isbn": libro.isbn
        }
    for id_usuario, usuario in biblioteca.usuarios.items():
        estado["usuarios"][id_usuario] = {
            "nombre": usuario.nombre,
            "id_usuario": usuario.id_usuario,
            "libros_prestados": [
                {
                    "info": list(libro.info),
                    "categoria": libro.categoria,
                    "isbn": libro.isbn
                } for libro in usuario.libros_prestados
            ],
            "multa": usuario.multa
        }
    try:
        with open(nombre_archivo, "w") as f:
            json.dump(estado, f, indent=4)
        print(f"[INFO] Estado de la biblioteca exportado en '{nombre_archivo}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo exportar el estado: {e}")


def menu():
    biblioteca = Biblioteca()
    print("¡Bienvenido al sistema de gestión de la Biblioteca Digital!")
    print("A continuación, elija una de las opciones de lo que desea hacer.")
    while True:
        print("\n--- Menú Principal ---")
        print("1. Añadir libro")
        print("2. Quitar libro")
        print("3. Registrar usuario")
        print("4. Dar de baja usuario")
        print("5. Prestar libro")
        print("6. Devolver libro")
        print("7. Buscar libros")
        print("8. Listar libros prestados por usuario")
        print("9. Mostrar todos los libros")
        print("10. Mostrar todos los usuarios")
        print("11. Gestionar multas")
        print("12. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            titulo = input("Ingrese el título del libro: ")
            autor = input("Ingrese el autor del libro: ")
            categoria = input("Ingrese la categoría: ")
            isbn = input("Ingrese el ISBN: ")
            libro = Libro(titulo, autor, categoria, isbn)
            print(biblioteca.agregar_libro(libro))
        elif opcion == "2":
            isbn = input("Ingrese el ISBN del libro a quitar: ")
            print(biblioteca.quitar_libro(isbn))
        elif opcion == "3":
            nombre = input("Ingrese el nombre del usuario: ")
            id_usuario = input("Ingrese el ID del usuario: ")
            usuario = Usuario(nombre, id_usuario)
            print(biblioteca.registrar_usuario(usuario))
        elif opcion == "4":
            id_usuario = input("Ingrese el ID del usuario a dar de baja: ")
            print(biblioteca.dar_de_baja_usuario(id_usuario))
        elif opcion == "5":
            isbn = input("Ingrese el ISBN del libro a prestar: ")
            id_usuario = input("Ingrese el ID del usuario que recibirá el libro: ")
            print(biblioteca.prestar_libro(isbn, id_usuario))
        elif opcion == "6":
            isbn = input("Ingrese el ISBN del libro a devolver: ")
            id_usuario = input("Ingrese el ID del usuario que devuelve el libro: ")
            print(biblioteca.devolver_libro(isbn, id_usuario))
        elif opcion == "7":
            print("Buscar por: 1. Título, 2. Autor, 3. Categoría")
            subop = input("Seleccione una opción de búsqueda: ")
            if subop == "1":
                valor = input("Ingrese el título a buscar: ")
                resultados = biblioteca.buscar_libros("titulo", valor)
            elif subop == "2":
                valor = input("Ingrese el autor a buscar: ")
                resultados = biblioteca.buscar_libros("autor", valor)
            elif subop == "3":
                valor = input("Ingrese la categoría a buscar: ")
                resultados = biblioteca.buscar_libros("categoria", valor)
            else:
                print("[ERROR] Opción de búsqueda inválida. Inténtelo de nuevo.")
                continue
            if resultados:
                print("\n--- Resultados de la Búsqueda ---")
                for libro in resultados:
                    print(libro)
            else:
                print("[INFO] No se encontraron libros con ese criterio.")
        elif opcion == "8":
            id_usuario = input("Ingrese el ID del usuario: ")
            print("\n--- Libros Prestados ---")
            print(biblioteca.listar_libros_prestados(id_usuario))
        elif opcion == "9":
            print("\n--- Lista de Todos los Libros ---")
            if not biblioteca.libros:
                print("[INFO] No hay libros en la biblioteca.")
            else:
                for libro in biblioteca.libros.values():
                    print(libro)
        elif opcion == "10":
            print("\n--- Lista de Usuarios Registrados ---")
            if not biblioteca.usuarios:
                print("[INFO] No hay usuarios registrados.")
            else:
                for usuario in biblioteca.usuarios.values():
                    print(usuario)
        elif opcion == "11":
            submenu_multas(biblioteca)
        elif opcion == "12":
            exportar_estado(biblioteca)
            print("Muchas gracias por utilizar el sistema de gestión de la Biblioteca Digital, vuelve pronto.")
            break
        else:
            print("[ERROR] Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    menu()
