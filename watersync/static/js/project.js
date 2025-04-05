/* Project specific Javascript goes here. */
function initializeJSONEditor(elementId, schemaUrl,
    hiddenFieldId, initialData) {
    // Fetch the JSON schema from the specified URL
    $.getJSON(schemaUrl, function (schema) {
        var options = {
            "theme": "bootstrap5",
            "template": "handlebars",
            "iconlib": "fontawesome5",
            "schema": schema,
            "startval": initialData,
            "disable_collapse": false,
            "disable_edit_json": true,
            "disable_properties": true,
            "array_controls_top": true
        };

        var element = document.getElementById(elementId);
        var editor = new JSONEditor(element, options);

        // On form submission, update the hidden textarea with the JSON string
        document.getElementById(hiddenFieldId).closest('form').addEventListener('submit', function () {
            document.getElementById(hiddenFieldId).value = JSON.stringify(editor.getValue());
        });
    });
}

function reinitializeJSONEditor(elementId, schemaUrl, hiddenFieldId, newData) {
    // Clear the existing editor instance
    var element = document.getElementById(elementId);
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }

    // Reinitialize the editor with new data
    initializeJSONEditor(elementId, schemaUrl, hiddenFieldId, newData);
}

function downloadCSV(elementId, data, fileName) {
    // Get the button element by ID
    const button = document.getElementById(elementId);

    // Set up the click event listener
    button.addEventListener('click', function () {
        // Prepare CSV content
        let csvContent = "data:text/csv;charset=utf-8,";

        // Generate the CSV header
        const headers = ["timestamp", "value", "type", "unit"];
        csvContent += headers.join(",") + "\n";

        // Add data rows
        data.forEach(function (row) {
            let rowData = [
                row.timestamp,
                row.value,
                row.type,
                row.unit
            ];
            csvContent += rowData.join(",") + "\n";
        });

        // Encode the content and create a link element
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", fileName);
        document.body.appendChild(link); // Required for FF

        // Trigger the download
        link.click();

        // Clean up
        document.body.removeChild(link);
    });
}