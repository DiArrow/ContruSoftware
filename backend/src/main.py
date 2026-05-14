from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Definimos un modelo de datos (Schema)
class Item(BaseModel):
    nombre: str
    precio: float
    descripcion: str | None = None
    oferta: bool = False


# Ruta de inicio (GET)
@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Bienvenido a mi API con FastAPI!"}


# Ruta con parámetros de ruta (GET)
@app.get("/items/{item_id}")
def leer_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "busqueda": q}


# Ruta para crear datos (POST)
@app.post("/items/")
def crear_item(item: Item):
    return {"mensaje": f"Producto '{item.nombre}' creado exitosamente", "datos": item}
