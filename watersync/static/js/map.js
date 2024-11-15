// Initialize the leaflet map
function initializeMap(mapId, lat = 0, lng = 0, zoom = 2) {
    var map = L.map(mapId).setView([lat, lng], zoom);

    // Add tile layers
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        noWrap: true,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
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

// function customLeafletWidget(initialLat, initialLng, latFieldId, lngFieldId) {
//     // Initialize the map
//     var map = L.map('map').setView([initialLat, initialLng], 13);

//     // Add a tile layer to the map (e.g., OpenStreetMap)
//     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         maxZoom: 19,
//         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//     }).addTo(map);

//     // Add a marker at the initial location or at the map center
//     var marker = L.marker([initialLat, initialLng], {
//         draggable: true
//     }).addTo(map);

//     // Update the hidden latitude and longitude fields on drag end
//     marker.on('dragend', function (e) {
//         var latLng = marker.getLatLng();
//         document.getElementById(latFieldId).value = latLng.lat.toFixed(6);
//         document.getElementById(lngFieldId).value = latLng.lng.toFixed(6);
//     });

//     // Initialize the hidden fields with the marker's initial position
//     document.getElementById(latFieldId).value = marker.getLatLng().lat.toFixed(6);
//     document.getElementById(lngFieldId).value = marker.getLatLng().lng.toFixed(6);

//     // Function to update marker position based on lat/lng inputs
//     function updateMarkerPosition() {
//         var lat = parseFloat(document.getElementById(latFieldId).value);
//         var lng = parseFloat(document.getElementById(lngFieldId).value);

//         if (!isNaN(lat) && !isNaN(lng)) {
//             var newLatLng = new L.LatLng(lat, lng);
//             marker.setLatLng(newLatLng);
//             map.setView(newLatLng);
//         }
//     }

//     // Add event listeners to update marker position when lat/lng inputs change
//     document.getElementById(latFieldId).addEventListener('input', updateMarkerPosition);
//     document.getElementById(lngFieldId).addEventListener('input', updateMarkerPosition);

//     // Add drawing controls to the map
//     var drawControl = new L.Control.Draw({
//         draw: {
//             polygon: false,
//             polyline: false,
//             rectangle: false,
//             circle: false,
//             circlemarker: false,
//             marker: true
//         },
//         edit: {
//             featureGroup: marker ? L.featureGroup([marker]).addTo(map) : L.featureGroup().addTo(map),
//             remove: false
//         }
//     }).addTo(map);

//     // Handle the creation of new markers
//     map.on(L.Draw.Event.CREATED, function (event) {
//         var layer = event.layer;

//         // If there's already a marker, remove it
//         if (marker) {
//             map.removeLayer(marker);
//         }

//         marker = layer;
//         marker.addTo(map);

//         // Update the hidden latitude and longitude fields
//         var latLng = marker.getLatLng();
//         document.getElementById(latFieldId).value = latLng.lat.toFixed(6);
//         document.getElementById(lngFieldId).value = latLng.lng.toFixed(6);
//     });
// }

function customLeafletWidget(initialLat, initialLng, latFieldId, lngFieldId) {
    var map = L.map('map').setView([initialLat, initialLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    var marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);

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

    return map;
}