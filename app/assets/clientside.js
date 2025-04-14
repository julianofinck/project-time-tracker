window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        reloadPage: function (data) {
            if (data && data.reload) {
                window.location.reload();
            }
            return window.location.pathname;
        }
    }
});


function matchSpacerHeight() {
    const spacer = document.getElementById("header-spacer");
    const selectors = document.getElementById("selectors-container");

    if (spacer && selectors) {
        spacer.style.height = selectors.offsetHeight + "px";
    }
}

// Wait until elements are available
function waitAndMatchHeight() {
    const selectors = document.getElementById("selectors-container");
    if (!selectors) {
        setTimeout(waitAndMatchHeight, 500);
        return;
    }
    matchSpacerHeight();
}

// Run after DOM is ready
window.addEventListener("load", waitAndMatchHeight);
window.addEventListener("resize", matchSpacerHeight);
