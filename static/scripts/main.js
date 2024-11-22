document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript loaded.'); // Logs when the DOM is ready

    // This defines the confirmDischarge function and attaches it to the global window object
    window.confirmDischarge = function (url) {
        console.log('confirmDischarge function called with URL:', url);
        
        if (confirm('Are you sure you want to discharge this patient?')) {
            // Make a POST request to the provided URL to discharge the patient
            fetch(url, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();  // Refresh the page if successful
                    } else {
                        alert('Failed to discharge patient.');
                    }
                })
                .catch(error => console.error('Error discharging patient:', error));
        }
    };
});

document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        const username = document.getElementById('form2Example17').value;
        const password = document.getElementById('form2Example27').value;
        const usernameRegex = /^[A-Za-z0-9]{6,}$/; // At least 6 characters
        const passwordRegex = /^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$/; // At least 8 characters with letters, numbers, and one special character
        
        if (!usernameRegex.test(username)) {
            alert('Username must be at least 6 characters long and can contain letters and numbers only.');
            event.preventDefault();
            return;
        }
        
        if (!passwordRegex.test(password)) {
            alert('Password must be at least 8 characters long, contain letters, numbers, and at least one special character.');
            event.preventDefault();
            return;
        }
    });
});

function validateForm(event) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            // Check username length
            if (username.length < 6) {
                alert("Username must be at least 6 characters long.");
                event.preventDefault(); // Prevent form submission
                return false;
            }

            // Check password length and complexity
            const passwordRegex = /^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/; // At least 8 characters, one letter, one number, one special character
            if (!passwordRegex.test(password)) {
                alert("Password must be at least 8 characters long and include at least one letter, one number, and one special character.");
                event.preventDefault(); // Prevent form submission
                return false;
            }

            // Check if passwords match
            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                event.preventDefault(); // Prevent form submission
                return false;
            }

            return true; // Allow form submission if all validations pass
        }
