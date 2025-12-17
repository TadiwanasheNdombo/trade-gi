// script.js for dashboard interactivity

/**
 * Displays a toast notification at the bottom-right of the screen.
 * @param {string} message The message to display.
 * @param {string} iconClass The Font Awesome icon class (e.g., 'fas fa-check-circle').
 */
function showToast(message, iconClass = 'fas fa-info-circle') {
    const toast = document.createElement('div');
    toast.className = 'notification-toast';
    toast.innerHTML = `<div class="toast-content"><i class="${iconClass}"></i><span>${message}</span></div>`;
    document.body.appendChild(toast);

    // Animate in and then out
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 4000);
}

document.addEventListener('DOMContentLoaded', function() {
    // New Agreement button click handler (show modal)
    const newAgreementBtn = document.getElementById('newAgreementBtn');
    const newAgreementModal = document.getElementById('newAgreementModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    if (newAgreementBtn && newAgreementModal && closeModalBtn) {
        newAgreementBtn.addEventListener('click', function() {
            newAgreementModal.style.display = 'block';
        });
        closeModalBtn.addEventListener('click', function() {
            newAgreementModal.style.display = 'none';
        });
        // Hide modal when clicking outside modal content
        window.addEventListener('click', function(event) {
            if (event.target === newAgreementModal) {
                newAgreementModal.style.display = 'none';
            }
        });
    }

    // Export Report button click handler
    const exportReportBtn = document.getElementById('exportReportBtn');
    if (exportReportBtn) {
        exportReportBtn.addEventListener('click', function() {
            showToast('Export functionality is coming soon!', 'fas fa-file-export');
        });
    }

    // Action buttons (Track, Review, Edit, Escalate)
    document.querySelectorAll('.action-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const ref = btn.getAttribute('data-ref');
            showToast(`Performing action for agreement: ${ref}`, 'fas fa-cogs');
        });
    });
});
