# Grupo Nº1 Constucción de Software.

## Integrantes

| Nombre             | Rol   |
| ------------------ | ----- |
| Benjamín Arancibia | Dev   |
| Camilo Fuentes     | Dev   |
| José Gómez         | Lider |

---
## 🛠 Estandarización de Código y Linters

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
