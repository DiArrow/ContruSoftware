# Grupo Nº1 Constucción de Software.

# Integrantes

| Nombre             | Rol   |
| ------------------ | ----- |
| Benjamín Arancibia | Dev   |
| Camilo Fuentes     | Dev   |
| José Gómez         | Lider |

---
# Nombre de Dominio

> proy-const.cfuentes.dev

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
### 📖 Estándares de Codificación por Lenguaje de Programación

#### 1. Frontend (JavaScript / React)
* **Herramientas:** ESLint + Prettier
* **Estándar base:** **ESLint Recommended** & **React Recommended**.
* **Reglas principales:** 
  * Uso estricto de Hooks de React (`react-hooks/recommended`).
  * Prettier maneja el formato:  punto y coma obligatorio, y comillas simples (`'`).
  * Prevención de variables no utilizadas y exportaciones incorrectas en Vite.

#### 2. Backend (Python / FastAPI)
* **Herramienta:** Ruff
* **Estándar base:** **PEP 8** (El estándar oficial de Python) + Estilo **Black**.
* **Reglas principales:**
  * **Pycodestyle (E, W):** Validación estricta del PEP 8 (espacios, saltos de línea).
  * **Pyflakes (F):** Detección de errores lógicos (variables sin usar, imports faltantes).
  * **Isort (I):** Ordenamiento automático y alfabético de las importaciones.
  * **Formato:** Longitud máxima de 88 caracteres por línea y uso de comillas dobles (`"`) para strings.

#### 3. Base de Datos (SQL / PostgreSQL)
* **Herramienta:** SQLFluff
* **Estándar base:** **PostgreSQL Official Conventions**.
* **Reglas principales:**
  * Palabras reservadas y funciones (`SELECT`, `FROM`, `COUNT`) estrictamente en **MAYÚSCULAS**.
  * Identificadores (nombres de tablas y columnas) estrictamente en **minúsculas**.

#### 4. Infraestructura (Docker & YAML)
* **Herramientas:** Hadolint (Docker) + Yamllint (YAML)
* **Estándar base:** **Docker Official Best Practices**.
* **Reglas principales:**
  * **Docker:** Uso de tags específicos (no usar `:latest`), agrupación de comandos `RUN`, y limpieza de cachés apt/apk (`--no-install-recommends`).
  * **YAML:** Longitud máxima de 120 caracteres, indentación estricta y formato uniforme en archivos de configuración como `docker-compose.yml` y GitHub Actions.

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
---

### Estrategia de branching

GitLab Flow adaptado:

- deploy
- main
- develop
- feat-x

---

### 🔑 Credenciales de Prueba

Todos los usuarios de prueba usan la misma contraseña: **`test123`**

| Rol          | Email        | Password | Descripción        |
| ------------ | ------------ | -------- | ------------------ |
| Solicitante  | `sol@uc.cl`  | test123  | Usuario SOL        |
| Estudiante   | `est@uc.cl`  | test123  | Usuario EST        |
| Ayudante     | `ayu@uc.cl`  | test123  | Usuario AYU        |
| Profesor     | `pro@uc.cl`  | test123  | Usuario PRO        |
| Admin        | `adm@uc.cl`  | test123  | Usuario ADM        |

> **Nota:** Estos usuarios se crean automáticamente al levantar los contenedores con `docker compose up --build`. No requieren ejecutar migraciones manuales.

#### Endpoints de Autenticación

| Método | Endpoint           | Descripción                     |
| ------ | ------------------ | ------------------------------- |
| POST   | `/api/auth/token`  | Login: envía `{email, password}` |
| GET    | `/api/auth/me`     | Perfil del usuario autenticado (requiere `Authorization: Bearer <token>`) |

#### Ejemplo de Login

```bash
# Obtener token JWT
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "sol@uc.cl", "password": "test123"}'

# Usar token para obtener perfil
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```
