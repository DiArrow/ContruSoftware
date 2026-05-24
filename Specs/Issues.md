Estudiante - Issue #2
**Título**: Implementación del Esquema de Datos en PostgreSQL.
**Descripción**: Crear los archivos de inicialización de la base de datos.
**Criterios de aceptación**:
- [ ] Archivo init.sql con el modelo de datos en formato SQL.
- [ ] Creación de usuario de acceso a la base de datos en archivo users.sql.
- [ ] El código SQL debe seguir la guía de estilo SQLRuff.
- [ ] Conexión y ejecución de consultas para comprobar existencia de las tablas (\dt) y  sus atributos (SELECT).
**Asignee**: Estudiante
**Labels**: Infraestructura

---

Estudiante - Issue #4
**Título**: Creación de modelos SQLAlchemy en el backend e integración con la base de datos 
**Descripción**: Crear los archivos de inicialización de la base de datos.
**Criterios de aceptación**:
- [ ] Modelo de datos presentes en el backend.
- [ ] Conexión mediante credenciales a la base de datos
- [ ] Código en Python sigue la guía de estilos PEP 8
- [ ] Código en Python con tipado estático.
**Asignee**: Estudiante
**Labels**: Infraestructura, backend

---

Estudiante - Issue #5
**Título**: Implementación de Core de Autenticación y Middleware de Seguridad 
**Descripción**: Establecer la lógica de generación, validación de tokens JWT y el control de acceso basado en roles (RBAC) para proteger las rutas del API. Esta base permitirá que cualquier método de login (incluyendo el futuro Google OAuth2) funcione bajo un estándar común.
**Criterios de aceptación**:
- [ ] Implementar `OAuth2PasswordBearer` en FastAPI para extraer el token de los headers.
- [ ] Crear funciones para codificar (crear) y decodificar (validar) tokens JWT usando una `SECRET_KEY`.
- [ ] Crear un middleware o dependencia que verifique los roles de usuario (SOL, EST, AYU, PRO, ADM) antes de permitir el acceso a ciertos endpoints.
- [ ] Asegurar que el modelo de usuario en PostgreSQL incluya los campos necesarios para la sesión (email, rol, estado).
- [ ] Código debe seguir la guía de estilos PEP 8.
- [ ] Código en Python con tipado estático.
**Asignee**: Estudiante 
**Labels**: Backend, Infraestructura

---

Estudiante - Issue #6
**Título**: Backend: Implementación de Integración Google OAuth2 y Registro Automático **Descripción**: Desarrollar los endpoints y la lógica de negocio necesaria para autenticar usuarios mediante Google OAuth2. El sistema debe recibir las credenciales de Google, validar la identidad del usuario y vincularla con el sistema de permisos interno (JWT/RBAC)
**Criterios de aceptación**:
- [ ] Implementación de la estrategia de OAuth2 (usando `authlib` o `fastapi-sso`) vinculada a las credenciales de Google Cloud Console.
- [ ] Implementar endpoint `/auth/login`: Punto de entrada que genera la URL de redirección hacia el servidor de autorización de Google.
- [ ] Implementar endpoint  `/auth/callback`:
    - Procesamiento del código de autorización devuelto por Google.
    - Verificación del `id_token` y extracción de datos básicos (email, nombre, imagen).
- [ ] Lógica de Sincronización de Usuarios:
    - Si el usuario no existe en la base de datos PostgreSQL, se debe crear automáticamente con el rol **Solicitante (SOL)**.
    - Si el usuario existe, se deben actualizar sus datos de perfil si hubo cambios.
- [ ] El flujo debe finalizar retornando un JWT propio del sistema que contenga el `sub` (identificador) y el `role` del usuario para su uso en el frontend.
- [ ] Los endpoints deben estar correctamente tipados y visibles en `/docs` (Swagger) con sus respectivos esquemas de respuesta.
- [ ] Código debe seguir la guía de estilos PEP 8.
- [ ] Código en Python con tipado estático.
**Asignee**: Estudiante 
**Labels**: Backend, Infraestructura