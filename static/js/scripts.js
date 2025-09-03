document.addEventListener('DOMContentLoaded', () => {
    // Menú hamburguesa
    const toggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    toggler.addEventListener('click', () => {
        navbarCollapse.classList.toggle('show');
        const isExpanded = navbarCollapse.classList.contains('show');
        toggler.setAttribute('aria-expanded', isExpanded);
    });

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                navbarCollapse.classList.remove('show');
                toggler.setAttribute('aria-expanded', 'false');
            }
        });
    });

    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && !navbarCollapse.contains(e.target) && !toggler.contains(e.target)) {
            navbarCollapse.classList.remove('show');
            toggler.setAttribute('aria-expanded', 'false');
        }
    });

    // Modales
    const modals = document.querySelectorAll('.modal');
    const modalCloses = document.querySelectorAll('.modal-close');

    // Abrir modales (necesitas un botón para dispararlos, p.ej., un botón de perfil)
    document.querySelectorAll('[data-modal]').forEach(button => {
        button.addEventListener('click', () => {
            const modalId = button.getAttribute('data-modal');
            document.getElementById(modalId).style.display = 'block';
        });
    });

    // Cerrar modales
    modalCloses.forEach(close => {
        close.addEventListener('click', () => {
            close.closest('.modal').style.display = 'none';
        });
    });

    // Cerrar modales al hacer clic fuera
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Cerrar alertas
    document.querySelectorAll('.alert-close').forEach(close => {
        close.addEventListener('click', () => {
            close.closest('.alert').style.display = 'none';
        });
    });
});