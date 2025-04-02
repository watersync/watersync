// Initialize a map specifically for a modal
function initializeModalMap(mapContainer) {
    if (!mapContainer) return;

    if (window.modalMap) {
        // Cleanup existing modal map
        cleanupModalMap();
    }
    
    const initialLat = parseFloat(mapContainer.dataset.lat) || 51.505;
    const initialLng = parseFloat(mapContainer.dataset.lng) || -0.09;
    
    window.modalMap = customLeafletWidget(
        initialLat, 
        initialLng, 
        mapContainer.dataset.latFieldId, 
        mapContainer.dataset.lngFieldId
    );
    
    // Ensure the map is correctly sized
    setTimeout(() => {
        if (window.modalMap) {
            window.modalMap.invalidateSize();
        }
    }, 200);
}

// Clean up modal map resources
function cleanupModalMap() {
    if (window.modalMap) {
        try {
            // Remove all layers first
            window.modalMap.eachLayer(layer => window.modalMap.removeLayer(layer));
            // Remove all event listeners
            window.modalMap.off();
            // Remove the map
            window.modalMap.remove();
            window.modalMap = null;
        } catch (e) {
            console.error("Error cleaning up modal map:", e);
        }
    }

    // Clean up any leaflet IDs from the map container
    const mapContainer = document.querySelector("#map");
    if (mapContainer && mapContainer._leaflet_id) {
        mapContainer._leaflet_id = null;
    }
}

// Create a Leaflet map with a draggable marker for form input
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
