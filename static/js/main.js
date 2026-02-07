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
