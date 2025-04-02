// General map initialization for any leaflet map
function initializeMap(mapId, lat = 0, lng = 0, zoom = 2) {
    // Check if container exists
    const container = document.getElementById(mapId);
    if (!container) return null;
    
    // Clean up any existing map instance on this container
    if (container._leaflet_id) {
        container._leaflet_id = null;
    }

    // Define the bounds you want to restrict the map to
    const maxBounds = L.latLngBounds(
        L.latLng(-85, -180),  // Southwest corner
        L.latLng(85, 180)     // Northeast corner
    );

    const map = L.map(mapId, {
        maxBounds: maxBounds,
        maxBoundsViscosity: 1.0,  // How "sticky" the bounds are (1.0 = cannot go outside)
        noWrap: true,
        bounceAtZoomLimits: true
    }).setView([lat, lng], zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
    
    // Store reference to main page map
    if (mapId !== 'map') {
        window.mainPageMap = map;
    }
    
    return map;
}

// Plot locations on the map
function plotLocations(map, locations) {
    var bounds = L.latLngBounds();

    locations.forEach(function (location) {
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
