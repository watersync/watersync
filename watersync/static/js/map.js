// Function to initialize the map
function initializeMap(mapId, lat = 0, lng = 0, zoom = 2) {
    var map = L.map(mapId).setView([lat, lng], zoom);

    // Add the OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    return map;
}

// Function to plot locations on the map
function plotLocations(map, locations) {
    var bounds = L.latLngBounds();

    locations.forEach(function(location) {
        var marker = L.marker([location.lat, location.lng]).addTo(map)
            .bindPopup('<b>' + location.name)
            .openPopup();
        bounds.extend(marker.getLatLng());
    });

    // Fit the map to the bounds of the markers if bounds are valid
    if (bounds.isValid()) {
        map.fitBounds(bounds);
    }
}