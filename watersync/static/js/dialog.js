// Modal initialization and management
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
        modalElement.addEventListener('shown.bs.modal', function () {
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

function cleanupModalMap() {
    // Only target the modal map instance
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

    // Only clean up the modal map container, not all map containers
    const modalMapContainer = document.querySelector("#modal #map");
    if (modalMapContainer && modalMapContainer._leaflet_id) {
        modalMapContainer._leaflet_id = null;
    }
}

function cleanupModalAndMap() {
    // First clean up just the modal map (not all maps)
    cleanupModalMap();

    // Then handle the modal itself
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

                    // Refresh only the main page map
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

// Offcanvas for details of some objects
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
