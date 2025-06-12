function initAlertAnimations() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 10000);
    });
}

document.addEventListener('DOMContentLoaded', initAlertAnimations);