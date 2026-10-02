/* ═══════════════════════════════════════════════════════════
   Fashion Store — Main JavaScript
   ═══════════════════════════════════════════════════════════ */

// ── Toast Notification ──────────────────────────────────
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = 'toast show' + (type === 'error' ? ' error' : '');
    setTimeout(() => { toast.className = 'toast'; }, 3000);
}

// ── Mobile Navigation ───────────────────────────────────
function toggleMobileMenu() {
    const nav = document.getElementById('mobileNav');
    const overlay = document.getElementById('mobileNavOverlay');
    if (nav && overlay) {
        nav.classList.toggle('open');
        overlay.classList.toggle('open');
        document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
    }
}

// ── Cart Count ──────────────────────────────────────────
async function loadCartCount() {
    try {
        const res = await fetch('/api/cart');
        const data = await res.json();
        updateCartCount(data.count || 0);
    } catch(e) {}
}

function updateCartCount(count) {
    const el = document.getElementById('cartCount');
    if (el) {
        if (count > 0) {
            el.textContent = count;
            el.style.display = 'flex';
        } else {
            el.style.display = 'none';
        }
    }
}

// ── Quick Add to Cart ───────────────────────────────────
async function quickAdd(productId) {
    try {
        const res = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1,
                size: 'M',
                color: ''
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Added to cart!');
            updateCartCount(data.count);
        } else {
            showToast(data.error || 'Failed to add', 'error');
        }
    } catch(e) {
        showToast('Error adding to cart', 'error');
    }
}

// ── Init ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadCartCount();
});
