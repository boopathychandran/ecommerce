document.addEventListener('DOMContentLoaded', () => {
    // Add overlay if it doesn't exist
    if (!document.querySelector('.page-transition-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'page-transition-overlay';
        document.body.appendChild(overlay);
    }

    // Intercept clicks on links
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            // If it's a valid internal link and not just a hash or JS
            if (href && href.startsWith('/') && !href.startsWith('#') && !link.hasAttribute('target')) {
                e.preventDefault();
                document.body.classList.add('leaving');

                // Wait for animation (400ms match CSS)
                setTimeout(() => {
                    window.location.href = href;
                }, 400);
            }
        });
    });
});
