setTimeout(() => {

    var visualizador_apontamentos = document.getElementById("main-analysis");

    visualizador_apontamentos.addEventListener('click', changeProductActivityCODEX);
    
    var projectDropdown = document.getElementById("project-selector");

    var selectArrowZone = document.getElementsByClassName("Select-arrow-zone");

    /*selectArrowZone.addEventListener('click', changeProductActivityCODEX)*/

}, 1000);


function changeProductActivityCODEX() {
    var dropdown = document.getElementById("project-selector");
    // Check if the element exists
    if (dropdown) {
        // Find the element that contains the value "CODEX"
        var valueElement = dropdown.querySelector(".Select-value-label");
        // Check if the value element exists
        if (valueElement) {
            // Get the text content of the value element
            var value = valueElement.textContent;
            var product_title = document.getElementById("product-selector-title");
            if (value === "CODEX") {
                product_title.innerText = "Atividade";
            } else {
                product_title.innerText = "Produto";
            }
            // Log or use the value as needed
            console.log(value); // Output: CODEX
        } else {
            console.log("Value element not found.");
        }
    } else {
        console.log("Dropdown element not found.");
    }
  }

// Function to get the current value from the dropdown
function getDropdownValue() {
    var dropdown = document.getElementById("project-selector");

    if (dropdown) {
        var valueElement = dropdown.querySelector(".Select-value-label");

        if (valueElement) {
            var value = valueElement.textContent;
            console.log(value); // Output the current value, e.g., "CODEX"
        } else {
            console.log("Value element not found.");
        }
    } else {
        console.log("Dropdown element not found.");
    }
}


