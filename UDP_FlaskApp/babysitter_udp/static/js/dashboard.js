// Define the toggleMenu function globally
function toggleMenu() {
    const menu = document.getElementById("dropdown-menu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

if (window.location.pathname === '/dashboard') {
    document.addEventListener('DOMContentLoaded', function () {
        const muteToggle = document.getElementById('muteToggle');
        const unmuteIcon = document.getElementById('unmuteIcon');
        const video = document.getElementById('myVideo');

        muteToggle.style.display = 'block';
        unmuteIcon.style.display = 'none';

        muteToggle.addEventListener('click', function () {
            if (video) {
                video.muted = true;
                muteToggle.style.display = 'none'; 
                unmuteIcon.style.display = 'block';
            } else {
                console.error("Video element not found");
            }
        });

        unmuteIcon.addEventListener('click', function () {
            if (video) {
                video.muted = false;
                unmuteIcon.style.display = 'none'; 
                muteToggle.style.display = 'block';
            } else {
                console.error("Video element not found");
            }
        });

        const statuses = ["Active", "Sleeping", "Crying"];
        let currentIndex = 0;

        const statusText = document.getElementById('statusText');
        const statusIcons = document.querySelectorAll('.statusIcon');

        // Function to update the displayed status and icons
        function updateStatus() {
            const currentStatus = statuses[currentIndex];
            statusText.textContent = currentStatus;

            statusIcons.forEach(icon => {
                if (icon.getAttribute('data-status') === currentStatus) {
                    icon.style.display = 'block'; 
                } else {
                    icon.style.display = 'none'; 
                }
            });
        }

        // Initial status display
        updateStatus();

        // Event listener for clicking on the status icon
        statusIcons.forEach(icon => {
            icon.addEventListener('click', function () {
                currentIndex = (currentIndex + 1) % statuses.length; // Loop through statuses
                updateStatus();
            });
        });
    });
}



// //     /* dashboard.js */

