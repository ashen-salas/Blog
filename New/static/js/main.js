document.addEventListener('DOMContentLoaded', () => {
    const dashboardLink = document.getElementById('dashboard-link');

    if (dashboardLink) {
        const isAuthenticated = document.body.dataset.authenticated === 'true';
        const dashboardUrl = dashboardLink.dataset.dashboardUrl;

        console.log("¿Usuario autenticado?", isAuthenticated); // Depuración

        dashboardLink.addEventListener('click', (e) => {
            e.preventDefault();

            if (isAuthenticated) {
                console.log("Redirigiendo a:", dashboardUrl);
                window.location.href = dashboardUrl;
            } else {
                alert('No tienes permiso de administrador');
            }
        });
    }
});
