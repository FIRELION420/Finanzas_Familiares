async function crear_opciones_id_padre() {
    const respuesta = await fetch("/leer_etiquetas")
    const etiquetas = await respuesta.json()
    const contenedor_etiquetas = document.getElementById("crear_etiqueta_padre_lista")

    etiquetas.forEach(fila => {
        let opcion = document.createElement("option")
        opcion.value = fila.etiqueta

        contenedor_etiquetas.appendChild(opcion)
    });
}

async function etiqueta_enviar() {
    if (document.getElementById("crear_etiqueta").value) {

        const mensaje = {
            etiqueta: document.getElementById("crear_etiqueta").value,
            etiqueta_padre: document.getElementById("crear_etiqueta_padre").value
        }

        await fetch("/crear_etiqueta", {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": JSON.stringify(mensaje)
        })
    }
}

crear_opciones_id_padre()
const formulario_etiquetas = document.getElementById("crear_etiqueta_enviar")
formulario_etiquetas.addEventListener("submit", etiqueta_enviar)