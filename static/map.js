function initMap(pathData, trackInfo) {
    // --- 1. Define map tile layers ---
    var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    });
    var esriSat = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
        { attribution: 'Tiles &copy; Esri &mdash; Source: Esri' }
    );
    var dark = L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { attribution: '&copy; OpenStreetMap &copy; Carto' }
    );

    // --- 2. Initialize map ---
    var map = L.map('map', {
        center: [0, 0],
        zoom: 2,
        layers: [osm]
    });

    // --- 3. Car icon ---
    var carIcon = L.icon({
        iconUrl: "/static/car.png",
        iconSize: [40, 40],
        iconAnchor: [20, 20]
    });

    // --- 4. Track polyline and markers ---
    var trackLayer = L.layerGroup();
    if (pathData.length > 0) {
        var latlngs = pathData.map(p => [p.lat, p.lon]);
        var polyline = L.polyline(latlngs, {
            color: '#3388ff',
            weight: 3,
            opacity: 0.5,
            interactive: false
        }).addTo(trackLayer);

        pathData.forEach((p, index) => {
            if (index % 50 === 0) {
                var marker = L.circleMarker([p.lat, p.lon], {
                    radius: 5,
                    color: '#ffffff',
                    weight: 1,
                    fillColor: '#007bff',
                    fillOpacity: 1,
                    interactive: true
                });
                marker.bindTooltip(`
                    <b>Speed:</b> ${p.speed ? p.speed.toFixed(1) : '0'} mph<br>
                    <b>Lat:</b> ${p.lat.toFixed(0)}
                `, { sticky: true });
                marker.addTo(trackLayer);
            }
        });

        trackLayer.addTo(map);
        map.fitBounds(polyline.getBounds());
    }

    // --- 5. Layer control ---
    var baseLayers = { "OSM": osm, "Satellite": esriSat, "Dark": dark };
    var overlays = { "Track & Points": trackLayer };
    L.control.layers(baseLayers, overlays).addTo(map);

    // --- 6. Animate car ---
    let currentStep = 0;
    let carMarker;
    function animateCar() {
        if (pathData.length > 0 && currentStep < pathData.length) {
            let p = pathData[currentStep];
            if (!carMarker) carMarker = L.marker([p.lat, p.lon], {icon: carIcon}).addTo(map);
            else carMarker.setLatLng([p.lat, p.lon]);
            currentStep++;
            setTimeout(animateCar, 100);
        }
    }
    animateCar();
}

// Initialize the map once JSON data is available
initMap(pathData, trackInfo);