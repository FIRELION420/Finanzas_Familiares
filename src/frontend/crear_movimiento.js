// ================================Variables===========================================
let ubicacion
let etiqueta

// ================================Funciones===========================================
async function crear_seleccionar_usuario() {

    const respuesta = await fetch("/leer_usuarios");
    const usuarios = await respuesta.json();
    const nombres = usuarios.map(usuarios => usuarios.nombre);

    nombres.forEach(nombre => {
        const seleccionar_nombre = document.getElementById("crear_movimiento_usuario");
        seleccionar_nombre.add(new Option(`${nombre}`, `${nombre}`))
    });
}

function crear_arbol (contenedor, padres, elementos, id_elemento, nombre_elemento) {

    const hijos = elementos.filter(elemento => padres.some(padre => padre[id_elemento] == elemento.id_padre))

    if (hijos.length === 0) {
        return
    }

    hijos.forEach(hijo => {

        const elemento = document.createElement("ul")
        elemento.id = `id_${id_elemento}_${hijo[id_elemento]}`
        elemento.name = hijo[nombre_elemento]
        
        const flecha = document.createElement("span")
        flecha.className = "arbol_flecha"
        flecha.textContent = "▸"

        const cajita = document.createElement("span")
        cajita.className = "arbol_cajita"

        const texto = document.createElement("span")
        texto.className = "arbol_texto"
        texto.textContent = hijo[nombre_elemento]

        elemento.appendChild(flecha)
        elemento.appendChild(cajita)
        elemento.appendChild(texto)

        if (hijo.id_padre == null) {
            contenedor.appendChild(elemento)
        }
        else {
            document.getElementById(`id_${id_elemento}_${hijo.id_padre}`).appendChild(elemento)
        }
    })
    crear_arbol(contenedor, hijos, elementos, id_elemento, nombre_elemento)
}

async function crear_seleccionar_ubicacion() {

    const respuesta = await fetch("/leer_ubicaciones");
    const ubicaciones = await respuesta.json()
    
    const seleccionar_ubicacion = document.getElementById("crear_movimiento_ubicacion")
    const padres = {}

    crear_arbol(seleccionar_ubicacion, [{"id_ubicacion": null}], ubicaciones, "id_ubicacion", "nombre")

    seleccionar_ubicacion.addEventListener("click", evento => {
        if (evento.target.classList.contains("arbol_flecha")) {
            evento.target.closest("ul").classList.toggle("colapsada")
            return
        }
        if (evento.target.classList.contains("arbol_cajita") || evento.target.classList.contains("arbol_texto")) {
            const nodo = evento.target.closest("ul")
            const anterior = seleccionar_ubicacion.querySelector(".arbol_cajita.seleccionada")
            if (anterior) {
                anterior.classList.remove("seleccionada")
            }
            nodo.querySelector(":scope > .arbol_cajita").classList.add("seleccionada")
            ubicacion = nodo.name
        }
    })
}

async function crear_seleccionar_etiqueta() {

    const respuesta = await fetch("/leer_etiquetas");
    const etiquetas = await respuesta.json()
    
    const seleccionar_etiqueta = document.getElementById("crear_movimiento_etiqueta")
    const padres = {}

    crear_arbol(seleccionar_etiqueta, [{"id_etiqueta": null}], etiquetas, "id_etiqueta", "etiqueta")

    seleccionar_etiqueta.addEventListener("click", evento => {
        if (evento.target.classList.contains("arbol_flecha")) {
            evento.target.closest("ul").classList.toggle("colapsada")
            return
        }
        if (evento.target.classList.contains("arbol_cajita") || evento.target.classList.contains("arbol_texto")) {
            const nodo = evento.target.closest("ul")
            const anterior = seleccionar_etiqueta.querySelector(".arbol_cajita.seleccionada")
            if (anterior) {
                anterior.classList.remove("seleccionada")
            }
            nodo.querySelector(":scope > .arbol_cajita").classList.add("seleccionada")
            etiqueta = nodo.name
        }
    })
}

async function crear_movimiento(evento) {
    evento.preventDefault()
    
    // Verificar que el monto sea correcto
    let monto = document.getElementById("crear_movimiento_monto").value

    if (/\d+\.\d{2}/.test(monto) != true){
        const valores = monto.split(".")

        if (valores == "") {
            alert("Solo se ingreso '.'")
            return
        }

        if (valores.length < 2) {
            monto = valores[0] + ".00"
        }
        else{
            if (valores[1].length > 2) {
                alert("Se ingresaron mas de 2 decimales")
                return
            }
            let cantidad = valores[1].length
            while (cantidad < 2) {
                valores[1] = valores[1] + "0"
                cantidad = valores[1].length
            }
            if (valores[0] == "") {
                monto = "0." + valores[1]
            }
        }  
    }
        // Crear objeto con los datos a enviar
        const mensaje = {
            "usuario": document.getElementById("crear_movimiento_usuario").value,
            "ubicacion": ubicacion,
            "descripcion": document.getElementById("crear_movimiento_descripcion").value,
            "monto": monto,
            "tipo": document.getElementById("crear_movimiento_tipo").value,
            "fecha": document.getElementById("crear_movimiento_fecha").value.replace("T", " "),
            "nota": document.getElementById("crear_movimiento_nota").value,
            "calidad": calidad_valor,
            "etiqueta": etiqueta
        }
        const confirmacion = document.getElementById("crear_movimiento_confirmacion")
        confirmacion.innerHTML = `
            <li>Usuario: ${mensaje.usuario}</li>
            <li>Ubicacion: ${mensaje.ubicacion}</li>
            <li>Descripción: ${mensaje.descripcion}</li>
            <li>Monto: ${mensaje.monto}</li>
            <li>Tipo de movimiento: ${mensaje.tipo}</li>
            <li>Fecha: ${mensaje.fecha}</li>
            <li>Nota: ${mensaje.nota}</li>
            <li>Calidad: ${mensaje.calidad}</li>
            <li>Etiqueta: ${mensaje.etiqueta}</li>
            <input type="button" id="rechazar" value="Me equivoque en algo :p">
            <input type="button" id="confirmar" value="Si es correcto :)">
        `
        document.getElementById("rechazar").addEventListener("click", () => {confirmacion.innerHTML = ""})
        document.getElementById("confirmar").addEventListener("click", async () => {
            await fetch("/crear_movimiento", {
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": JSON.stringify(mensaje)
            })

            document.getElementById("crear_movimiento_enviar").reset()
            calidad_valor = null
            calidad_display.textContent  = "Calidad: "
            confirmacion.innerHTML = ""
            document.querySelectorAll(".arbol_cajita.seleccionada").forEach(cajita => cajita.classList.remove("seleccionada"))
            ubicacion = undefined
            etiqueta = undefined
        })
}

crear_seleccionar_usuario()
crear_seleccionar_ubicacion()
crear_seleccionar_etiqueta()

const  rango = document.getElementById("crear_movimiento_calidad")
const calidad_display = document.getElementById("crear_movimiento_display_calidad")
let calidad_valor = null

rango.addEventListener("change", () => {
    calidad_display.textContent  = "Calidad: " + rango.value
    calidad_valor = Number(rango.value)
})

const formulario_crear_movimiento = document.getElementById("crear_movimiento_enviar")
formulario_crear_movimiento.addEventListener("submit", crear_movimiento)