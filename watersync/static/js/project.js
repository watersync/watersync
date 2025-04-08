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