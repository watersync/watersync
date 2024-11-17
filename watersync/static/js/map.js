// Initialize the leaflet map
function initializeMap(mapId, lat = 0, lng = 0, zoom = 2) {

    const map = L.map(mapId).setView([lat, lng], zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        noWrap: true,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
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

function customizeLeafletDjangoWidget(map) {
    // Access the Leaflet map instance created by LeafletWidget
    const leafletMap = window.map_init_basic;

    if (leafletMap) {
        leafletMap.setMaxBounds([[85, -180], [-85, 180]]);
        leafletMap.options.noWrap = true;
    }
}

function customLeafletWidget(initialLat, initialLng, latFieldId, lngFieldId) {
    const map = initializeMap('map', initialLat, initialLng, 13);

    const marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);

    marker.on('dragend', function () {
        const latLng = marker.getLatLng();
        const latInput = document.getElementById(latFieldId);
        const lngInput = document.getElementById(lngFieldId);

        if (latInput && lngInput) {
            latInput.value = latLng.lat.toFixed(6);
            lngInput.value = latLng.lng.toFixed(6);
        }
    });

    const latInput = document.getElementById(latFieldId);
    const lngInput = document.getElementById(lngFieldId);

    if (latInput && lngInput) {
        latInput.value = initialLat.toFixed(6);
        lngInput.value = initialLng.toFixed(6);

        function updateMarker() {
            const lat = parseFloat(latInput.value);
            const lng = parseFloat(lngInput.value);

            if (!isNaN(lat) && !isNaN(lng)) {
                const newLatLng = L.latLng(lat, lng);
                marker.setLatLng(newLatLng);
                map.setView(newLatLng);
            }
        }

        latInput.addEventListener('input', updateMarker);
        lngInput.addEventListener('input', updateMarker);
    }

    // Invalidate size after a short delay to ensure correct rendering
    setTimeout(() => {
        map.invalidateSize();
    }, 300);

    return map;
}