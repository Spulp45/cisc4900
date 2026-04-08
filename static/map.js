let lastClickedPoint = null;

// Retrieve current unit setting
function getUnits() {
  return sessionStorage.getItem("units") || "metric";
}
// Store selected unit setting
function setUnits(unit) {
  sessionStorage.setItem("units", unit);
}
// Format values base on type and unit setting
function formatValue(value, type, units) {
  if (value == null) return "";
  if (units === "raw") return value;

  switch (type) {
    case "speed":
      return units === "imperial"
        ? `${(value * 2.23694).toFixed(2)} mph`
        : `${(value * 3.6).toFixed(2)} km/h`;
    case "distance":
      return units === "imperial"
        ? `${(value * 0.000621371).toFixed(2)} mi`
        : `${(value / 1000).toFixed(2)} km`;
    case "elevation":
      return units === "imperial"
        ? `${(value * 3.28084).toFixed(2)} ft`
        : `${value.toFixed(2)} m`;
    case "time":
      const h = Math.floor(value / 3600);
      const m = Math.floor((value % 3600) / 60);
      const s = Math.floor(value % 60);
      return `${h}:${m.toString().padStart(2, "0")}:${s
        .toString()
        .padStart(2, "0")}`;
    default:
      return value;
  }
}

// Display info for a single track_point
function renderTrackPanel(point) {
  if (!point) return;

  const panel = document.getElementById("track-details");
  const userUnits = getUnits();

  panel.innerHTML = `
    <h3>Track Point</h3>

    ${point.lat != null ? `<p><b>Latitude:</b> ${point.lat}</p>` : ""}
    ${point.lon != null ? `<p><b>Longitude:</b> ${point.lon}</p>` : ""}
    ${point.speed != null ? `<p><b>Speed:</b> ${formatValue(point.speed, "speed", userUnits)}</p>` : ""}
    ${point.ele != null ? `<p><b>Elevation:</b> ${formatValue(point.ele, "elevation", userUnits)}</p>` : ""}
    ${point.timestamp != null ? `<p><b>Time:</b> ${point.timestamp}</p>` : ""}
    ${point.course != null ? `<p><b>Course:</b> ${point.course}</p>` : ""}
    ${point.geoidheight != null ? `<p><b>Geoid Height:</b> ${point.geoidheight}</p>` : ""}
    ${point.src != null ? `<p><b>Source:</b> ${point.src}</p>` : ""}
    ${point.sat != null ? `<p><b>Satellites:</b> ${point.sat}</p>` : ""}
    ${point.hdop != null ? `<p><b>HDOP:</b> ${point.hdop}</p>` : ""}
    ${point.vdop != null ? `<p><b>VDOP:</b> ${point.vdop}</p>` : ""}
    ${point.pdop != null ? `<p><b>PDOP:</b> ${point.pdop}</p>` : ""}
  `;
}
// Display overall info for the track
function renderStatsTable(track, units) {
  const table = document.getElementById("stats-table");

  table.innerHTML = `
    <div class="unit-toggle">
      <span>Units:</span>
      <button type="button" class="unit-btn" data-unit="metric">Metric</button>
      <button type="button" class="unit-btn" data-unit="imperial">Imperial</button>
      <button type="button" class="unit-btn" data-unit="raw">Raw</button>
    </div>
    <tr><th>Data</th><th>Value</th></tr>
    <tr><td>Average Moving Speed</td><td>${formatValue(track.avg_speed, "speed", units)}</td></tr>
    <tr><td>Total Distance 2D</td><td>${formatValue(track.length_2d, "distance", units)}</td></tr>
    <tr><td>Total Distance 3D</td><td>${formatValue(track.length_3d, "distance", units)}</td></tr>
    <tr><td>Moving Time</td><td>${formatValue(track.moving_time, "time", units)}</td></tr>
    <tr><td>Stopped Time</td><td>${formatValue(track.stopped_time, "time", units)}</td></tr>
    <tr><td>Moving Distance</td><td>${formatValue(track.moving_distance, "distance", units)}</td></tr>
    <tr><td>Stopped Distance</td><td>${formatValue(track.stopped_distance, "distance", units)}</td></tr>
    <tr><td>Max Speed</td><td>${formatValue(track.max_speed, "speed", units)}</td></tr>
    <tr><td>Average Speed</td><td>${formatValue(track.avg_speed, "speed", units)}</td></tr>
    <tr><td>Uphill</td><td>${formatValue(track.uphill, "elevation", units)}</td></tr>
    <tr><td>Downhill</td><td>${formatValue(track.downhill, "elevation", units)}</td></tr>
    <tr><td>Start Time</td><td>${track.start_time}</td></tr>
    <tr><td>End Time</td><td>${track.end_time}</td></tr>
    <tr><td>Points</td><td>${track.points}</td></tr>
    <tr><td>Filename</td><td>${track.filename}</td></tr>
    <tr><td>Filepath</td><td>${track.filepath}</td></tr>
    <tr><td>GPX Version</td><td>${track.gpx_version}</td></tr>
  `;
}

// Handle clicks
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("unit-btn")) {
    const unit = e.target.dataset.unit;
    setUnits(unit);
    renderStatsTable(track, unit);
    if (lastClickedPoint) renderTrackPanel(lastClickedPoint);
  }
});

// Initialize Map
function initMap(track_points) {
  const osm = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      attribution: "&copy; OpenStreetMap contributors",
      maxNativeZoom: 19,
      maxZoom: 23,
    },
  );
  const esriSat = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri", maxNativeZoom: 23, maxZoom: 25 },
  );
  const dark = L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    {
      attribution: "&copy; OpenStreetMap &copy; Carto",
      maxNativeZoom: 19,
      maxZoom: 23,
    },
  );

const map = L.map("map", {
    center: [0, 0],
    zoom: 13,
    maxZoom: 23,
    layers: [osm],
    scrollWheelZoom: true,
    fullscreenControl: true,
    fullscreenControlOptions: {     
        position: 'bottomright'
    }
});

  L.control
    .scale({
      position: "bottomleft",
      metric: true,
      imperial: true,
      updateWhenIdle: true,
      maxWidth: 150,
    })
    .addTo(map);

    

  let polylineLayer = null;
  const trackPointsLayer = L.layerGroup();
  const minZoomForTrackPoints = 14;

  if (track_points.length > 0) {
    const latlngs = track_points.map((p) => [p.lat, p.lon]);
    polylineLayer = L.polyline(latlngs, {
      color: "#008e00",
      weight: 7,
      opacity: 1,
    }).addTo(map);

    L.marker([track_points[0].lat, track_points[0].lon])
      .addTo(map)
      .bindPopup("Start");
    L.marker([
      track_points[track_points.length - 1].lat,
      track_points[track_points.length - 1].lon,
    ])
      .addTo(map)
      .bindPopup("End");
  }

  function renderTrackPoints() {
    trackPointsLayer.clearLayers();
    const zoom = map.getZoom();
    if (zoom < minZoomForTrackPoints) return;

    const radius = zoom < 18 ? 3 : 6;

    track_points.forEach((point) => {
      const marker = L.circleMarker([point.lat, point.lon], {
        radius: radius,
        color: "#1f3145",
        weight: 1,
        fillOpacity: 0.7,
      });
      marker.on("mouseover", () =>
        marker.setStyle({ radius: radius + 10, color: "yellow" }),
      );
      marker.on("mouseout", () =>
        marker.setStyle({ radius: radius, color: "#1f3145" }),
      );
      marker.on("click", () => {
        lastClickedPoint = point;
        renderTrackPanel(point);
      });
      trackPointsLayer.addLayer(marker);
    });

    if (!map.hasLayer(trackPointsLayer)) map.addLayer(trackPointsLayer);
  }

  map.on("zoomend", renderTrackPoints);
  renderTrackPoints();

  const baseLayers = { OSM: osm, Satellite: esriSat, Dark: dark };
  const overlayLayers = { "Track Points": trackPointsLayer };
  L.control.layers(baseLayers, overlayLayers).addTo(map);

  if (polylineLayer) map.fitBounds(polylineLayer.getBounds());
  console.log("Initial zoom:", map.getZoom());
}

// Start the map and render table
initMap(track_points, track);
const units = getUnits();
renderStatsTable(track, units);
