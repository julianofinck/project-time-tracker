/* This file is running before the whole html loads */
window.onload = function () {
   
    /* Get update button */
    var updateButton = document.getElementById("update-button");
    var updateArea = document.getElementById('update-area');
    window.alert(updateArea)
}



document.addEventListener('DOMContentLoaded', () => {
    /* Get update button */
    var updateButton = document.getElementById("update-button");
    var updateArea = document.getElementById('update-area');
    window.alert(updateArea)
    /* Get computed style */
    var computedStyle = window.getComputedStyle(updateButton);
});



// Get border and padding width
var borderWidth = parseFloat(computedStyle.borderLeftWidth) + parseFloat(computedStyle.borderRightWidth);
var paddingWidth = parseFloat(computedStyle.paddingLeft) + parseFloat(computedStyle.paddingRight);

// Calculate total width
var totalWidth = parseFloat(computedStyle.width) + borderWidth + paddingWidth;

// Set width of update area
updateArea.style.width = totalWidth + "px";

