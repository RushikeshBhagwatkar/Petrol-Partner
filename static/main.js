/**
 * Petrol Partner — Main JavaScript
 * Core utilities: toast system, mobile menu, auth state observer
 */

// ── Toast Notification System ──
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const colors = {
        success: 'bg-fuel-600 text-white',
        error: 'bg-red-600 text-white',
        info: 'bg-petrol-600 text-white',
        warning: 'bg-amber-500 text-white',
    };
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const toast = document.createElement('div');
    toast.className = `pointer-events-auto flex items-center space-x-3 px-5 py-3 rounded-xl shadow-2xl ${colors[type] || colors.info} toast-enter max-w-sm`;
    toast.innerHTML = `<span>${icons[type] || ''}</span><span class="text-sm font-medium">${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.classList.add('toast-exit'); setTimeout(() => toast.remove(), 300); }, 4000);
}

// ── Mobile Menu ──
document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');
    const closeBtn = document.getElementById('mobile-menu-close');
    const panel = document.getElementById('mobile-menu-panel');

    function openMenu() {
        menu.classList.remove('hidden');
        setTimeout(() => panel.classList.remove('translate-x-full'), 10);
    }
    function closeMenu() {
        panel.classList.add('translate-x-full');
        setTimeout(() => menu.classList.add('hidden'), 300);
    }
    if (menuBtn) menuBtn.addEventListener('click', openMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
});

// ── Firebase Auth State Observer ──
if (typeof firebase !== 'undefined') {
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            console.log('Petrol Partner: User signed in —', user.displayName);
        } else {
            console.log('Petrol Partner: No user signed in.');
        }
    });
}

console.log('⛽ Petrol Partner JS Initialized');
