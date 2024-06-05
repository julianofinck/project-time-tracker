
function updateWindowSize() {
    // Get the innerWidth and innerHeight of the browser window
    var width = window.innerWidth;
    var height = window.innerHeight;

    // Update the HTML elements with the window size information
    document.getElementById('window-size-width').textContent = width;
    document.getElementById('window-size-height').textContent = height;
    
    return { "width": width, "height": height };
}

// Call the updateWindowSize function to display the initial window size
updateWindowSize();

