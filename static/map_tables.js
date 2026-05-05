
    // 1. Global Variables
    let map; 
    let lastClickedPoint = null;
    let isPlaying = false;
    let animationIndex = 0;
    let carMarker = null;

    // 2. Unit Management (Original)
    function getUnits() { return sessionStorage.getItem("units") || "metric"; }
    function setUnits(unit) { sessionStorage.setItem("units", unit); }

    function formatValue(value, type, units) {
        if (value == null) return "";
        if (units === "raw") return value;
        switch (type) {
            case "speed": return units === "imperial" ? `${(value * 2.23694).toFixed(2)} mph` : `${(value * 3.6).toFixed(2)} km/h`;
            case "distance": return units === "imperial" ? `${(value * 0.000621371).toFixed(2)} mi` : `${(value / 1000).toFixed(2)} km`;
            case "elevation": return units === "imperial" ? `${(value * 3.28084).toFixed(2)} ft` : `${value.toFixed(2)} m`;
            case "time":
                const h = Math.floor(value / 3600);
                const m = Math.floor((value % 3600) / 60);
                const s = Math.floor(value % 60);
                return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
            case "timestamp": return new Date(value).toLocaleString();
            default: return value;
            case "misc": return value;
        }
    }

    // 3. UI Rendering (Original)
    function renderTrackPanel(point) {
        if (!point) return;
        const panel = document.getElementById("point-readout");
        const userUnits = getUnits();
        panel.innerHTML = `<h3>Track Point</h3>
            ${point.lat != null ? `<p><b>Latitude:</b> ${point.lat}</p>` : ""}
            ${point.lon != null ? `<p><b>Longitude:</b> ${point.lon}</p>` : ""}
            ${point.speed != null ? `<p><b>Speed:</b> ${formatValue(point.speed, "speed", userUnits)}</p>` : ""}
            ${point.ele != null ? `<p><b>Elevation:</b> ${formatValue(point.ele, "elevation", userUnits)}</p>` : ""}
            ${point.timestamp != null ? `<p><b>Time:</b> ${formatValue(point.timestamp, "timestamp", userUnits)}</p>` : ""}
            ${point.course != null ? `<p><b>Course:</b> ${point.course}</p>` : ""}`;
    }

    function renderStatsTable(track, units) {
        const table = document.getElementById("stats-table");
        if (!table) return;
        table.innerHTML = `
            <div class="unit-toggle">
                <span>Units:</span>
                <button type="button" class="unit-btn" data-unit="metric">Metric</button>
                <button type="button" class="unit-btn" data-unit="imperial">Imperial</button>
                <button type="button" class="unit-btn" data-unit="raw">Raw</button>
            </div>
            <tr><th>Data</th><th>Value</th></tr>
            <tr><td>Filename</td><td>${track.filename}</td></tr>
            <tr><td>Filepath</td><td>${track.filepath}</td></tr>
            <tr><td>Description</td><td>${formatValue(track.description, "misc", units)}</td></tr>
            <tr><td>Average Moving Speed</td><td>${formatValue(track.avg_speed, "speed", units)}</td></tr>
            <tr><td>Total Distance 2D</td><td>${formatValue(track.length_2d, "distance", units)}</td></tr>
            <tr><td>Moving Time</td><td>${formatValue(track.moving_time, "time", units)}</td></tr>
            <tr><td>Max Speed</td><td>${formatValue(track.max_speed, "speed", units)}</td></tr>`;
    }

    // 4. Map & Animation Logic (Original + Car)
    function initMap(track_points) {
        const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "&copy; OpenStreetMap contributors", maxNativeZoom: 19, maxZoom: 23 });
        const esriSat = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri", maxNativeZoom: 23, maxZoom: 25 });
        const dark = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { attribution: "&copy; OpenStreetMap &copy; Carto", maxNativeZoom: 19, maxZoom: 23 });

        map = L.map("map", { center: [track_points[0].lat, track_points[0].lon], zoom: 13, layers: [osm], fullscreenControl: true });

        const trackPointsLayer = L.layerGroup();
        const polyline = L.polyline(track_points.map(p => [p.lat, p.lon]), { color: "#008e00", weight: 7 }).addTo(map);

        // --- ADDED START & END WAYPOINTS BACK ---
        if (track_points.length > 0) {
            L.marker([track_points[0].lat, track_points[0].lon])
                .addTo(map)
                .bindPopup("Start");

            L.marker([track_points[track_points.length - 1].lat, track_points[track_points.length - 1].lon])
                .addTo(map)
                .bindPopup("End");
        }
        // ----------------------------------------

        function renderTrackPoints() {
            trackPointsLayer.clearLayers();
            if (map.getZoom() < 14) return;
            track_points.forEach((point) => {
                const marker = L.circleMarker([point.lat, point.lon], { radius: 4, color: "#1f3145", weight: 1, fillOpacity: 0.7 });
                marker.on("mouseover", () => marker.setStyle({ radius: 14, color: "yellow" }));
                marker.on("mouseout", () => marker.setStyle({ radius: 4, color: "#1f3145" }));
                marker.on("click", () => { lastClickedPoint = point; renderTrackPanel(point); });
                trackPointsLayer.addLayer(marker);
            });
            if (!map.hasLayer(trackPointsLayer)) trackPointsLayer.addTo(map);
        }

        map.on("zoomend", renderTrackPoints);
        renderTrackPoints();
        L.control.layers({ "OSM": osm, "Satellite": esriSat, "Dark": dark }, { "Track Points": trackPointsLayer }).addTo(map);
        map.fitBounds(polyline.getBounds());

        // --- CAR ANIMATION ---
        const carIcon = L.icon({
            iconUrl: "/static/car.png",
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        carMarker = L.marker([track_points[0].lat, track_points[0].lon], { icon: carIcon }).addTo(map);
        
        const playBtn = document.getElementById("play-btn");
        if (playBtn) {
            playBtn.addEventListener("click", () => {
                isPlaying = !isPlaying;
                playBtn.innerHTML = isPlaying ? "⏸ Pause" : "▶ Play Timelapse";
                if (isPlaying) animateCar();
            });
        }

        function animateCar() {
            if (!isPlaying || animationIndex >= track_points.length) return;
            const p = track_points[animationIndex];
    
            // 1. Move the car marker to the new coordinates
            carMarker.setLatLng([p.lat, p.lon]);

            // 2. Rotate the car based on heading
            if (p.course) {
                 const el = carMarker.getElement();
            if (el) {
                el.style.transform = `translate3d(${el._leaflet_pos.x}px, ${el._leaflet_pos.y}px, 0px) rotate(${p.course}deg)`;
             }
         }

    // 3. CHECKBOX LOGIC: Only move the camera if the user wants it to follow
    const followCarToggle = document.getElementById("follow-car-toggle");
    if (followCarToggle && followCarToggle.checked) {
        map.panTo([p.lat, p.lon]);
    }

    // 4. Step forward and loop
    animationIndex++;
    setTimeout(animateCar, 50);
}
    }

    // 5. Initialize
    document.addEventListener("DOMContentLoaded", () => {
        initMap(track_points);
        renderStatsTable(track, getUnits());

        document.addEventListener("click", (e) => {
            if (e.target.classList.contains("unit-btn")) {
                setUnits(e.target.dataset.unit);
                renderStatsTable(track, getUnits());
                if (lastClickedPoint) renderTrackPanel(lastClickedPoint);
            }
        });
    });