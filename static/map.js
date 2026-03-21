// --- GLOBAL VARIABLES ---
let lastClickedPoint = null; // Store the last clicked track point

// Helper function to format values based on units
function formatValue(value, type, units) {
  if (value == null) return "";

  switch (type) {
    case "speed": // value in m/s
      return units === "imperial"
        ? `${(value * 2.23694).toFixed(2)} mph`
        : `${(value * 3.6).toFixed(2)} km/h`;
    case "elevation": // value in meters
      return units === "imperial"
        ? `${(value * 3.28084).toFixed(2)} ft`
        : `${value.toFixed(2)} m`;
    default:
      return value;
  }
}

// Function to render the track info panel
function renderTrackPanel(point) {
  if (!point) return;

  const panel = document.getElementById("track-details");
  const userUnits = sessionStorage.getItem("units") || "metric";

  panel.innerHTML = `

    <h3>Track Point</h3>

    <div class="unit-toggle">
    <span>Units:</span>
    <button type="button" class="unit-btn" data-unit="metric">Metric</button>
    <button type="button" class="unit-btn" data-unit="imperial">Imperial</button>
  </div>
  
    ${point.lat != null ? `<p><b>Latitude:</b> ${point.lat}</p>` : ""}
    ${point.lon != null ? `<p><b>Longitude:</b> ${point.lon}</p>` : ""}
    ${point.speed != null ? `<p><b>Speed:</b> ${formatValue(point.speed, "speed", userUnits)}</p>` : ""}
    ${point.ele != null ? `<p><b>Elevation:</b> ${formatValue(point.ele, "elevation", userUnits)}</p>` : ""}
    ${point.time != null ? `<p><b>Time:</b> ${point.time}</p>` : ""}
    ${point.course != null ? `<p><b>Course:</b> ${point.course}</p>` : ""}
    ${point.geoidheight != null ? `<p><b>Geoid Height:</b> ${point.geoidheight}</p>` : ""}
    ${point.src != null ? `<p><b>Source:</b> ${point.src}</p>` : ""}
    ${point.sat != null ? `<p><b>Satellites:</b> ${point.sat}</p>` : ""}
    ${point.hdop != null ? `<p><b>HDOP:</b> ${point.hdop}</p>` : ""}
    ${point.vdop != null ? `<p><b>VDOP:</b> ${point.vdop}</p>` : ""}
    ${point.pdop != null ? `<p><b>PDOP:</b> ${point.pdop}</p>` : ""}
  `; 
}

// --- MAP INITIALIZATION ---
function initMap(pathData, trackInfo) {
  // 1. Base layers
  const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  });
  const esriSat = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri" }
  );
  const dark = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; Carto",
  });

  // 2. Create map
  const map = L.map("map", { center: [0, 0], zoom: 1, layers: [osm] });

  // 3. Layer groups
  const trackLayer = L.layerGroup().addTo(map);
  const uiLayer = L.layerGroup().addTo(map);

  // 4. Draw track polyline
  if (pathData.length > 0) {
  const latlngs = pathData.map((p) => [p.lat, p.lon]);
  const polyline = L.polyline(latlngs, { color: "orange", weight: 7, opacity: 1 }).addTo(trackLayer);

  // Start and end markers
  L.marker([pathData[0].lat, pathData[0].lon]).addTo(uiLayer).bindPopup("Start");
  L.marker([pathData[pathData.length - 1].lat, pathData[pathData.length - 1].lon])
    .addTo(uiLayer)
    .bindPopup("End");

  // Clickable markers with hover effect on radius
  pathData.forEach((point) => {
    const marker = L.circleMarker([point.lat, point.lon], {
      radius: 3,
      color: "orange",
      weight: 1,
      fillOpacity: 1,
    }).addTo(trackLayer);

    // Hover effect: increase radius
    marker.on("mouseover", () => marker.setStyle({ radius: 10, color: 'yellow'}));
    marker.on("mouseout", () => marker.setStyle({ radius: 3, color: 'orange'}));

    // Click event for track panel
    marker.on("click", () => {
      lastClickedPoint = point;       // save clicked point
      renderTrackPanel(point);        // render panel
    });
  });

  map.fitBounds(polyline.getBounds());
}

  // 5. Layer control
  const baseLayers = { OSM: osm, Satellite: esriSat, Dark: dark };
  L.control.layers(baseLayers).addTo(map);

  // 6. Unit toggle buttons
  document.getElementById("track-details").addEventListener("click", (e) => {
  if (e.target.classList.contains("unit-btn")) {
    const newUnit = e.target.dataset.unit;
    sessionStorage.setItem("units", newUnit);
    renderTrackPanel(lastClickedPoint);
  }
});
  btn.addEventListener("click", (e) => {
  const newUnit = e.currentTarget.dataset.unit;

  // update frontend
  sessionStorage.setItem("units", newUnit);

  // update backend + reload page
  window.location.href = `/set_units/${newUnit}`;
});
}

// --- INIT CALL ---
initMap(pathData, trackInfo);