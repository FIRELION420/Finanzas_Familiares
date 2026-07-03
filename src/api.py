from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware # BORARRRRRRRRRRR
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from typing import Annotated
from .finanzas import crear_usuario, crear_tablas, crear_movimiento, leer_datos, crear_ubicacion, leer_usuarios, leer_ubicaciones, crear_etiqueta, leer_etiquetas

origenes = ["http://127.0.0.1:5500"]

class UsuarioNuevo(BaseModel) :
    nombre: str
    color: str = Field(pattern = r"#[0-9a-f]{6}")

class UbicacionNueva(BaseModel) :
    nombre: str
    latitud: float
    longitud: float

class EtiquetaNueva(BaseModel) :
    etiqueta: str
    etiqueta_padre: str

class MovimientoNuevo(BaseModel) :
    usuario: str | None
    ubicacion: str
    descripcion: str
    monto: str = Field(pattern = r"\d+\.\d{2}")
    tipo: str
    fecha: str = Field(pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
    nota: str | None
    calidad: int | None

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = origenes,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/crear_usuario")
def crear_usuario_endpoint(usuario: UsuarioNuevo) :
    respuesta = crear_usuario(usuario = usuario.nombre, color = usuario.color)
    return respuesta

@app.get("/leer_usuarios")
def leer_usuarios_endpoint():
    respuesta = leer_usuarios()
    return respuesta

@app.post("/crear_ubicacion")
def crear_ubicacion_endpoint(ubicacion: UbicacionNueva) :
    respuesta = crear_ubicacion(
        nombre = ubicacion.nombre,
        latitud = ubicacion.latitud,
        longitud = ubicacion.longitud
        )
    return respuesta

@app.get("/leer_ubicaciones")
def leer_ubicaciones_endpoint() :
    respuesta = leer_ubicaciones()
    return respuesta

@app.post("/crear_etiqueta")
def crear_etiqueta_endpoint(etiqueta: EtiquetaNueva) :
    respuesta = crear_etiqueta(
        etiqueta = etiqueta.etiqueta,
        etiqueta_padre = etiqueta.etiqueta_padre
    )
    return respuesta

@app.get("/leer_etiquetas")
def leer_etiquetas_endpoint() :
    respuesta = leer_etiquetas()
    return respuesta

@app.post("/crear_movimiento")
def crear_movimiento_endpoint(movimiento: MovimientoNuevo) :

    try :
        respuesta = crear_movimiento(
            usuario = movimiento.usuario,
            ubicacion = movimiento.ubicacion,
            descripcion = movimiento.descripcion,
            monto = movimiento.monto,
            tipo = movimiento.tipo,
            fecha = movimiento.fecha,
            nota = movimiento.nota,
            calidad = movimiento.calidad
            )
    except ValueError as error:
        raise HTTPException(status_code = 404, detail = str(error))

    return respuesta

@app.get("/leer_datos")
async def leer_datos_endpoint(
    usuarios: Annotated[list[str] | None, Query()] = None,
    ubicaciones: Annotated[list[str] | None, Query()] = None,
    fechas: Annotated[list[str] | None, Query()] = None,
    tipos: Annotated[list[str] | None, Query()] = None,
    etiquetas: Annotated[list[str] | None, Query()] = None
) :
    respuesta = leer_datos(
        usuarios = usuarios,
        ubicaciones = ubicaciones,
        fechas = fechas,
        tipos = tipos,
        etiquetas = etiquetas
    )
    return respuesta

app.mount("/static", StaticFiles(directory = "src/frontend"), name = "frontend")

@app.get("/")
def servir_pagina():
    return FileResponse("src/frontend/pagina.html")