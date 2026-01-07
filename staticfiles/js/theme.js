/**
 * Premium Theme Manager for Chandran Electronics
 * Handles Light/Dark mode transitions and persistence.
 */
const themeManager = {
    init() {
        // Run immediately to prevent flash of light mode
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.classList.add('dark-mode');
            document.body.classList.add('dark-mode');
        } else {
            document.documentElement.classList.remove('dark-mode');
            document.body.classList.remove('dark-mode');
        }

        // Setup listeners once DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    },

    setup() {
        this.syncUI();
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    },

    toggle() {
        const isDark = document.body.classList.contains('dark-mode');
        const newTheme = isDark ? 'light' : 'dark';
        this.setTheme(newTheme);
        this.showToast(newTheme);
    },

    setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-mode');
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark-mode');
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
        this.syncUI();
    },

    syncUI() {
        const isDark = document.body.classList.contains('dark-mode');
        const icons = document.querySelectorAll('#theme-icon');
        icons.forEach(icon => {
            icon.textContent = isDark ? 'light_mode' : 'dark_mode';
        });

        // Update theme toggle button description if exists
        const toggles = document.querySelectorAll('#theme-toggle');
        toggles.forEach(toggle => {
            toggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
        });
    },

    showToast(theme) {
        if (window.Swal) {
            const Toast = Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                background: theme === 'dark' ? '#1E1E1E' : '#FFFFFF',
                color: theme === 'dark' ? '#FFFFFF' : '#1E1E1E',
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                }
            });

            Toast.fire({
                icon: 'info',
                title: `${theme.charAt(0).toUpperCase() + theme.slice(1)} mode enabled`
            });
        }
    }
};

// Initialize early
themeManager.init();

// Export for global access
window.themeManager = themeManager;
function toggleDarkMode() { themeManager.toggle(); }
