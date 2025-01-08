function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    setCookie('dark_mode', isDarkMode, 365); 


}

// Cookie functions
function setCookie(name, value, minutes) {
    const d = new Date();
    d.setTime(d.getTime() + minutes * 60 * 1000);  
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}


function getCookie(name) {
    const nameEQ = name + "=";
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim();
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function deleteCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}


 
window.onload = function () {
    const isDarkMode = getCookie('dark_mode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }

    const savedName = getCookie('child_name');
    const savedAge = getCookie('child_age');

    if (savedName) {
        document.querySelector('.profile-info h2').textContent = savedName;
        document.getElementById('childNameInput').value = savedName;
    }

    if (savedAge) {
        document.querySelector('.profile-info .age').textContent = `Age: ${savedAge}`;
        document.getElementById('child_age').value = savedAge;
    }
};
 
 saveProfileBtn = document.getElementById('saveProfileBtn');
if (saveProfileBtn) {
    saveProfileBtn.addEventListener('click', () => {
        const childName = document.getElementById('childNameInput').value;
        const childAge = document.getElementById('child_age').value;

        setCookie('child_name', childName, 7);  
        setCookie('child_age', childAge, 7);

        document.querySelector('.profile-info h2').textContent = childName;
        document.querySelector('.profile-info .age').textContent = `Age: ${childAge}`;
        if (typeof editProfileModal !== 'undefined') {
            editProfileModal.style.display = 'none';
        }
    });
}
 
 resetBtn = document.getElementById('resetProfileBtn');
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        deleteCookie('child_name');
        deleteCookie('child_age');

        document.querySelector('.profile-info h2').textContent = "Child's Name";
        document.querySelector('.profile-info .age').textContent = "Age: N/A";

        document.getElementById('childNameInput').value = '';
        document.getElementById('child_age').value = '';
    });
}
