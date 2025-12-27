// Authentication check script
// Add this to all protected pages

(function () {
    // Check if user is authenticated
    if (sessionStorage.getItem('sg200_authenticated') !== 'true') {
        // Redirect to login page
        window.location.href = 'login.html';
    }

    // Update username display if element exists
    document.addEventListener('DOMContentLoaded', function () {
        const username = sessionStorage.getItem('sg200_username') || 'User';
        const usernameElements = document.querySelectorAll('.navbar-item span');
        usernameElements.forEach(function (el) {
            if (el.textContent === 'John Doe') {
                el.textContent = username;
            }
        });
    });

    // Logout function
    window.logout = function () {
        sessionStorage.removeItem('sg200_authenticated');
        sessionStorage.removeItem('sg200_username');
        window.location.href = 'login.html';
    };
})();
