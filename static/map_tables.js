
    // 1. Global Variables
    let map; 
    let lastClickedPoint = null;
    let isPlaying = false;
    let animationIndex = 0;
    let animationDirection = 1 // 1 = forward, -1 = backward
    let carMarker = null;
    let animationTimer = null;
    let playbackSpeed = 1;
    let currentAngle = 0;
    

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

    function field(label, value, formatter, type) {
    let displayValue = value;

    if (value == null || value === "") {
        displayValue = "—";
    } else if (formatter) {
        displayValue = formatter(value, type);
    }

    return `<p><b>${label}:</b> ${displayValue}</p>`;
}

    // 3. UI Rendering (Original)
    function renderTrackPanel(point) {
        if (!point) return;
        const panel = document.getElementById("point-readout");
        const userUnits = getUnits();
        panel.innerHTML = `
            <h3>Track Point</h3>

            ${field("Latitude", point.lat)}
            ${field("Longitude", point.lon)}
            ${field("Speed", point.speed, formatValue, "speed")}
            ${field("Elevation", point.ele, formatValue, "elevation")}
            ${field("Time", point.timestamp, formatValue, "timestamp")}
            ${field("Course", point.course)}
            ${field("Geoid Height", point.geoidheight)}
            ${field("Source", point.src)}
            ${field("Satellites", point.sat)}
            ${field("HDOP", point.hdop)}
            ${field("VDOP", point.vdop)}
            ${field("PDOP", point.pdop)}
            `;
    }

    function renderStatsTable(track, units) {
        const table = document.getElementById("stats-table");
        if (!table) return;
        table.innerHTML = `
            <tr><th>Data</th><th>Value</th></tr>
            <tr><td>Filename</td><td>${track.filename}</td></tr>
            <tr><td>Filepath</td><td>${track.filepath}</td></tr>
            <tr><td>Description</td><td>${formatValue(track.description, "misc", units)}</td></tr>
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
            <tr><td>Start Time</td><td>${formatValue(track.start_time, "timestamp", units)}</td></tr>
            <tr><td>End Time</td><td>${formatValue(track.end_time, "timestamp", units)}</td></tr>
            <tr><td>Points</td><td>${track.points}</td></tr>
            <tr><td>GPX Version</td><td>${track.gpx_version}</td></tr>
        `;
    }

    // 4. Map & Animation Logic (Original + Car)
    function initMap(track_points) {
        const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "&copy; OpenStreetMap contributors", maxNativeZoom: 19, maxZoom: 23 });
        const esriSat = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri", maxNativeZoom: 23, maxZoom: 25 });
        const dark = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { attribution: "&copy; OpenStreetMap &copy; Carto", maxNativeZoom: 19, maxZoom: 23 });

        map = L.map("map", { center: [track_points[0].lat, track_points[0].lon], zoom: 13, layers: [osm], fullscreenControl: true });

        const trackPointsLayer = L.layerGroup();
        const polyline = L.polyline(track_points.map(p => [p.lat, p.lon]), { color: "#607D8B", weight: 7 }).addTo(map);

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
            if (map.getZoom() < 12) return;
            track_points.forEach((point) => {
                 
                // if statement (check if point.speed >= track.max_speed)
                    // set it to red color (indicating >= max speed was reached here)

                if(point.speed >= track.max_speed)
                {   
                    const marker = L.circleMarker([point.lat, point.lon], { radius: 4, color: "#E53935", weight: 1, fillOpacity: 0.7 });
                    trackPointsLayer.addLayer(marker);
                    marker.on("mouseover", () => marker.setStyle({ radius: 14, color: "yellow" }));
                    marker.on("mouseout", () => marker.setStyle({ radius: 4, color: "#E53935" }));
                    marker.on("click", () => { lastClickedPoint = point; renderTrackPanel(point); });
                }
                else if(point.speed == 0.0)
                {   
                    const marker = L.circleMarker([point.lat, point.lon], { radius: 4, color: "#FB8C00", weight: 1, fillOpacity: 0.7 });
                    trackPointsLayer.addLayer(marker);
                    marker.on("mouseover", () => marker.setStyle({ radius: 14, color: "yellow" }));
                    marker.on("mouseout", () => marker.setStyle({ radius: 4, color: "#FB8C00" }));
                    marker.on("click", () => { lastClickedPoint = point; renderTrackPanel(point); });
                }
                else {
                    const marker = L.circleMarker([point.lat, point.lon], { radius: 4, color: "#145A32", weight: 1, fillOpacity: 0.7 });
                    trackPointsLayer.addLayer(marker);
                    marker.on("mouseover", () => marker.setStyle({ radius: 14, color: "yellow" }));
                    marker.on("mouseout", () => marker.setStyle({ radius: 4, color: "#145A32" }));
                    marker.on("click", () => { lastClickedPoint = point; renderTrackPanel(point); });
                }
                
               
            });
            if (!map.hasLayer(trackPointsLayer)) trackPointsLayer.addTo(map);
        }

        map.on("zoomend", renderTrackPoints);
        renderTrackPoints();
        L.control.layers({ "OSM": osm, "Satellite": esriSat, "Dark": dark }, { "Track Points": trackPointsLayer }).addTo(map);
        map.fitBounds(polyline.getBounds());

        // --- CAR ANIMATION ---
        const carIcon = L.icon({
        iconUrl: '/static/arrow.png',
        shadowUrl: '/static/car.png',

        iconSize:     [24, 24], // size of the icon
        shadowSize:   [32, 32], // size of the shadow
        iconAnchor:   [8, 8], // point of the icon which will correspond to marker's location
        shadowAnchor: [8, 8],  // the same for the shadow
    });

        carMarker = L.marker([track_points[0].lat, track_points[0].lon], {icon : carIcon }).addTo(map);
    const playBtn = document.getElementById("play-btn");
    const rewindBtn = document.getElementById("rewind-btn");
    const forwardBtn = document.getElementById("forward-btn");

    // --- CAR SHADOW CUSTOMIZATION ---
    const colorSelect = document.getElementById("car-color-select");

    if (colorSelect) {
        colorSelect.addEventListener("change", (e) => {
            
            const newShadowUrl = `/static/${e.target.value}`;
            
            const updatedIcon = L.icon({
                iconUrl: '/static/arrow.png',    // The arrow stays the same
                shadowUrl: newShadowUrl,        // The car (shadow) changes
                
                iconSize:     [24, 24],
                shadowSize:   [32, 32],
                iconAnchor:   [8, 8],
                shadowAnchor: [16, 16], 
            });

            // Apply the update
            carMarker.setIcon(updatedIcon);
            
            
            const el = carMarker.getElement();
            if (el) {
                const base = el.style.transform.replace(/rotate\(.*?\)/, "");
                el.style.transform = `${base} rotate(${currentAngle}deg)`;
            }
        });
    }

    if (playBtn) {
        playBtn.addEventListener("click", () => {
            clearTimeout(animationTimer); 
            isPlaying = !isPlaying;

            playBtn.innerHTML = isPlaying ? "⏸ Pause" : "▶ Play Timelapse";

            if (isPlaying) animateCar();
        });
    }

    if (rewindBtn) {
        rewindBtn.addEventListener("click", () => {
            clearTimeout(animationTimer);

            animationDirection = -1;
            isPlaying = true;

            animateCar();
        });
    }

const customSpeedInput = document.getElementById("custom-speed");
const customSpeedBtn = document.getElementById("custom-speed-btn");

if (customSpeedBtn && customSpeedInput) {

    customSpeedBtn.addEventListener("click", () => {
        const val = parseFloat(customSpeedInput.value);

        if (!isNaN(val) && val > 0) {
            playbackSpeed = val;
            console.log("Custom speed set to:", playbackSpeed);
        }
    });

    customSpeedInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            customSpeedBtn.click();
        }
    });


    customSpeedInput.addEventListener("input", () => {
        const val = parseFloat(customSpeedInput.value);

        if (!isNaN(val) && val > 0) {
            playbackSpeed = val;
            console.log("Custom speed set to:", playbackSpeed);
        }
    });

}

if (forwardBtn) {
    forwardBtn.addEventListener("click", () => {
        clearTimeout(animationTimer); // prevent stacking

        animationDirection = 1; 
        isPlaying = true;

        animateCar();
    });
}


const slider = document.getElementById("timeline-slider");
slider.max = track_points.length - 1;
slider.value = 0;


slider.addEventListener("input", () => {
    isPlaying = false;
    clearTimeout(animationTimer);

    animationIndex = parseInt(slider.value);

    const p = track_points[animationIndex];

    carMarker.setLatLng([p.lat, p.lon]);
    renderTrackPanel(p);

    updateSliderProgress(slider);
});

function updateSliderProgress(slider) {
    const percent = (slider.value / slider.max) * 100;
    slider.style.setProperty("--progress", `${percent}%`);
}


// Calculate Angle 
function calculateBearing(lat1, lon1, lat2, lon2) {
    const toRad = (deg) => deg * Math.PI / 180;
    const toDeg = (rad) => rad * 180 / Math.PI;

    const phi1 = toRad(lat1);
    const phi2 = toRad(lat2);
    const delta = toRad(lon2 - lon1);

    const y = Math.sin(delta) * Math.cos(phi2);
    const x =
        Math.cos(phi1) * Math.sin(phi2) -
        Math.sin(phi1) * Math.cos(phi2) * Math.cos(delta);

    let θ = Math.atan2(y, x);
    θ = toDeg(θ);

    return (θ + 360) % 360; // normalize 0–360
}

function lerpAngle(a, b, t) {
    const diff = ((b - a + 540) % 360) - 180; // shortest direction
    return (a + diff * t + 360) % 360;
}
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}


function animateCar() {
    if (!isPlaying) return;

    // Update the slider as we run the animation
    if (slider) {
        slider.value = animationIndex;
        updateSliderProgress(slider); 
    }

    // Stop at bounds
    if (animationIndex >= track_points.length) {
        animationIndex = track_points.length - 1;
        isPlaying = false;
        return;
    }

    if (animationIndex < 0) {
        animationIndex = 0;
        isPlaying = false;
        return;
    }

    const p = track_points[animationIndex];

    //console.log("Track point:", p); // optional debug

    // 1. Move car
    carMarker.setLatLng([p.lat, p.lon]);
    renderTrackPanel(p);

    // 2. Rotate arrow
    const p1 = track_points[animationIndex];
    const p2 = track_points[Math.min(animationIndex + 5, track_points.length - 5)];

    const baseHeading = calculateBearing(p1.lat, p1.lon, p2.lat, p2.lon);
    
    currentAngle = lerpAngle(currentAngle, baseHeading, 0.67);

    const el = carMarker.getElement(); 
    if (el) {
        const base = el.style.transform.replace(/rotate\(.*?\)/, "");
        el.style.transform = `${base} rotate(${currentAngle}deg)`;
    }

    // 3. Follow toggle
    const followCarToggle = document.getElementById("follow-car-toggle");
    if (followCarToggle && followCarToggle.checked) {
        map.panTo([p.lat, p.lon]);
    }

    // 4. Move forward/backward
    animationIndex += animationDirection;

    // 5. Loop safely
    animationTimer = setTimeout(animateCar, 300 / playbackSpeed);
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