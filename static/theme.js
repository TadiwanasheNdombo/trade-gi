/**
 * Applies the saved theme and color from localStorage.
 * This function is defined in the global scope and executed immediately
 * to prevent a Flash of Unstyled Content (FOUC).
 */
const applyActiveTheme = () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedColor = localStorage.getItem('themeColor') || '#006B3F'; // Default to Ecobank green

    // Apply 'dark-theme' class to the <html> element if the saved theme is 'dark'
    document.documentElement.classList.toggle('dark-theme', savedTheme === 'dark');

    // Set the primary color variables for the entire application
    document.documentElement.style.setProperty('--ecobank-green', savedColor);
    document.documentElement.style.setProperty('--primary-color', savedColor);

    // The state of the settings controls will be set within DOMContentLoaded
    // to ensure the elements are available before we try to modify them.
};

// Run the function to apply the theme as soon as the script is parsed
applyActiveTheme();

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('#theme-toggle');
    const colorSchemeInput = document.querySelector('#color-scheme');

    if (themeToggle) {
        // Set the initial state of the toggle switch
        themeToggle.checked = (localStorage.getItem('theme') === 'dark');

        // Add the event listener for changes
        themeToggle.addEventListener('change', (e) => {
            const isDarkMode = e.target.checked;
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');

            document.documentElement.classList.toggle('dark-theme', isDarkMode);
        });
    }

    if (colorSchemeInput) {
        // Set the initial value of the color picker
        colorSchemeInput.value = localStorage.getItem('themeColor') || '#006B3F';

        colorSchemeInput.addEventListener('input', (e) => {
            const newColor = e.target.value;
            localStorage.setItem('themeColor', newColor);
            document.documentElement.style.setProperty('--ecobank-green', newColor); // Set the main variable
            document.documentElement.style.setProperty('--primary-color', newColor); // Also set the settings page variable
        });
    }
});