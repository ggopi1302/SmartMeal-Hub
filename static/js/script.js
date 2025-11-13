const themeToggle = document.getElementById('themeToggle');
    const preferredTheme = localStorage.getItem('theme');

    if (preferredTheme === 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        document.documentElement.removeAttribute('data-bs-theme');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }

    themeToggle.addEventListener('click', function() {
        if (document.documentElement.hasAttribute('data-bs-theme')) {
            document.documentElement.removeAttribute('data-bs-theme');
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    });