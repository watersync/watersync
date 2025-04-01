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
                // Initialize modal map after a short delay
                setTimeout(() => {
                    initializeModalMap(mapContainer);
                }, 100);
            }
        }, { once: true });
    }
});

// Improved cleanup function
function cleanupModalAndMap() {
    // First clean up the map
    if (window.modalMap) {
        try {
            window.modalMap.eachLayer(layer => window.modalMap.removeLayer(layer));
            window.modalMap.off();
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

    // Then handle the modal
    const modalElement = document.getElementById('modal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            try {
                modal.hide();
                
                modalElement.addEventListener('hidden.bs.modal', function onHidden() {
                    modalElement.removeEventListener('hidden.bs.modal', onHidden);
                    
                    if (bootstrap.Modal.getInstance(modalElement)) {
                        modal.dispose();
                    }
                    
                    // Refresh the main page map if it exists
                    if (window.mainPageMap) {
                        setTimeout(() => {
                            window.mainPageMap.invalidateSize();
                        }, 200);
                    }
                }, { once: true });
            } catch (e) {
                console.error("Error with modal:", e);
            }
        }
    }
}

document.addEventListener('htmx:beforeSwap', function (e) {
    if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
        cleanupModalAndMap();
    }
});

// Make sure we only have one event listener for modal hidden
$(document).off('hidden.bs.modal', '#modal').on('hidden.bs.modal', '#modal', function () {
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
    if (e.detail.target.id === "ofc-dialog" && !e.detail.xhr.response) {
        const offcanvasElement = document.getElementById('offcanvasRight');
        if (offcanvasElement) {
            const offcanvasRight = bootstrap.Offcanvas.getInstance(offcanvasElement);
            if (offcanvasRight) {
                offcanvasRight.hide();
            }
        }
    }
});
