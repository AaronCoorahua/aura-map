// AuraMap: búsqueda de batallas por zona de Lima, publicación con pin en el mapa e inscripción.
const LIMA = [-12.0931, -77.0465];

const DISTRITOS = [
  ["Ate", -12.0256, -76.9186],
  ["Barranco", -12.1496, -77.0221],
  ["Breña", -12.0597, -77.0503],
  ["Cercado de Lima", -12.0464, -77.0428],
  ["Chorrillos", -12.1686, -77.0147],
  ["Comas", -11.9333, -77.05],
  ["Independencia", -11.99, -77.054],
  ["Jesús María", -12.0764, -77.0444],
  ["La Molina", -12.0866, -76.9352],
  ["La Victoria", -12.0708, -77.0167],
  ["Lince", -12.0839, -77.0356],
  ["Los Olivos", -11.992, -77.0706],
  ["Magdalena del Mar", -12.091, -77.069],
  ["Miraflores", -12.1211, -77.0297],
  ["Pueblo Libre", -12.0747, -77.0628],
  ["Rímac", -12.029, -77.028],
  ["San Borja", -12.1017, -76.9989],
  ["San Isidro", -12.0977, -77.0365],
  ["San Juan de Lurigancho", -11.9808, -77.0022],
  ["San Juan de Miraflores", -12.1575, -76.9711],
  ["San Martín de Porres", -12.005, -77.085],
  ["San Miguel", -12.0771, -77.0914],
  ["Santiago de Surco", -12.1453, -76.992],
  ["Surquillo", -12.1128, -77.02],
  ["Villa El Salvador", -12.2131, -76.9361],
].map(([nombre, lat, lng]) => ({ nombre, lat, lng }));

const ICONOS = {
  lugar: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 18s6-5.3 6-10a6 6 0 1 0-12 0c0 4.7 6 10 6 10z"/><circle cx="10" cy="8" r="2"/></svg>',
  reloj: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7"/><path d="M10 6v4l3 2"/></svg>',
  persona: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="7" r="3"/><path d="M4 17c0-3.3 2.7-5 6-5s6 1.7 6 5"/></svg>',
  ok: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3 3 7-7"/></svg>',
  error: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7"/><path d="M10 6.5v4M10 13.5v.01"/></svg>',
};

const estado = {
  batallas: [],
  centro: null,
  radioKm: 5,
  activa: null,
  inscribiendo: null,
};

const $ = (selector) => document.querySelector(selector);

function escapar(texto) {
  return String(texto).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

function fechaDe(batalla) {
  return new Date(batalla.fecha + "Z");
}

function formatoFecha(fecha) {
  const texto = fecha.toLocaleString("es-PE", {
    weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit",
  });
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function distanciaKm(a, b) {
  const rad = (g) => (g * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat);
  const dLng = rad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.sqrt(h));
}

function cuposLibres(batalla) {
  return Math.max(0, batalla.cupo - (batalla.inscritos || 0));
}

function avisar(mensaje, tipo = "ok") {
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.innerHTML = `${ICONOS[tipo]}<span>${escapar(mensaje)}</span>`;
  $("#toasts").appendChild(toast);
  setTimeout(() => toast.remove(), 3800);
}

// ---------- Mapa principal ----------
const TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const ATRIBUCION = '&copy; <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a>';

const mapa = L.map("mapa", { zoomControl: false }).setView(LIMA, 12);
L.control.zoom({ position: "bottomright" }).addTo(mapa);
L.tileLayer(TILES, { maxZoom: 19, attribution: ATRIBUCION }).addTo(mapa);

const capaBatallas = L.layerGroup().addTo(mapa);
const capaZona = L.layerGroup().addTo(mapa);
const marcadores = new Map();

function iconoPin(batalla, activo = false) {
  const clases = ["pin", cuposLibres(batalla) === 0 ? "lleno" : "", activo ? "activo" : ""].join(" ");
  return L.divIcon({
    className: "",
    html: `<span class="${clases}"></span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -32],
  });
}

function contenidoPopup(batalla) {
  const libres = cuposLibres(batalla);
  const boton = libres > 0
    ? `<button type="button" class="btn btn-primario btn-chico" data-inscribir="${batalla.id}">Inscribirme</button>`
    : '<button type="button" class="btn btn-secundario btn-chico" disabled>Sin cupos</button>';
  return `<div class="popup">
    <h3>${escapar(batalla.titulo)}</h3>
    <p>${escapar(formatoFecha(fechaDe(batalla)))}</p>
    <p>${escapar(batalla.distrito)} · ${escapar(batalla.direccion)}</p>
    <p>${libres} de ${batalla.cupo} cupos libres</p>
    ${boton}
  </div>`;
}

// ---------- Lista ----------
function tarjeta(batalla) {
  const fecha = fechaDe(batalla);
  const libres = cuposLibres(batalla);
  const ocupacion = Math.min(100, Math.round(((batalla.inscritos || 0) / batalla.cupo) * 100));
  const distancia = estado.centro
    ? `<span class="etiqueta">a ${distanciaKm(estado.centro, batalla).toFixed(1)} km</span>`
    : "";
  const permiso = batalla.tiene_permiso
    ? '<span class="etiqueta ok">Con permiso municipal</span>'
    : '<span class="etiqueta alerta">Sin permiso municipal</span>';
  const boton = libres > 0
    ? `<button type="button" class="btn btn-primario btn-chico" data-inscribir="${batalla.id}">Inscribirme</button>`
    : '<button type="button" class="btn btn-secundario btn-chico" disabled>Lleno</button>';

  const li = document.createElement("li");
  li.className = "tarjeta";
  li.dataset.id = batalla.id;
  li.tabIndex = 0;
  li.innerHTML = `
    <div class="fecha-bloque" aria-hidden="true">
      <span class="fecha-dia">${fecha.getDate()}</span>
      <span class="fecha-mes">${escapar(fecha.toLocaleString("es-PE", { month: "short" }).replace(".", ""))}</span>
    </div>
    <div>
      <h3>${escapar(batalla.titulo)}</h3>
      <p class="meta">${ICONOS.lugar}${escapar(batalla.distrito)} · ${escapar(batalla.direccion)}</p>
      <p class="meta">${ICONOS.reloj}${escapar(formatoFecha(fecha))}</p>
      <p class="meta">${ICONOS.persona}Organiza ${escapar(batalla.organizador)}</p>
      <div class="etiquetas">${permiso}${distancia}</div>
      <div class="tarjeta-pie">
        <div class="cupos">
          <div class="barra ${libres === 0 ? "llena" : ""}"><span style="width:${ocupacion}%"></span></div>
          <span class="cupos-texto">${libres === 0 ? "Cupos agotados" : `${libres} de ${batalla.cupo} cupos libres`}</span>
        </div>
        ${boton}
      </div>
    </div>`;
  return li;
}

function filtradas() {
  const soloCupo = $("#filtro-cupo").checked;
  const soloPermiso = $("#filtro-permiso").checked;
  return estado.batallas.filter((b) =>
    (!soloCupo || cuposLibres(b) > 0) && (!soloPermiso || b.tiene_permiso));
}

function textoZona() {
  const zona = $("#zona").value;
  if (!zona) return "en toda Lima";
  if (zona === "__cerca") return `a menos de ${estado.radioKm} km de ti`;
  return `a menos de ${estado.radioKm} km de ${zona}`;
}

function pintar() {
  const batallas = filtradas();
  const lista = $("#lista");
  lista.replaceChildren();
  capaBatallas.clearLayers();
  marcadores.clear();

  const n = batallas.length;
  $("#resumen").textContent = `${n} ${n === 1 ? "batalla" : "batallas"} ${textoZona()}`;

  if (n === 0) {
    lista.innerHTML = `<li class="vacio"><strong>No hay batallas por aquí todavía.</strong>
      Prueba con más distancia, otra zona, o publica la primera y farmea todo el aura.</li>`;
    return;
  }

  batallas.forEach((batalla) => {
    lista.appendChild(tarjeta(batalla));
    const marcador = L.marker([batalla.lat, batalla.lng], {
      icon: iconoPin(batalla, batalla.id === estado.activa),
      title: batalla.titulo,
      riseOnHover: true,
    }).bindPopup(contenidoPopup(batalla));
    marcador.on("click", () => marcarActiva(batalla.id, { desdeMapa: true }));
    marcador.addTo(capaBatallas);
    marcadores.set(batalla.id, marcador);
  });
}

function marcarActiva(id, { desdeMapa = false } = {}) {
  estado.activa = id;
  document.querySelectorAll(".tarjeta").forEach((el) => {
    el.classList.toggle("activa", Number(el.dataset.id) === id);
  });
  marcadores.forEach((marcador, idMarcador) => {
    const batalla = estado.batallas.find((b) => b.id === idMarcador);
    marcador.setIcon(iconoPin(batalla, idMarcador === id));
  });
  const marcador = marcadores.get(id);
  if (!marcador) return;
  if (desdeMapa) {
    document.querySelector(`.tarjeta[data-id="${id}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } else {
    mapa.flyTo(marcador.getLatLng(), Math.max(mapa.getZoom(), 14), { duration: 0.6 });
    marcador.openPopup();
  }
}

function dibujarZona() {
  capaZona.clearLayers();
  if (!estado.centro) return;
  L.circle([estado.centro.lat, estado.centro.lng], {
    radius: estado.radioKm * 1000,
    color: "#6a45ff",
    weight: 1.5,
    fillColor: "#6a45ff",
    fillOpacity: 0.06,
  }).addTo(capaZona);
  if ($("#zona").value === "__cerca") {
    L.marker([estado.centro.lat, estado.centro.lng], {
      icon: L.divIcon({ className: "", html: '<span class="pin-yo"></span>', iconSize: [18, 18] }),
      interactive: false,
    }).addTo(capaZona);
  }
}

function encuadrar() {
  if (estado.centro) {
    const circulo = L.circle([estado.centro.lat, estado.centro.lng], { radius: estado.radioKm * 1000 });
    circulo.addTo(mapa);
    mapa.flyToBounds(circulo.getBounds(), { padding: [30, 30], duration: 0.6 });
    circulo.remove();
  } else if (marcadores.size) {
    mapa.flyToBounds(L.featureGroup([...marcadores.values()]).getBounds(), { padding: [60, 60], maxZoom: 14, duration: 0.6 });
  } else {
    mapa.flyTo(LIMA, 12, { duration: 0.6 });
  }
}

async function cargar({ encuadre = true } = {}) {
  const lista = $("#lista");
  lista.innerHTML = '<li class="esqueleto"></li><li class="esqueleto"></li><li class="esqueleto"></li>';
  $("#resumen").textContent = "Buscando batallas...";

  const parametros = new URLSearchParams();
  if (estado.centro) {
    parametros.set("lat", estado.centro.lat);
    parametros.set("lng", estado.centro.lng);
    parametros.set("radius_km", estado.radioKm);
  }

  try {
    const respuesta = await fetch(`/api/battles?${parametros}`);
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error || "No pudimos cargar las batallas.");
    estado.batallas = datos;
  } catch (error) {
    estado.batallas = [];
    avisar(error.message || "No pudimos cargar las batallas.", "error");
  }
  pintar();
  dibujarZona();
  if (encuadre) encuadrar();
}

// ---------- Búsqueda ----------
function llenarDistritos(select) {
  DISTRITOS.forEach((d) => {
    const opcion = document.createElement("option");
    opcion.value = d.nombre;
    opcion.textContent = d.nombre;
    select.appendChild(opcion);
  });
}

llenarDistritos($("#zona-distritos"));
llenarDistritos($("#publicar-distrito"));

$("#zona").addEventListener("change", (evento) => {
  const zona = evento.target.value;
  $("#radio-busqueda").hidden = !zona;

  if (!zona) {
    estado.centro = null;
    cargar();
    return;
  }
  if (zona !== "__cerca") {
    const distrito = DISTRITOS.find((d) => d.nombre === zona);
    estado.centro = { lat: distrito.lat, lng: distrito.lng };
    cargar();
    return;
  }
  if (!navigator.geolocation) {
    avisar("Tu navegador no permite compartir la ubicación.", "error");
    evento.target.value = "";
    $("#radio-busqueda").hidden = true;
    return;
  }
  $("#resumen").textContent = "Obteniendo tu ubicación...";
  navigator.geolocation.getCurrentPosition(
    (posicion) => {
      estado.centro = { lat: posicion.coords.latitude, lng: posicion.coords.longitude };
      cargar();
    },
    () => {
      avisar("No pudimos obtener tu ubicación. Elige un distrito.", "error");
      evento.target.value = "";
      $("#radio-busqueda").hidden = true;
      estado.centro = null;
      cargar();
    },
    { enableHighAccuracy: true, timeout: 10000 },
  );
});

document.querySelectorAll("[data-radio]").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll("[data-radio]").forEach((c) => {
      c.classList.toggle("activo", c === chip);
      c.setAttribute("aria-checked", String(c === chip));
    });
    estado.radioKm = Number(chip.dataset.radio);
    cargar();
  });
});

["#filtro-cupo", "#filtro-permiso"].forEach((id) => {
  $(id).addEventListener("change", () => pintar());
});

$("#lista").addEventListener("click", (evento) => {
  const botonInscribir = evento.target.closest("[data-inscribir]");
  if (botonInscribir) {
    abrirInscripcion(Number(botonInscribir.dataset.inscribir));
    return;
  }
  const tarjetaEl = evento.target.closest(".tarjeta");
  if (tarjetaEl) marcarActiva(Number(tarjetaEl.dataset.id));
});

$("#lista").addEventListener("keydown", (evento) => {
  if (evento.key !== "Enter") return;
  const tarjetaEl = evento.target.closest(".tarjeta");
  if (tarjetaEl && evento.target === tarjetaEl) marcarActiva(Number(tarjetaEl.dataset.id));
});

mapa.getContainer().addEventListener("click", (evento) => {
  const boton = evento.target.closest("[data-inscribir]");
  if (boton) abrirInscripcion(Number(boton.dataset.inscribir));
});

// ---------- Diálogos ----------
document.querySelectorAll("dialog [data-cerrar]").forEach((boton) => {
  boton.addEventListener("click", () => boton.closest("dialog").close());
});

document.querySelectorAll("dialog").forEach((dialogo) => {
  dialogo.addEventListener("click", (evento) => {
    if (evento.target === dialogo) dialogo.close();
  });
});

// Inscripción
function abrirInscripcion(id) {
  const batalla = estado.batallas.find((b) => b.id === id);
  if (!batalla) return;
  estado.inscribiendo = batalla;
  mapa.closePopup();
  $("#inscripcion-batalla").textContent =
    `${batalla.titulo} · ${formatoFecha(fechaDe(batalla))} · ${cuposLibres(batalla)} cupos libres`;
  $("#error-inscripcion").textContent = "";
  $("#form-inscripcion").reset();
  $("#dlg-inscripcion").showModal();
  $("#form-inscripcion [name=nombre]").focus();
}

$("#form-inscripcion").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campo = evento.target.elements.nombre;
  const nombre = campo.value.trim();
  const error = $("#error-inscripcion");
  if (!nombre) {
    error.textContent = "Escribe tu nombre para inscribirte.";
    campo.setAttribute("aria-invalid", "true");
    campo.focus();
    return;
  }
  campo.removeAttribute("aria-invalid");

  const boton = $("#btn-inscribir");
  boton.disabled = true;
  try {
    const batalla = estado.inscribiendo;
    const respuesta = await fetch(`/api/battles/${batalla.id}/rsvp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre }),
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) {
      error.textContent = datos.error || "No pudimos inscribirte.";
      return;
    }
    $("#dlg-inscripcion").close();
    avisar(`Listo, ${datos.nombre}: estás dentro de "${batalla.titulo}". +1000 de aura.`);
    await cargar({ encuadre: false });
    marcarActiva(batalla.id, { desdeMapa: true });
  } catch {
    error.textContent = "Se cayó la conexión. Intenta de nuevo.";
  } finally {
    boton.disabled = false;
  }
});

// Publicación
const formPublicar = $("#form-publicar");
let mapaPublicar = null;
let pinPublicar = null;

function ponerPin(latlng) {
  if (pinPublicar) {
    pinPublicar.setLatLng(latlng);
  } else {
    pinPublicar = L.marker(latlng, {
      draggable: true,
      icon: L.divIcon({ className: "", html: '<span class="pin"></span>', iconSize: [34, 34], iconAnchor: [17, 34] }),
    }).addTo(mapaPublicar);
  }
  $("#ayuda-pin").textContent = "Arrastra el pin o toca el mapa para ajustar el lugar exacto.";
}

function prepararMapaPublicar() {
  if (!mapaPublicar) {
    mapaPublicar = L.map("mapa-publicar", { zoomControl: false }).setView(LIMA, 11);
    L.control.zoom({ position: "bottomright" }).addTo(mapaPublicar);
    L.tileLayer(TILES, { maxZoom: 19, attribution: ATRIBUCION }).addTo(mapaPublicar);
    mapaPublicar.on("click", (evento) => ponerPin(evento.latlng));
  }
  setTimeout(() => mapaPublicar.invalidateSize(), 60);
}

function manianaISO() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toLocaleDateString("en-CA");
}

$("#btn-abrir-publicar").addEventListener("click", () => {
  formPublicar.reset();
  formPublicar.elements.dia.min = new Date().toLocaleDateString("en-CA");
  formPublicar.elements.dia.value = manianaISO();
  $("#error-publicar").textContent = "";
  formPublicar.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
  $("#dlg-publicar").showModal();
  prepararMapaPublicar();
  if (pinPublicar) {
    pinPublicar.remove();
    pinPublicar = null;
  }
  mapaPublicar.setView(LIMA, 11);
  $("#ayuda-pin").textContent = "Elige un distrito y luego toca el mapa o arrastra el pin hasta el lugar exacto.";
});

formPublicar.addEventListener("input", (evento) => {
  if (String(evento.target.value).trim()) evento.target.removeAttribute("aria-invalid");
  $("#error-publicar").textContent = "";
});

$("#form-inscripcion").addEventListener("input", (evento) => {
  evento.target.removeAttribute("aria-invalid");
  $("#error-inscripcion").textContent = "";
});

$("#publicar-distrito").addEventListener("change", (evento) => {
  const distrito = DISTRITOS.find((d) => d.nombre === evento.target.value);
  if (!distrito) return;
  mapaPublicar.setView([distrito.lat, distrito.lng], 15);
  ponerPin([distrito.lat, distrito.lng]);
});

function validarPublicacion(campos) {
  const obligatorios = ["titulo", "dia", "hora", "cupo", "organizador", "distrito", "direccion"];
  let primero = null;
  obligatorios.forEach((nombre) => {
    const el = campos[nombre];
    const vacio = !String(el.value).trim();
    if (vacio) {
      el.setAttribute("aria-invalid", "true");
      primero = primero || el;
    } else {
      el.removeAttribute("aria-invalid");
    }
  });
  if (primero) {
    primero.focus();
    return "Completa los campos marcados.";
  }
  const cupo = Number(campos.cupo.value);
  if (!Number.isInteger(cupo) || cupo < 1 || cupo > 100) return "Los cupos deben estar entre 1 y 100.";
  if (new Date(`${campos.dia.value}T${campos.hora.value}`) <= new Date()) return "La fecha y hora deben ser futuras.";
  if (!pinPublicar) return "Marca en el mapa dónde será la batalla.";
  return null;
}

formPublicar.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campos = formPublicar.elements;
  const error = $("#error-publicar");
  const problema = validarPublicacion(campos);
  if (problema) {
    error.textContent = problema;
    return;
  }
  error.textContent = "";

  const posicion = pinPublicar.getLatLng();
  const cuerpo = {
    titulo: campos.titulo.value.trim(),
    descripcion: campos.descripcion.value.trim(),
    distrito: campos.distrito.value,
    direccion: campos.direccion.value.trim(),
    lat: Number(posicion.lat.toFixed(6)),
    lng: Number(posicion.lng.toFixed(6)),
    fecha: new Date(`${campos.dia.value}T${campos.hora.value}`).toISOString(),
    cupo: Number(campos.cupo.value),
    organizador: campos.organizador.value.trim(),
    tiene_permiso: campos.tiene_permiso.checked,
  };

  const boton = $("#btn-publicar");
  boton.disabled = true;
  try {
    const respuesta = await fetch("/api/battles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) {
      error.textContent = datos.error || "No pudimos publicar la batalla.";
      return;
    }
    $("#dlg-publicar").close();
    avisar(`"${datos.titulo}" ya está en el mapa. Que empiece el aura farming.`);
    $("#zona").value = "";
    $("#radio-busqueda").hidden = true;
    estado.centro = null;
    await cargar({ encuadre: false });
    marcarActiva(datos.id);
  } catch {
    error.textContent = "Se cayó la conexión. Intenta de nuevo.";
  } finally {
    boton.disabled = false;
  }
});

cargar();
