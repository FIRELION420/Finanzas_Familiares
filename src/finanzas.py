import sqlite3
from itertools import groupby
import requests
import time

NOMBRE_USUARIO_REFERENCIAS = "referencias"
COLOR_USUARIO_REFERENCIAS = "#05ad7b"

def enviar(funcion) :

    def wrapper(*args, **kwargs) :

        conexion = sqlite3.connect("finanzas.db")
        cursor = conexion.cursor()

        try :
            resultado = funcion(cursor, *args, **kwargs)
            conexion.commit()
            return resultado

        finally :
            cursor.close()
            conexion.close()

    return wrapper


@enviar
def crear_tablas(cursor) :
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    color TEXT NOT NULL,
                    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
                    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos(
                    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL,
                    id_ubicacion INTEGER NOT NULL,
                    descripcion TEXT NOT NULL,
                    monto INTEGER NOT NULL CHECK(monto > 0),
                    tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso', 'referencia')),
                    fecha TEXT NOT NULL,
                    nota TEXT,
                    calidad INTEGER CHECK(calidad >= 0 AND calidad <= 5),
                            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                            FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones(id_ubicacion)
                    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etiquetas(
                    id_etiqueta INTEGER PRIMARY KEY AUTOINCREMENT,
                    etiqueta TEXT NOT NULL,
                    id_padre INTEGER,
                        FOREIGN KEY (id_padre) REFERENCES etiquetas(id_etiqueta)
                    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimiento_etiqueta(
                    id_movimiento INTEGER NOT NULL,
                    id_etiqueta INTEGER NOT NULL,
                        FOREIGN KEY (id_movimiento) REFERENCES movimientos(id_movimiento),
                        FOREIGN KEY (id_etiqueta) REFERENCES etiquetas(id_etiqueta)
                    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipo_ubicacion(
                   id_tipo_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   tipo TEXT NOT NULL
                   )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ubicaciones(
                    id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    id_padre INTEGER,
                    id_tipo_ubicacion INTEGER NOT NULL,
                    latitud REAL,
                    longitud REAL,
                        FOREIGN KEY (id_padre) REFERENCES ubicaciones(id_ubicacion),
                        FOREIGN KEY (id_tipo_ubicacion) REFERENCES tipo_ubicacion(id_tipo_ubicacion),
                        CONSTRAINT UQ_columnas UNIQUE (nombre, id_padre)
                    )
    """)

    global NOMBRE_USUARIO_REFERENCIAS

    cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre = (?)", (NOMBRE_USUARIO_REFERENCIAS, ))
    if not cursor.fetchone() :
        cursor.execute("INSERT INTO usuarios(nombre, color) VALUES (?, ?)", (NOMBRE_USUARIO_REFERENCIAS, COLOR_USUARIO_REFERENCIAS))



@enviar
def crear_usuario(cursor, usuario, color) :

    nombre = usuario.lower().strip()
    cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre = (?)", (nombre, ))
    id_usuario = cursor.fetchone()

    if id_usuario :
        return {"id": id_usuario[0], "nombre": nombre, "color": color, "estado": "preexistente"}
    else :
        cursor.execute("INSERT INTO usuarios(nombre, color) VALUES (?, ?)", (nombre, color))

        return {"id": cursor.lastrowid, "nombre": nombre, "color": color, "estado": "creado"}

@enviar
def leer_usuarios(cursor) :
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    respuesta = list()
    for usuario in usuarios :
        diccionario = {
            "id_usuario": usuario[0],
            "nombre": usuario[1],
            "color": usuario[2],
            "fecha_creacion": usuario[3]
        }
        respuesta.append(diccionario)

    return respuesta

def registrar_ubicacion(cursor, nombre, id_padre, tipo, latitud, longitud) :
    time.sleep(1)
    nombre = nombre.lower().strip()

    cursor.execute("SELECT id_ubicacion FROM ubicaciones WHERE nombre = (?)", (nombre, ))
    id_ubicacion = cursor.fetchone()

    if id_ubicacion :
        return id_ubicacion[0]
    else :
        cursor.execute("SELECT id_tipo_ubicacion FROM tipo_ubicacion WHERE tipo = (?)", (tipo, ))
        id_tipo = cursor.fetchone()
        if not id_tipo :
            cursor.execute("INSERT INTO tipo_ubicacion(tipo) VALUES (?)", (tipo, ))
            id_tipo = cursor.lastrowid
        else :
            id_tipo = id_tipo[0]

        cursor.execute(
            "INSERT INTO ubicaciones(nombre, id_padre, id_tipo_ubicacion, latitud, longitud) VALUES (?, ?, ?, ?, ?)",
            (nombre, id_padre, id_tipo, latitud, longitud)
        )
        cursor.execute("SELECT id_ubicacion FROM ubicaciones WHERE nombre = (?)", (nombre, ))
        id_ubicacion = cursor.fetchone()
        return id_ubicacion[0]
        

@enviar
def crear_ubicacion(cursor, nombre, latitud, longitud) :
    id_padre = None
    nombre = nombre.lower().strip()

    cursor.execute("SELECT * FROM ubicaciones WHERE nombre = (?)", (nombre, ))
    id_ubicacion = cursor.fetchone()


    if id_ubicacion :
        return {"id": id_ubicacion[0], "nombre": nombre, "id_padre": id_ubicacion[2], "tipo": id_ubicacion[3], "latitud": id_ubicacion[4], "longitud": id_ubicacion[5], "estado": "preexistente"}
    else :
        
        url = f"https://nominatim.openstreetmap.org/reverse"
        headers = {
            "User-Agent": "registro ubicaciones",
            "Accept": "application/json"
        }
        respuesta = requests.get(url=url, headers=headers, params= {
            "format": "json",
            "lat": latitud,
            "lon": longitud,
            "addressdetails": 1,
            "extratags": 0,
            "namedetails": 0,
            "entrances": 0,
            "accept-language": "es",
            "zoom": 18,
            "layer": "poi"
        })
        diccionario = respuesta.json()

        if diccionario["address"].get("country") :
            id_padre = registrar_ubicacion(
                cursor = cursor,
                nombre = diccionario["address"]["country"],
                id_padre = id_padre,
                tipo = "pais",
                latitud = None,
                longitud = None
                )
        if diccionario["address"].get("state") :
            id_padre = registrar_ubicacion(
                cursor = cursor,
                nombre = diccionario["address"]["state"],
                id_padre = id_padre,
                tipo = "estado",
                latitud = None,
                longitud = None
                )
        if diccionario["address"].get("county") :
            id_padre = registrar_ubicacion(
                cursor = cursor,
                nombre = diccionario["address"]["county"],
                id_padre = id_padre,
                tipo = "municipio",
                latitud = None,
                longitud = None
                )
        if diccionario["address"].get("city") :
            id_padre = registrar_ubicacion(
                cursor = cursor,
                nombre = diccionario["address"]["city"],
                id_padre = id_padre,
                tipo = "localidad",
                latitud = None,
                longitud = None
                )
            
        id_ubicacion = registrar_ubicacion(
            cursor = cursor,
            nombre = nombre,
            id_padre = id_padre,
            tipo = diccionario["class"],
            latitud = latitud,
            longitud = longitud
            )
        
        return {"id": id_ubicacion, "nombre": nombre, "id_padre": id_padre, "tipo": diccionario["class"], "latitud": latitud, "longitud": longitud, "estado": "creado"}

@enviar
def leer_ubicaciones(cursor) :
    cursor.execute("SELECT * FROM ubicaciones")
    ubicaciones = cursor.fetchall()

    respuesta = list()
    for ubicacion in ubicaciones :
        diccionario = {
            "id_ubicacion": ubicacion[0],
            "nombre": ubicacion[1],
            "id_padre": ubicacion[2],
            "tipo": ubicacion[3],
            "latitud": ubicacion[4],
            "longitud": ubicacion[5]
        }
        respuesta.append(diccionario)

    return respuesta

@enviar
def crear_etiqueta(cursor, etiqueta, etiqueta_padre) :
    etiqueta = etiqueta.lower().strip()

    cursor.execute("SELECT * FROM etiquetas WHERE etiqueta = (?)", (etiqueta, ))
    respuesta = cursor.fetchone()

    if respuesta :
        return {"id_etiqueta": respuesta[0], "etiqueta": respuesta[1], "id_padre": respuesta[2]}
    
    else:   
        cursor.execute("SELECT id_etiqueta FROM etiquetas WHERE etiqueta = (?)", (etiqueta_padre, ))
        id_padre = cursor.fetchone()

        if id_padre :
            id_padre = id_padre[0]

        cursor.execute("INSERT INTO etiquetas(etiqueta, id_padre) VALUES (?, ?)", (etiqueta, id_padre))

        return {"id_etiqueta": cursor.lastrowid, "etiqueta": etiqueta, "id_padre": id_padre}

@enviar
def leer_etiquetas(cursor):
    cursor.execute("SELECT * FROM etiquetas")
    etiquetas = cursor.fetchall()

    respuesta = list()
    for etiqueta in etiquetas :
        diccionario = {
            "id_etiqueta": etiqueta[0],
            "etiqueta": etiqueta[1],
            "id_padre": etiqueta[2]
        }
        respuesta.append(diccionario)

    return respuesta

@enviar
def crear_movimiento(cursor, ubicacion, descripcion, monto, tipo, fecha, nota = None, calidad = None, etiquetas = None, usuario = None) :

    if usuario :
        usuario = usuario.lower().strip()
        cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre = (?)", (usuario, ))
        id_usuario = cursor.fetchone()
        if not id_usuario :
            raise ValueError("no se encontro al usuario")
        else :
            id_usuario = id_usuario[0]
    else :
        global NOMBRE_USUARIO_REFERENCIAS
        cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre = (?)", (NOMBRE_USUARIO_REFERENCIAS, ))
        id_usuario = cursor.fetchone()[0]

    ubicacion = ubicacion.lower().strip()
    cursor.execute("SELECT id_ubicacion FROM ubicaciones WHERE nombre = (?)", (ubicacion, ))
    id_ubicacion = cursor.fetchone()
    if not id_ubicacion :
            cursor.execute("INSERT INTO ubicaciones(ubicacion) VALUES (?)", (ubicacion, ))    
            id_ubicacion = cursor.lastrowid
    else :
        id_ubicacion = id_ubicacion[0]

    valores = monto.split(".")
    monto_entero = valores[0] + valores[1]
    monto_entero = int(monto_entero)
    
    datos = {
        "id_usuario": id_usuario,
        "id_ubicacion": id_ubicacion,
        "descripcion": descripcion,
        "monto": monto_entero,
        "tipo": tipo,
        "fecha": fecha,
        "nota": nota,
        "calidad": calidad
    }

    agregar = list()
    columnas = ""
    signos = ""

    for clave in datos.keys() :
        if datos[clave] :
            columnas = columnas + clave + ","
            agregar.append(datos[clave])

    for i in range(len(agregar)) :
        signos += "?,"
    
    columnas = columnas[:-1]
    signos = signos[:-1]

    cursor.execute(f"INSERT INTO movimientos({columnas}) VALUES ({signos})", agregar)

    if etiquetas :
        id_movimiento = cursor.lastrowid
        ids_etiquetas = list()

        for etiqueta in etiquetas :
            cursor.execute("SELECT id_etiqueta FROM etiquetas WHERE etiqueta = (?)", (etiqueta, ))
            respuesta = cursor.fetchone()
            if respuesta :
                ids_etiquetas.append(respuesta[0])
            else :
                cursor.execute("INSERT INTO etiquetas(etiqueta) VALUES (?)", (etiqueta, ))
                ids_etiquetas.append(cursor.lastrowid)

        for id_etiqueta in ids_etiquetas :
            cursor.execute("INSERT INTO movimiento_etiqueta(id_movimiento, id_etiqueta) VALUES (?, ?)", (id_movimiento, id_etiqueta))

    return datos

@enviar
def leer_datos(cursor, usuarios = None, ubicaciones = None, fechas = None, tipos = None, etiquetas = None) :
    condiciones_texto = ""
    condiciones_datos = list()

    if usuarios :
        ids_usuarios = list()
        signos = ""
        for usuario in usuarios :
            cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre = (?)", (usuario.lower().strip(), ))
            id_usuario = cursor.fetchone()
            if not id_usuario :
                raise ValueError("no se encontro al usuario")
            signos += "?,"
            ids_usuarios.append(id_usuario[0])        
        condiciones_texto  = f"movimientos.id_usuario IN ({signos[:-1]})"
        condiciones_datos.extend(ids_usuarios)

    if ubicaciones :
        ids_ubicaciones = list()
        signos = ""
        for ubicacion in ubicaciones :
            cursor.execute("""WITH RECURSIVE arbolUbicaciones AS (
                            SELECT * FROM ubicaciones WHERE nombre = (?)
                            
                            UNION ALL

                            SELECT ubicaciones.* FROM ubicaciones JOIN arbolUbicaciones ON ubicaciones.id_padre = arbolUbicaciones.id_ubicacion
                            )
                            SELECT id_ubicacion FROM arbolUbicaciones
            """, (ubicacion.lower().strip(), ))

            ids_ubicaciones_hijos = cursor.fetchall()
            for id in ids_ubicaciones_hijos :
                signos += "?,"
                ids_ubicaciones.append(id[0])

        if condiciones_texto :
            condiciones_texto += f" AND movimientos.id_ubicacion IN ({signos[:-1]})"
        else :
            condiciones_texto = f"movimientos.id_ubicacion IN ({signos[:-1]})"
        condiciones_datos.extend(ids_ubicaciones)
    
    if fechas :
        if condiciones_texto :
            condiciones_texto += " AND movimientos.fecha BETWEEN (?) AND (?)"
        else :
            condiciones_texto = "movimientos.fecha BETWEEN (?) AND (?)"
        condiciones_datos.append(fechas[0])
        condiciones_datos.append(fechas[1])

    if tipos :
        tipos_movimiento = list()
        signos = ""
        for tipo in tipos :
            signos += "?,"
            tipos_movimiento.append(tipo)
        if condiciones_texto :
            condiciones_texto += f" AND movimientos.tipo IN ({signos[:-1]})"
        else :
            condiciones_texto = f"movimientos.tipo IN ({signos[:-1]})"
        condiciones_datos.extend(tipos_movimiento)

    if etiquetas :
        ids_etiquetas = list()
        simbolos = ""

        for etiqueta in etiquetas :
            cursor.execute("""WITH RECURSIVE arbolEtiquetas AS (
                            SELECT * FROM etiquetas WHERE etiqueta = (?)
                            
                            UNION ALL

                            SELECT etiquetas.* FROM etiquetas JOIN arbolEtiquetas ON etiquetas.id_padre = arbolEtiquetas.id_etiqueta
                            )
                            SELECT id_etiqueta FROM arbolEtiquetas
            """, (etiqueta, ))

            ids_etiquetas_hijos = cursor.fetchall()
            for id in ids_etiquetas_hijos :
                simbolos = simbolos + "?,"
                ids_etiquetas.append(id[0])
        simbolos = simbolos[:-1]

        if condiciones_texto :
            condiciones_texto += f" AND etiquetas.id_etiqueta IN ({simbolos})"
        else :
            condiciones_texto = f"etiquetas.id_etiqueta IN ({simbolos})"
        condiciones_datos.extend(ids_etiquetas)

    if condiciones_texto :
        cursor.execute(f"""SELECT movimientos.*, etiquetas.etiqueta
                            FROM movimientos
                            LEFT JOIN movimiento_etiqueta ON movimientos.id_movimiento = movimiento_etiqueta.id_movimiento
                            LEFT JOIN etiquetas ON movimiento_etiqueta.id_etiqueta = etiquetas.id_etiqueta
                            WHERE {condiciones_texto}
                            ORDER BY movimientos.id_movimiento""",
                       condiciones_datos)
        movimientos = cursor.fetchall()
    else :
        cursor.execute(f"""SELECT movimientos.*, etiquetas.etiqueta
                            FROM movimientos
                            LEFT JOIN movimiento_etiqueta ON movimientos.id_movimiento = movimiento_etiqueta.id_movimiento
                            LEFT JOIN etiquetas ON movimiento_etiqueta.id_etiqueta = etiquetas.id_etiqueta
                            ORDER BY movimientos.id_movimiento""")
        movimientos = cursor.fetchall()

    respuesta = list()
    for id_mov, grupo in groupby(movimientos, key=lambda fila: fila[0]) :
        primera_fila = next(grupo)
        etiquetas_mov = [primera_fila[-1]]
        for fila in grupo :
            etiquetas_mov.append(fila[-1])
        
        etiquetas_mov = [e for e in etiquetas_mov if e is not None]

        if not etiquetas_mov :
            etiquetas_mov = [None]
        
        diccionario = {
        "id_movimiento": primera_fila[0],
        "id_usuario": primera_fila[1],
        "id_ubicacion": primera_fila[2],
        "descripcion": primera_fila[3],
        "monto": primera_fila[4],
        "tipo": primera_fila[5],
        "fecha": primera_fila[6],
        "nota": primera_fila[7],
        "calidad": primera_fila[8],
        "etiquetas": etiquetas_mov
        }
        respuesta.append(diccionario)

             
    return respuesta
    

# ===================================================PRUEBAS=========================================================================

if __name__ == "__main__" :
    crear_tablas()
    
    probar_crear_usuario = input("¿Quieres probar la creación de usuarios? [si, no]: ")
    if probar_crear_usuario.strip().lower() == "si" :

        usuario = input("¿Que usuario quieres crear?:\n").strip().lower()
        crear_usuario(usuario)
        print(f"Usuario: {usuario} creado")


    probar_crear_movimiento = input("¿Quieres probar la creación de movimientos? [si, no]: ")
    if probar_crear_movimiento.strip().lower() == "si" :

        descripcion = input("¿Que movimiento quieres registrar?:\n")

        monto = input("¿Cuanto fue el monto del movimiento?:\n")

        print("Ingresa el numero correspondiente al tipo de movimiento.\ningreso [1]\negreso [2]\nreferencia [3]")
        tipo = int(input("Numero: "))
        if tipo == 1 :
            tipo = "ingreso"
            usuario = input("Ingreso de que usuario?:\n")
        elif tipo == 2 :
            tipo = "egreso"
            usuario = input("Egreso de que usuario?:\n")
        elif tipo == 3 :
            tipo = "referencia"

        print("¿Cuando se realizó el movimiento? (la respuesta final tendra la forma 'YYYY:MM:DD-HH:mm')")
        año = input("Año [YYYY]: ")
        mes = input("Mes [MM]: ")
        dia = input("Dia [DD]: ")
        hora = input("Hora [HH]: ")
        minuto = input("Minuto [mm]: ")
        fecha = año + "-" + mes + "-" + dia + " " + hora + ":" + minuto

        nota = input("¿Quieres añadir una nota? [si, no]: ")
        if nota.strip().lower() == "si" :
            nota = input("¿Que nota quieres añadir?:\n")
        else :
            nota = None

        calidad = input("¿Quiere agregar una calificación del 1 al 5? [si, no]: ")
        if calidad.strip().lower() == "si" :
            calidad = input("Siendo 1 la calificación mas baja y 5 la mas alta, ¿que tan buena fue la calidad del producto/servicio?:\n")
        else :
            calidad = None

        etiquetas = input("¿Quieres añadirle etiquetas al movimiento? [si, no]: ")
        if etiquetas.strip().lower() == "si" :
            etiquetas = list()
            cantidad = int(input("¿Cuantas etiquetas quieres añadir?: "))
            for i in range(cantidad) :
                etiqueta = input(f"Etiqueta {i + 1}: ").strip().lower()
                etiquetas.append(etiqueta)
        else :
            etiquetas = None

        ubicacion = input("¿Donde se realizo la compra?:\n")
        
        crear_movimiento(descripcion=descripcion, monto=monto, tipo=tipo, fecha=fecha, nota=nota, calidad=calidad, etiquetas=etiquetas, usuario=usuario, ubicacion=ubicacion)
        
        print("Movimiento creado")

    print(leer_datos())