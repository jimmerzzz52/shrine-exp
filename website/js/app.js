// Remove import 'dotenv/config'
// Instead, you can access environment variables via process.env if needed

// Example usage (not directly in app.js):
// console.log(process.env.MY_ENV_VARIABLE); // Assuming this variable is passed during the build

// add classes for mobile navigation toggling
var CSbody = document.querySelector('body');
const CSnavbarMenu = document.querySelector('#cs-navigation');
const CShamburgerMenu = document.querySelector('#cs-navigation .cs-toggle');

CShamburgerMenu.addEventListener('click', function () {
    CShamburgerMenu.classList.toggle('cs-active');
    CSnavbarMenu.classList.toggle('cs-active');
    CSbody.classList.toggle('cs-open');
    // run the function to check the aria-expanded value
    ariaExpanded();
});

// checks the value of aria expanded on the cs-ul and changes it accordingly whether it is expanded or not
function ariaExpanded() {
    const csUL = document.querySelector('#cs-expanded');
    const csExpanded = csUL.getAttribute('aria-expanded');

    if (csExpanded === 'false') {
        csUL.setAttribute('aria-expanded', 'true');
    } else {
        csUL.setAttribute('aria-expanded', 'false');
    }
}

// mobile nav toggle code
const dropDowns = Array.from(document.querySelectorAll('#cs-navigation .cs-dropdown'));
for (const item of dropDowns) {
    const onClick = () => {
        item.classList.toggle('cs-active');
    };
    item.addEventListener('click', onClick);
}

const faqItems = Array.from(document.querySelectorAll('.cs-faq-item'));
for (const item of faqItems) {
    const onClick = () => {
        item.classList.toggle('active');
    };
    item.addEventListener('click', onClick);
}

// Copyright Current Year
// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Get the current year
    var currentYear = new Date().getFullYear();
    
    // Find the element with the id "cs-copyright-year"
    var copyrightYearElement = document.getElementById("cs-copyright-year");
    
    // Check if the element exists
    if (copyrightYearElement) {
        // Set the text content to the current year
        copyrightYearElement.textContent = currentYear;
    }
});

// Toggle Gesture Recognition Apps
document.getElementById("toggle-app-button").addEventListener("click", function() {
    var x = document.getElementById("choose-an-app");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
});
