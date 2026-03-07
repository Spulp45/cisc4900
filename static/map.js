var map = L.map('map').setView([40.7128, -74.0060], 10);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// NEW: Plotting the line
if (typeof pathData !== 'undefined' && pathData.length > 0) {
    var polyline = L.polyline(pathData, {
        color: 'aqua',
        weight: 4,
        opacity: 0.7
    }).addTo(map);

    // Zoom the map to fit the path
    map.fitBounds(polyline.getBounds());
}

