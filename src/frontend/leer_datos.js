// =================================Variables=====================================================
let usuarios
let ubicaciones
let etiquetas
let grafica
let color_usuarios

// ==================================Funciones====================================================
async function crear_leer_datos_usuario () {
    const respuesta = await fetch("/leer_usuarios")
    usuarios = await respuesta.json()
    const nombres = usuarios.map(usuarios => usuarios.nombre)

    nombres.forEach(nombre => {
        const seleccionar_nombre = document.getElementById("leer_datos_usuario");
        let checkbox = document.createElement("input")
        checkbox.type = "checkbox"
        checkbox.value = `${nombre}`
        let label = document.createElement("label")
        label.textContent = `${nombre}`
        seleccionar_nombre.appendChild(label)
        label.appendChild(checkbox)
    });
}

async function crear_leer_datos_ubicacion () {
    const respuesta = await fetch("/leer_ubicaciones")
    ubicaciones = await respuesta.json()
    const nombres_ubicaciones = ubicaciones.map(ubicaciones => ubicaciones.nombre)

    nombres_ubicaciones.forEach(ubicacion => {
        const seleccionar_nombre = document.getElementById("leer_datos_ubicacion");
        let checkbox = document.createElement("input")
        checkbox.type = "checkbox"
        checkbox.value = `${ubicacion}`
        label = document.createElement("label")
        label.textContent = `${ubicacion}`
        seleccionar_nombre.appendChild(label)
        label.appendChild(checkbox)
    });
}

async function crear_leer_datos_etiqueta () {
    const respuesta = await fetch("/leer_etiquetas")
    etiquetas = await respuesta.json()
    const nombres_etiquetas = etiquetas.map(etiqueta => etiqueta.etiqueta)

    nombres_etiquetas.forEach(etiqueta => {
        const seleccionar_nombre = document.getElementById("leer_datos_etiqueta");
        let checkbox = document.createElement("input")
        checkbox.type = "checkbox"
        checkbox.value = `${etiqueta}`
        label = document.createElement("label")
        label.textContent = `${etiqueta}`
        seleccionar_nombre.appendChild(label)
        label.appendChild(checkbox)
    });
}

function invertir_color (color) {
    let r = parseInt(color.slice(1, 3), 16)
    let g = parseInt(color.slice(3, 5), 16)
    let b = parseInt(color.slice(5, 7), 16)

    r = 255 - r
    g = 255 - g
    b = 255 - b

    const rgb = `rgb(${r}, ${g}, ${b})`
    return rgb
}

async function leer_datos (evento) {
    evento.preventDefault()

    // Crear mensaje para la API
    const formulario = document.getElementById("leer_datos_enviar")
    const divs = formulario.querySelectorAll("div[data-nombre]")
    const mensaje = {
        "fechas": [
            document.getElementById("leer_datos_fecha_inicio").value.replace("T", " "),
            document.getElementById("leer_datos_fecha_fin").value.replace("T", " ")
        ]
    }

    mensaje.fechas = mensaje.fechas.filter(fecha => fecha != "")

    divs.forEach(div => {
        let checkbox = div.querySelectorAll("input[type='checkbox']:checked")
        mensaje[div.dataset.nombre] = []

        checkbox.forEach(checkbox => {
            mensaje[div.dataset.nombre].push(checkbox.value)
        })
    })

    const parametros_url = new URLSearchParams()
    const parametros = Object.keys(mensaje)
    parametros.forEach(parametro => {
        mensaje[parametro].forEach(elemento => {
            parametros_url.append(parametro, elemento)
        })
    })

    // Peticion a la API
    const respuesta = await fetch(`/leer_datos?${parametros_url}`)
    const datos = await respuesta.json()
    datos.sort((a, b) => b.fecha.localeCompare(a.fecha))
    datos.forEach(movimiento => {
        movimiento.monto = movimiento.monto / 100
    })
    const display = document.getElementById("leer_datos_display")

    //Crear tabla para display de los datos de la API
    if (document.getElementById("leer_datos_tabla") != null) {
        document.getElementById("leer_datos_tabla").remove()
    }
    const tabla = document.createElement("table")
    tabla.id = "leer_datos_tabla"
    display.appendChild(tabla)
    tabla.innerHTML = `
    <thead>
        <tr>
        <th scope="col">Usuario</th>
        <th scope="col">Ubicación</th>
        <th scope="col">Descripción</th>
        <th scope="col">Monto</th>
        <th scope="col">Tipo</th>
        <th scope="col">Fecha</th>
        <th scope="col">Nota</th>
        <th scope="col">Calificación</th>
        <th scope="col">Etiquetas</th>
        </tr>
    </thead>
    <tbody id="leer_datos_tabla_cuerpo">
    </tbody>
    `
    const tabla_cuerpo = document.getElementById("leer_datos_tabla_cuerpo")
    const cantidad_elementos = datos.length
    let indice = 1
    datos.forEach(movimiento => {
        let fila = document.createElement("tr")
        fila.dataset.indice = cantidad_elementos - indice
        fila.innerHTML = `
            <th scope="row">${usuarios.find(usuario => usuario.id_usuario === movimiento.id_usuario).nombre}</th>
            <td>${ubicaciones.find(ubicacion => ubicacion.id_ubicacion === movimiento.id_ubicacion).nombre}</td>
            <td>${movimiento.descripcion}</td>
            <td>${movimiento.monto}</td>
            <td>${movimiento.tipo}</td>
            <td>${movimiento.fecha}</td>
            <td>${movimiento.nota}</td>
            <td>${movimiento.calidad}</td>
            <td>${movimiento.etiquetas}</td>
        `
        tabla_cuerpo.appendChild(fila)
        indice = indice + 1
        fila.addEventListener("click", () => {
            // Regresar a estado original
            grafica.data.datasets[0].pointBackgroundColor = datos.map(() => "#000000")
            grafica.data.datasets[0].pointRadius = datos.map(() => 3)
            grafica.data.datasets[1].pointBackgroundColor = datos.map(() => "#000000")
            grafica.data.datasets[1].pointRadius = datos.map(() => 3)

            // Modificar nodo correspondiente a tabla clickeada
            grafica.data.datasets[0].pointBackgroundColor[fila.dataset.indice] = "#d4af37"
            grafica.data.datasets[0].pointRadius[fila.dataset.indice] = 6
            grafica.data.datasets[1].pointBackgroundColor[fila.dataset.indice] = "#d4af37"
            grafica.data.datasets[1].pointRadius[fila.dataset.indice] = 6

            grafica.update()
        })
    })

    // Crear grafica con los mismos datos
    datos.sort((a, b) => a.fecha.localeCompare(b.fecha))
    const ids_usuarios = datos.filter(movimiento => movimiento.id_usuario).map(movimiento => movimiento.id_usuario)
    const colores_rgb = usuarios.filter(usuario => ids_usuarios.includes(usuario.id_usuario)).map(usuario => {
        let r = parseInt(usuario.color.slice(1, 3), 16)
        let g = parseInt(usuario.color.slice(3, 5), 16)
        let b = parseInt(usuario.color.slice(5, 7), 16)

        return {
            rojo: r,
            verde: g,
            azul: b
        }
    })
    
    color_usuarios = colores_rgb.shift()
    colores_rgb.forEach(color => {
        color_usuarios.rojo = (color_usuarios.rojo + color.rojo) / 2
        color_usuarios.verde = (color_usuarios.verde + color.verde) / 2
        color_usuarios.azul = (color_usuarios.azul + color.azul) / 2
    })
    color_usuarios = "#" + ((1 << 24) + (color_usuarios.rojo << 16) + (color_usuarios.verde << 8) + color_usuarios.azul).toString(16).slice(1);

    let dinero_gastado = 0
    let dinero_gastado_total = []
    datos.map(movimiento => {
        dinero_gastado = dinero_gastado + movimiento.monto
        dinero_gastado_total.push(dinero_gastado)
    })

    if (grafica) {grafica.destroy()}
    grafica = new Chart(
        document.getElementById("leer_datos_grafica"),
        {
            type: "line",
            data: {
                labels: datos.map(movimiento => movimiento.fecha),
                datasets: [{
                    label: "Flujo de Dinero",
                    data: datos.map(movimiento => movimiento.monto),
                    pointRadius: datos.map(() => 3),
                    pointBackgroundColor: datos.map(() => "#000000"),
                    borderColor: color_usuarios
                },
                {
                    label: "Gasto acumulado",
                    data: dinero_gastado_total,
                    pointRadius: datos.map(() => 3),
                    pointBackgroundColor: datos.map(() => "#000000"),
                    borderColor: invertir_color(color_usuarios)
                }
                ]
            }
        }
    )
}

// ======================================Codigo=============================================
crear_leer_datos_usuario()
crear_leer_datos_ubicacion()
crear_leer_datos_etiqueta()

const formulario = document.getElementById("leer_datos_enviar")
formulario.addEventListener("submit", leer_datos)