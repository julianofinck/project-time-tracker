console.log("it ran")
window.alert("it worked2")
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


document.addEventListener('DOMContentLoaded', () => {
    const height = window.innerHeight;
    const element = document.getElementById('histogram');
    element.style.height = (height * 0.3) + 'px';
    window.alert("it worked")
});

window.alert("it worked2")