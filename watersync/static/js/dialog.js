document.addEventListener('htmx:afterSwap', function (e) {

    if (e.detail.target.id === "dialog") {
        const modalElement = document.getElementById('modal');
        const mapContainer = modalElement.querySelector("#map");

        if (mapContainer) {

            const initialLat = parseFloat(mapContainer.dataset.lat) || 51.505;
            const initialLng = parseFloat(mapContainer.dataset.lng) || -0.09;
            const latFieldId = mapContainer.dataset.latFieldId;
            const lngFieldId = mapContainer.dataset.lngFieldId;

            // Always reinitialize the map instance and invalidate size
            const map = customLeafletWidget(initialLat, initialLng, latFieldId, lngFieldId);
            window.modalMap = map;

        }
        // Show the modal after ensuring the map is ready
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
});

function cleanupModalAndMap() {
    const modalElement = document.getElementById('modal');
    const modal = bootstrap.Modal.getInstance(modalElement);

    if (modal) {
        modal.hide();
    }

    const mapContainer = modalElement.querySelector("#map");

    if (mapContainer && window.modalMap) {

        window.modalMap.off(); // Remove all event listeners
        window.modalMap.remove(); // Destroy the map instance
        window.modalMap = null; // Clear the reference
    }
}

document.addEventListener('htmx:beforeSwap', function (e) {

    if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
        cleanupModalAndMap();
    }
});

$(document).on('hidden.bs.modal', '#modal', function () {
    cleanupModalAndMap();
});

document.addEventListener('htmx:responseError', function (e) {
    console.error("HTMX request failed with response:", e.detail);
    alert("An error occurred while processing your request. Please try again.");
});