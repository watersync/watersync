document.addEventListener('htmx:afterSwap', function (e) {

    if (e.detail.target.id === "dialog") {

        var modalElement = document.getElementById('modal');
        var modal = new bootstrap.Modal(modalElement);

        modal.show();
    }
});

document.addEventListener('htmx:beforeSwap', function (e) {
    if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
        var modalElement = document.getElementById('modal');
        var modal = bootstrap.Modal.getInstance(modalElement);

        if (modal) {
            modal.hide();
        }
    }
});