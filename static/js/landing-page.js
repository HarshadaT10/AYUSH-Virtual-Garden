document.addEventListener("DOMContentLoaded", function() {
    const words = ["Searching", "Exploring", "Reading", "Discussing"]; // Words to be cycled through
    let currentWordIndex = 0; // Starting index for the words
    const dynamicWordElement = document.getElementById("dynamic-word"); // Target element for the changing words
    const dots = document.querySelectorAll(".dot"); // All dot elements

    // Function to change the word and highlight the correct dot
    function changeWord(index) {
        dynamicWordElement.textContent = words[index]; // Update the displayed word
        dots.forEach(dot => dot.classList.remove("active")); // Remove active class from all dots
        dots[index].classList.add("active"); // Add active class to the clicked dot
        currentWordIndex = index; // Update the current word index
    }

    // Automatically change the word every 4 seconds
    setInterval(function() {
        currentWordIndex = (currentWordIndex + 1) % words.length; // Loop through words
        changeWord(currentWordIndex);
    }, 4000);

    // Add click event listeners to the dots
    dots.forEach(dot => {
        dot.addEventListener("click", function() {
            const index = parseInt(dot.getAttribute("data-index")); // Get the index of the clicked dot
            changeWord(index); // Change the word based on the clicked dot
        });
    });

    // Initialize the first word and set the first dot as active
    changeWord(currentWordIndex);

});



