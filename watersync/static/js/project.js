/* Project specific Javascript goes here. */
function initializeJSONEditor(elementId, schemaUrl, hiddenFieldId) {
    // Fetch the JSON schema from the specified URL
    $.getJSON(schemaUrl, function(schema) {
        var options = {
            "theme": "bootstrap5",
            "template": "handlebars",
            "iconlib": "fontawesome5",
            "schema": schema,
            "disable_collapse": false,
            "disable_edit_json": true,
            "disable_properties": true,
            "array_controls_top": true
        };

        var element = document.getElementById(elementId);
        var editor = new JSONEditor(element, options);

        // On form submission, update the hidden textarea with the JSON string
        document.querySelector('form').addEventListener('submit', function() {
            document.getElementById(hiddenFieldId).value = JSON.stringify(editor.getValue());
        });
    });
}