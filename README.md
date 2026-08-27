# Finanzas Familiares

Aplicación web para el registro y consulta de movimientos financieros
familiares. La aplicación permite organizar los movimientos mediante
usuarios, ubicaciones, etiquetas y fechas, además de proporcionar
herramientas para consultar y filtrar la información almacenada.

## Tecnologías

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic

### Frontend
- HTML
- CSS
- JavaScript

### Conceptos y herramientas
- REST API
- Query parameters
- Git / GitHub

## Características

- Registro de usuarios.
- Registro de ubicaciones mediante coordenadas geográficas.
- Creación y organización de etiquetas.
- Registro de movimientos financieros.
- Asociación de movimientos con usuarios y ubicaciones.
- Consulta de información financiera.
- Filtrado de datos mediante parámetros de consulta.
- Validación de los datos recibidos por la API.
- Interfaz web interactiva.

## Arquitectura

La aplicación está dividida en un frontend y un backend.

El backend está construido con FastAPI y proporciona una API REST mediante
endpoints para la creación y consulta de usuarios, ubicaciones, etiquetas y
movimientos financieros.

Los datos enviados a la API son validados mediante modelos de Pydantic antes
de ser procesados.

El frontend está compuesto por HTML, CSS y JavaScript, y se comunica con el
backend mediante la API.

## API

| Método | Endpoint | Función |
|--------|----------|---------|
| POST | `/crear_usuario` | Creación de usuarios |
| GET | `/leer_usuarios` | Consulta de usuarios |
| POST | `/crear_ubicacion` | Creación de ubicaciones |
| GET | `/leer_ubicaciones` | Consulta de ubicaciones |
| POST | `/crear_etiqueta` | Creación de etiquetas |
| GET | `/leer_etiquetas` | Consulta de etiquetas |
| POST | `/crear_movimiento` | Registro de movimientos |
| GET | `/leer_datos` | Consulta y filtrado de movimientos |


## Validación de datos

Los datos recibidos por la API son definidos mediante modelos de Pydantic.
Se establecen tipos y restricciones para campos como nombres, coordenadas,
montos y fechas.

Por ejemplo, los movimientos financieros requieren una fecha con un formato
específico y un monto con dos cifras decimales.

## Ejecución
1. Instalación

Se recomienda utilizar un entorno virtual de Python.

python -m venv .venv

Activación del entorno:

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

2. Instalación de dependencias

```bash
pip install -r requirements.txt
```

3. Ejecución

El servidor puede ejecutarse mediante Uvicorn:

```bash
uvicorn src.api:app --reload
```

Una vez iniciado el servidor, la aplicación puede accederse desde el
navegador mediante la dirección proporcionada por Uvicorn.

## Estado del proyecto

El proyecto se encuentra en desarrollo. Las funcionalidades principales se
encuentran implementadas, mientras que algunas características continúan
siendo mejoradas.

## Asistencia mediante IA

La implementación del frontend, particularmente el HTML y CSS, fue realizada
con asistencia de una herramienta de inteligencia artificial.

La lógica del backend, la API, el manejo de datos y la funcionalidad
interactiva mediante JavaScript fueron desarrollados por el autor.
