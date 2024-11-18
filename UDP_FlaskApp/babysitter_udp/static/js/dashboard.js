
const muteToggle = document.getElementById('muteToggle');
const unmuteIcon = document.getElementById('unmuteIcon');

muteToggle.addEventListener('click', function() {
    muteToggle.style.display = 'none';
    unmuteIcon.style.display = 'block';
});

unmuteIcon.addEventListener('click', function() {
    unmuteIcon.style.display = 'none';
    muteToggle.style.display = 'block';
});


//testing


