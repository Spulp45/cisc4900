
// MAP INITIALIZATION
function initMap(pathData, trackInfo) {
  // --- 1. Base layers ---
  const osm = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    { attribution: "&copy; OpenStreetMap contributors" }
  );

  const esriSat = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri" }
  );

  const dark = L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    { attribution: "&copy; OpenStreetMap &copy; Carto" }
  );

  // --- 2. Create map ---
  const map = L.map("map", {
    center: [0, 0],
    zoom: 2,
    layers: [osm],
  });

  // --- 3. Layer groups ---
  const trackLayer = L.layerGroup().addTo(map);
  const uiLayer = L.layerGroup().addTo(map);


  // DRAW TRACK POLYLINE
  if (pathData.length > 0) {
    const latlngs = pathData.map((p) => [p.lat, p.lon]);

    const polyline = L.polyline(latlngs, {
      color: "red",
      weight: 5,
      opacity: 1,
      interactive: true,
    }).addTo(trackLayer);

    // Hover effect
    polyline.on("mouseover", function () { this.setStyle({ color: "blue", weight: 7 }); });
    polyline.on("mouseout", function () { this.setStyle({ color: "red", weight: 5 }); });

    // --- Start marker ---
    L.marker([pathData[0].lat, pathData[0].lon]).addTo(uiLayer).bindPopup("Start");

    // --- End marker ---
    L.marker([pathData[pathData.length - 1].lat, pathData[pathData.length - 1].lon])
      .addTo(uiLayer)
      .bindPopup("End");

    // --- Clickable markers for all points ---
    pathData.forEach((point) => {
      const marker = L.circleMarker([point.lat, point.lon], {
        radius: 4,
        color: "red",
        weight: 1,
        fillOpacity: 0.8,
      }).addTo(trackLayer);

      marker.on("click", () => {
        const panel = document.getElementById("track-details");
        panel.innerHTML = `
          <h3>Track Point</h3>
          ${point.lat != null ? `<p><b>Latitude:</b> ${point.lat}</p>` : ""}
          ${point.lon != null ? `<p><b>Longitude:</b> ${point.lon}</p>` : ""}
          ${point.speed != null ? `<p><b>Speed:</b> ${point.speed}</p>` : ""}
          ${point.time != null ? `<p><b>Speed:</b> ${point.speed}</p>` : ""}
          ${point.ele != null ? `<p><b>Elevation:</b> ${point.ele}</p>` : ""}
          ${point.time != null ? `<p><b>Time:</b> ${point.time}</p>` : ""}
          ${point.course != null ? `<p><b>Course:</b> ${point.course}</p>` : ""}
          ${point.geoidheight != null ? `<p><b>Geoid Height:</b> ${point.geoidheight}</p>` : ""}
          ${point.src != null ? `<p><b>Source:</b> ${point.src}</p>` : ""}
          ${point.sat != null ? `<p><b>Satellites:</b> ${point.sat}</p>` : ""}
          ${point.hdop != null ? `<p><b>HDOP:</b> ${point.hdop}</p>` : ""}
          ${point.vdop != null ? `<p><b>VDOP:</b> ${point.vdop}</p>` : ""}
          ${point.pdop != null ? `<p><b>PDOP:</b> ${point.pdop}</p>` : ""}
        `;
      });
    });

    // Fit map to track bounds
    map.fitBounds(polyline.getBounds());
  }


  // LAYER CONTROL
  const baseLayers = {
    OSM: osm,
    Satellite: esriSat,
    Dark: dark,
  };
  L.control.layers(baseLayers).addTo(map);
}

// INIT CALL
initMap(pathData, trackInfo);