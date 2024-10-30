document.addEventListener("DOMContentLoaded", function() {
    const options = document.querySelectorAll(".option");
    const selectedOptionInput = document.getElementById("selected-role");

    options.forEach(option => {
        option.addEventListener("click", () => {
            // Remove selected class from all options
            options.forEach(opt => opt.classList.remove("selected"));

            // Add selected class to the clicked option
            option.classList.add("selected");

            // Set the hidden input value
            selectedOptionInput.value = option.getAttribute("data-value");
        });
    });
});