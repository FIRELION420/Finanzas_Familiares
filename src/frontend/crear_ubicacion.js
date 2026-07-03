// Crear mapa
const mapa = L.map('mapa', {
    closePopupOnClick: false,
    center: [32.487552, -116.931138],
    zoom: 13
})
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa)

const provedor = new GeoSearch.OpenStreetMapProvider({
    params: {
        viewbox: [-117.30, 32.65, -116.75, 32.30].join(','),
        bounded: 0,
        addressdetails: 1,
        countrycodes: 'mx',
        'accept-language': "es"
    }
  })
const search = new GeoSearch.GeoSearchControl({
  notFoundMessage: 'No se pudo encontrar esa ubicación D:',
  provider: provedor,
  style: 'bar'
});

mapa.addControl(search)


// Eventos
let marcador = null
let coordenadas

mapa.on('click', (evento) => {
    if (marcador !== null) {
        marcador.remove()
    }
    coordenadas = evento.latlng
    marcador = L.marker([coordenadas.lat, coordenadas.lng]).addTo(mapa)
})

const boton_mapa = document.getElementById("mapa_enviar")
boton_mapa.addEventListener("click", () => {
    if (marcador !== null) {
        const confirmacion = document.getElementById("mapa_confirmacion")
        confirmacion.innerHTML = `
        <input type="text" id="mapa_confirmacion_nombre">
        <input type="button" id="mapa_confirmacion_boton" value="Enviar el nombre y ubicacion">
        `
        const boton_confirmacion = document.getElementById("mapa_confirmacion_boton")
        boton_confirmacion.addEventListener("click", () => {
            
            let nombre = document.getElementById("mapa_confirmacion_nombre").value
            if (nombre) {
            const mensaje = {
                    "nombre": nombre,
                    "latitud": coordenadas.lat,
                    "longitud": coordenadas.lng
                }
            fetch("/crear_ubicacion", {
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": JSON.stringify(mensaje),
            })

            mapa.setView([32.487552, -116.931138], 13)
            marcador.remove()
            }
            else {
                alert("No se ingreso nombre")
            }
    })
    }
    else {
        alert("No se agrego ningun lugar")
    }
})

