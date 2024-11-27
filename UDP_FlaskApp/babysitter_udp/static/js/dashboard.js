
const muteToggle = document.getElementById('muteToggle');
const unmuteIcon = document.getElementById('unmuteIcon');

muteToggle.addEventListener('click', function() {
    muteToggle.style.display = 'none';
    unmuteIcon.style.display = 'block';
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

// for hiding status elements when not active:

document.addEventListener('DOMContentLoaded', function () {
    const currentStatus = "Active";
    const statusText = document.getElementById('statusText');
    const statusIcons = document.querySelectorAll('.statusIcon');

    
    
    statusText.textContent = currentStatus;

    statusIcons.forEach(icon => {
        if (icon.getAttribute('data-status') === currentStatus) {
            icon.style.display = 'block'; 
        } else {
            icon.style.display = 'none'; 
        }
    });
});



function toggleMenu() {
    const menu = document.getElementById("dropdown-menu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}
