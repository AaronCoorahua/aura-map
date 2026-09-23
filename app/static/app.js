// Mapa de batallas de aura: consulta la API y pinta un marcador por batalla.
const LIMA = [-12.121, -77.029];

const mapa = L.map("mapa").setView(LIMA, 12);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; colaboradores de OpenStreetMap",
}).addTo(mapa);

const capaBatallas = L.layerGroup().addTo(mapa);
const resultado = document.getElementById("resultado");
const avisoPublicar = document.getElementById("aviso-publicar");

function textoFecha(iso) {
  return new Date(iso + "Z").toLocaleString("es-PE");
}

function pintar(batallas) {
  capaBatallas.clearLayers();
  batallas.forEach((batalla) => {
    const permiso = batalla.tiene_permiso ? "con permiso municipal" : "sin permiso municipal";
    L.marker([batalla.lat, batalla.lng])
      .bindPopup(
        `<strong>${batalla.titulo}</strong><br>` +
          `${batalla.distrito} — ${batalla.direccion}<br>` +
          `${textoFecha(batalla.fecha)}<br>` +
          `Cupo: ${batalla.cupo} · ${permiso}<br>` +
          `Organiza: ${batalla.organizador}`
      )
      .addTo(capaBatallas);
  });
  resultado.textContent = `${batallas.length} batalla(s) encontradas.`;
}

async function cargar(parametros) {
  const url = parametros ? `/api/battles?${parametros}` : "/api/battles";
  const respuesta = await fetch(url);
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    resultado.textContent = datos.error;
    return;
  }
  pintar(datos);
}

document.getElementById("form-busqueda").addEventListener("submit", (evento) => {
  evento.preventDefault();
  const campos = new FormData(evento.target);
  if (!campos.get("district")) {
    campos.delete("district");
  }
  const parametros = new URLSearchParams(campos);
  mapa.setView([campos.get("lat"), campos.get("lng")], 13);
  cargar(parametros.toString());
});

document.getElementById("btn-todas").addEventListener("click", () => cargar());

document.getElementById("form-publicar").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campos = new FormData(evento.target);
  const cuerpo = {
    titulo: campos.get("titulo"),
    descripcion: campos.get("descripcion") || "",
    distrito: campos.get("distrito"),
    direccion: campos.get("direccion"),
    lat: Number(campos.get("lat")),
    lng: Number(campos.get("lng")),
    // El input entrega hora local; la API trabaja en UTC.
    fecha: new Date(campos.get("fecha")).toISOString(),
    cupo: Number(campos.get("cupo")),
    organizador: campos.get("organizador"),
    tiene_permiso: campos.get("tiene_permiso") === "on",
  };

  const respuesta = await fetch("/api/battles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  const datos = await respuesta.json();

  if (!respuesta.ok) {
    avisoPublicar.textContent = datos.error;
    return;
  }
  avisoPublicar.textContent = `Batalla "${datos.titulo}" publicada.`;
  evento.target.reset();
  cargar();
});

cargar();
