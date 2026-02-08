// ===== Courses Dropdown Toggle =====
const dropdown = document.getElementById('coursesDropdown');
const trigger = document.getElementById('dropdownTrigger');

trigger.addEventListener('click', function (e) {
    e.stopPropagation();
    dropdown.classList.toggle('open');
});

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

// Close dropdown when a link inside is clicked
dropdown.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });
});

// ===== Mobile Hamburger Toggle =====
const hamburger = document.getElementById('hamburger');
const navbar = document.getElementById('navbar');

hamburger.addEventListener('click', function () {
    navbar.classList.toggle('mobile-open');
});

// ===== Signup & Login Modals =====
// These elements only exist when user is NOT logged in (Jinja2 conditional)
const signupModal = document.getElementById('signupModal');
const loginModal = document.getElementById('loginModal');

if (signupModal && loginModal) {
    const openSignupBtn = document.getElementById('openSignupModal');
    const closeSignupBtn = document.getElementById('closeSignupModal');
    const signupForm = document.getElementById('signupForm');
    const signupError = document.getElementById('signupError');

    const openLoginBtn = document.getElementById('openLoginModal');
    const closeLoginBtn = document.getElementById('closeLoginModal');
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    const switchToLogin = document.getElementById('switchToLogin');
    const switchToSignup = document.getElementById('switchToSignup');

    function openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    function closeAllModals() {
        closeModal(signupModal);
        closeModal(loginModal);
    }

    // Open modals
    openSignupBtn.addEventListener('click', function () {
        openModal(signupModal);
    });

    openLoginBtn.addEventListener('click', function () {
        openModal(loginModal);
    });

    // Close buttons
    closeSignupBtn.addEventListener('click', function () {
        closeModal(signupModal);
    });

    closeLoginBtn.addEventListener('click', function () {
        closeModal(loginModal);
    });

    // Switch between modals
    switchToLogin.addEventListener('click', function (e) {
        e.preventDefault();
        closeModal(signupModal);
        openModal(loginModal);
    });

    switchToSignup.addEventListener('click', function (e) {
        e.preventDefault();
        closeModal(loginModal);
        openModal(signupModal);
    });

    // Close on overlay click
    [signupModal, loginModal].forEach(function (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) closeModal(modal);
        });
    });

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAllModals();
    });

    // Handle signup form submission
    signupForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        signupError.textContent = '';

        const formData = new FormData(signupForm);

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                signupError.textContent = data.detail || 'Something went wrong';
                return;
            }

            // Server sets cookie — reload page so middleware picks it up
            window.location.reload();
        } catch (err) {
            signupError.textContent = 'Network error. Please try again.';
        }
    });

    // Handle login form submission
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        loginError.textContent = '';

        const formData = new FormData(loginForm);

        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                loginError.textContent = data.detail || 'Something went wrong';
                return;
            }

            // Server sets cookie — reload page so middleware picks it up
            window.location.reload();
        } catch (err) {
            loginError.textContent = 'Network error. Please try again.';
        }
    });
}
