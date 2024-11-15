// document.addEventListener('htmx:afterSwap', function (e) {

//     if (e.detail.target.id === "dialog") {

//         var modalElement = document.getElementById('modal');
//         var modal = new bootstrap.Modal(modalElement);

//         modal.show();
//     }
// });


// document.addEventListener('htmx:beforeSwap', function (e) {
//     if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
//         var modalElement = document.getElementById('modal');
//         var modal = bootstrap.Modal.getInstance(modalElement);

//         if (modal) {
//             modal.hide();
//         }
//     }
// });


document.addEventListener('htmx:afterSwap', function (e) {
    if (e.detail.target.id === "dialog") {
        var modalElement = document.getElementById('modal');
        var modal = new bootstrap.Modal(modalElement);

        modal.show();

        // Check if the modal contains a map element
        const mapContainer = modalElement.querySelector("#map");
        if (mapContainer) {
            const initialLat = parseFloat(mapContainer.dataset.lat) || 51.505;
            const initialLng = parseFloat(mapContainer.dataset.lng) || -0.09;
            const latFieldId = mapContainer.dataset.latFieldId;
            const lngFieldId = mapContainer.dataset.lngFieldId;

            // Initialize or reinitialize the map
            if (!window.modalMap) {
                window.modalMap = customLeafletWidget(initialLat, initialLng, latFieldId, lngFieldId);
            }

            // Adjust map size after modal is fully rendered
            setTimeout(() => {
                if (window.modalMap) {
                    window.modalMap.invalidateSize();
                }
            }, 200);
        }
    }
});

document.addEventListener('htmx:beforeSwap', function (e) {
    if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
        var modalElement = document.getElementById('modal');
        var modal = bootstrap.Modal.getInstance(modalElement);

        if (modal) {
            modal.hide();

            // Clean up map instance when modal content is replaced
            const mapContainer = modalElement.querySelector("#map");
            if (mapContainer && window.modalMap) {
                window.modalMap.off(); // Remove all event listeners
                window.modalMap.remove(); // Destroy the map instance
                window.modalMap = null;
            }
        }
    }
});