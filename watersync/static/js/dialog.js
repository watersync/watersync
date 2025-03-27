document.addEventListener('htmx:afterSwap', function (e) {
    if (e.detail.target.id === "dialog") {
        const modalElement = document.getElementById('modal');
        let modal = bootstrap.Modal.getInstance(modalElement);
        
        // Initialize or get existing modal
        if (!modal) {
            modal = new bootstrap.Modal(modalElement);
        }

        // Delay map initialization for DOM stability
        setTimeout(() => {
            const mapContainer = modalElement.querySelector("#map");
            if (mapContainer) {
                if (window.modalMap) {
                    // Cleanup existing map
                    window.modalMap.eachLayer(layer => window.modalMap.removeLayer(layer));
                    window.modalMap.off();
                    window.modalMap.remove();
                    mapContainer._leaflet_id = null;
                }
                
                const initialLat = parseFloat(mapContainer.dataset.lat) || 51.505;
                const initialLng = parseFloat(mapContainer.dataset.lng) || -0.09;
                window.modalMap = customLeafletWidget(initialLat, initialLng, 
                    mapContainer.dataset.latFieldId, 
                    mapContainer.dataset.lngFieldId
                );
            }
            modal.show();
        }, 50);
    }
});

// Unified cleanup function
function cleanupModalAndMap() {
    const modalElement = document.getElementById('modal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    
    if (modal) {
        modal.hide();
        modal.dispose(); // Properly dispose the modal instance
    }

    if (window.modalMap) {
        window.modalMap.eachLayer(layer => window.modalMap.removeLayer(layer));
        window.modalMap.off();
        window.modalMap.remove();
        const mapContainer = document.querySelector("#map");
        if (mapContainer) mapContainer._leaflet_id = null;
        window.modalMap = null;
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

// offcanvas for details of some objects
document.addEventListener('htmx:afterSwap', function (e) {
    if (e.detail.target.id === "ofc-dialog") {
        const offcanvasElement = document.getElementById('offcanvasRight');
        const offcanvasRight = new bootstrap.Offcanvas(offcanvasElement);
        offcanvasRight.show();
    }
});

document.addEventListener('htmx:beforeSwap', function (e) {
    const offcanvasElement = document.getElementById('offcanvasRight');
    const offcanvasRight = bootstrap.Offcanvas.getInstance(offcanvasElement);

    if (e.detail.target.id === "ofc-dialog" && !e.detail.xhr.response) {
        if (offcanvasRight) {
            offcanvasRight.hide();
        }
    }
});