// Toggle mobile navigation menu
document.addEventListener("DOMContentLoaded", function() {
    const hamburgerMenu = document.querySelector(".hamburger-menu");
    const mobileNav = document.querySelector(".mobile-nav");
    const header = document.querySelector(".header");
    const landingSection = document.querySelector("#landing");

    hamburgerMenu.addEventListener("click", function() {
        mobileNav.classList.toggle("active");
    });

    // Function to adjust navbar background based on scroll position and section
    function adjustNavbarBackground() {
        if (window.scrollY > landingSection.offsetHeight) {
            header.style.backgroundColor = "rgba(34, 34, 34, 0.8)"; // Darker background for other sections
            header.style.backdropFilter = "none"; // Remove blur effect
        } else {
            header.style.backgroundColor = "rgba(34, 34, 34, 0.5)"; // Semi-transparent for landing page
            header.style.backdropFilter = "blur(10px)"; // Add blur effect for landing page
        }
    }

    // Call the function on scroll to dynamically update background
    window.addEventListener("scroll", adjustNavbarBackground);

    // Call the function once on load to set initial background based on position
    adjustNavbarBackground();
});
