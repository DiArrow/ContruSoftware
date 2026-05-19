# Grupo Nº1 Constucción de Software.

# Integrantes

| Nombre             | Rol   |
| ------------------ | ----- |
| Benjamín Arancibia | Dev   |
| Camilo Fuentes     | Dev   |
| José Gómez         | Lider |

---
# Estandares de Codificación

## 1. Nomenclatura y Valores

- **Variables descriptivas:** Las variables deben nombrarse utilizando sustantivos concretos y descriptivos que expliquen claramente la información que almacenan (evitando nombres genéricos o ambiguos).
- **Constantes en mayúsculas:** Queda prohibido el uso de valores _hardcodeados_ (números o cadenas de texto mágicas) sueltos en la lógica. Estos deben extraerse a constantes declaradas en mayúsculas al inicio del archivo o en un archivo de configuración.
- **Funciones orientadas a la acción:** Todo nombre de función o método debe incluir un verbo que describa explícitamente la acción que realiza (ej. `calcularTotal`, `obtenerUsuario`). _Excepción:_ Se toleran convenciones estándar para _getters_ y _setters_.

## 2. Diseño de Funciones

- **Límite de argumentos:** Las funciones deben ser concisas y no recibir más de **3 argumentos**. Si una función requiere más, la información debe agruparse y pasarse mediante un objeto o estructura de datos.
- **Inmutabilidad de parámetros:** Los parámetros que recibe una función son de solo lectura y no deben modificarse o reasignarse directamente. Cualquier transformación de los datos de entrada debe guardarse en una nueva variable local.

## 3. Arquitectura y Estilo

- **Inyección de dependencias:** Si una función o clase necesita interactuar con un servicio externo (bases de datos, APIs, clientes HTTP), la instancia de dicho servicio debe pasarse como parámetro, nunca debe ser instanciada internamente.
- **Indentación:** Todo el código del proyecto debe indentarse utilizando estrictamente **4 espacios** por nivel (sin tabulaciones).

## 4. Seguridad y Control de Versiones

- **Cero credenciales en el código:** Queda estrictamente prohibido registrar contraseñas, _tokens_ de acceso, llaves de API o cualquier secreto en el repositorio. Toda información sensible debe gestionarse a través de variables de entorno.
- **Commits estandarizados:** El historial del repositorio debe mantenerse limpio e intencional. Todo mensaje de _commit_ debe iniciar con uno de los siguientes prefijos obligatorios:
    - `feat:` Al añadir una nueva funcionalidad.
    - `fix:` Al corregir un error o _bug_.
    - `docs:` Al realizar cambios exclusivos en la documentación.
    - `refactor:` Al reestructurar código sin alterar su comportamiento ni añadir funciones nuevas.

## 🛠 Estandarización de Código y Linters por lenguaje de programación

Para mantener la calidad y consistencia en el proyecto, utilizamos las siguientes herramientas:
* **Frontend:** ESLint (Estándar Airbnb) + Prettier
* **Backend:** Ruff (Estándar PEP 8)
* **Base de Datos:** SQLFluff (Dialecto PostgreSQL)
* **Infraestructura:** Yamllint y Hadolint (Docker)

---
### 💻 Ejecución Local (Antes de hacer commit)

Para facilitar tu flujo de trabajo, hemos creado scripts que revisan y auto-corrigen tu código usando entornos virtuales aislados (no ensuciarán las dependencias globales de tu PC). 

**Requisitos:** Tener instalados Node.js, Python y tener **Docker Desktop abierto** (necesario para evaluar los Dockerfiles).

Desde la carpeta raíz del proyecto, ejecuta el script correspondiente a tu sistema operativo:

* **En Linux / Mac:**
```bash
  bash test_linters/run_linters.sh
```
- **En Windows:**
``` Powershell
.\test_linters\run_linters.bat
```
