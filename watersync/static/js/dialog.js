document.addEventListener('htmx:afterSwap', function (e) {
    if (e.detail.target.id === "dialog") {
        const modalElement = document.getElementById('modal');
        let modal = bootstrap.Modal.getInstance(modalElement);
        
        // Initialize or get existing modal
        if (!modal) {
            modal = new bootstrap.Modal(modalElement);
        }
        
        modal.show();
        
        // Wait for modal to be fully visible before initializing map
        modalElement.addEventListener('shown.bs.modal', function() {
            const mapContainer = modalElement.querySelector("#map");
            if (mapContainer) {
                // Initialize modal map
                initializeModalMap(mapContainer);

                window.modalMap.invalidateSize();

            }
        }, { once: true });
    }
});

// Unified cleanup function
function cleanupModalAndMap() {
    const modalElement = document.getElementById('modal');
    
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        
        if (modal) {
            try {
                // Use a safer approach to hiding the modal
                modal.hide();
                
                // Don't dispose immediately - let the hiding complete first
                modalElement.addEventListener('hidden.bs.modal', function onHidden() {
                    // Remove this listener to prevent memory leaks
                    modalElement.removeEventListener('hidden.bs.modal', onHidden);
                    
                    if (bootstrap.Modal.getInstance(modalElement)) {
                        modal.dispose();
                    }
                }, { once: true });
            } catch (e) {
                console.error("Error with modal:", e);
            }
        }
    }

    // Map cleanup code - this part seems fine
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