(function () {
  // Enhanced Micro-interactions for Chandran Electronics
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  function createToast() {
    var t = document.createElement('div');
    t.id = 'mi-toast';
    t.style.position = 'fixed';
    t.style.right = '20px';
    t.style.bottom = '20px';
    t.style.zIndex = 99999;
    document.body.appendChild(t);
    return t;
  }
  var toastRoot = null;
  function showToast(msg, type) {
    if (!toastRoot) toastRoot = createToast();
    var el = document.createElement('div');
    el.className = 'mi-toast-item';
    el.textContent = msg;
    // Premium styling
    el.style.background = type === 'error' ? 'linear-gradient(90deg, #b91c1c, #ef4444)' : 'linear-gradient(90deg, #1e1b4b, #4f46e5)';
    el.style.color = '#fff';
    el.style.padding = '12px 20px';
    el.style.borderRadius = '12px';
    el.style.marginTop = '10px';
    el.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    el.style.fontWeight = '600';
    el.style.fontFamily = 'Inter, sans-serif';
    toastRoot.appendChild(el);

    requestAnimationFrame(function () {
      el.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      el.style.opacity = '1';
      el.style.transform = 'none';
    });

    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transform = 'translateY(10px)';
      setTimeout(function () { el.remove(); }, 400);
    }, 3000);
  }

  function bounce(el) {
    if (!el) return;
    el.animate([
      { transform: 'scale(1)' },
      { transform: 'scale(1.1)' },
      { transform: 'scale(0.95)' },
      { transform: 'scale(1)' }
    ], { duration: 300, easing: 'ease-out' });
  }

  function updateBadge(id, count) {
    var badge = document.getElementById(id);
    if (!badge) return;
    badge.textContent = count;
    if (count > 0) {
      badge.style.display = 'flex';
      badge.animate([
        { transform: 'scale(1)', opacity: 1 },
        { transform: 'scale(1.5)', opacity: 0.5 },
        { transform: 'scale(1)', opacity: 1 }
      ], { duration: 400 });
    } else {
      badge.style.display = 'none';
    }
  }

  function csrf() {
    var c = document.cookie.match(/csrftoken=([^;]+)/);
    return c ? c[1] : '';
  }

  function setup() {
    // Add to Cart Logic
    qsa('[data-action="add-to-cart"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var slug = btn.getAttribute('data-product-slug') || btn.getAttribute('data-product-id');
        if (!slug) return;

        bounce(btn);

        var url = '/ajax/add_to_cart/' + encodeURIComponent(slug) + '/';
        fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrf(), 'Accept': 'application/json' }
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              updateBadge('cart-badge', data.cart_count);
              showToast('Added to Cart! ⚡');
            } else {
              showToast(data.error || 'Failed to add', 'error');
            }
          })
          .catch(() => showToast('Network Error', 'error'));
      });
    });

    // Toggle Wishlist Logic
    qsa('[data-action="toggle-wishlist"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var slug = btn.getAttribute('data-product-slug') || btn.getAttribute('data-product-id');
        if (!slug) return;

        bounce(btn);

        var url = '/ajax/add_to_wishlist/' + encodeURIComponent(slug) + '/';
        fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrf(), 'Accept': 'application/json' }
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              updateBadge('wishlist-badge', data.wishlist_count);
              if (data.action === 'added') {
                btn.classList.add('in-wishlist');
                showToast('Saved to Wishlist! ❤️');
              } else {
                btn.classList.remove('in-wishlist');
                showToast('Removed from Wishlist');
              }
            }
          })
          .catch(() => showToast('Network Error', 'error'));
      });
    });

    // Update Quantity Logic
    qsa('[data-action="update-quantity"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var slug = btn.getAttribute('data-slug');
        var action = btn.getAttribute('data-update-action'); // 'increase' or 'decrease'
        if (!slug || !action) return;

        bounce(btn);

        var url = '/ajax/update_cart_quantity/' + encodeURIComponent(slug) + '/' + action + '/';
        fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrf(), 'Accept': 'application/json' }
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              updateBadge('cart-badge', data.cart_count);

              // Update DOM elements if on Cart Page
              var row = btn.closest('.cart-entry');
              if (row) {
                var qtySpan = row.querySelector('.qty-display');
                if (qtySpan) qtySpan.textContent = data.new_quantity;

                var itemTotal = row.querySelector('.item-total-price');
                if (itemTotal) itemTotal.textContent = '₹' + data.item_total.toFixed(2);
              }

              // Update Global Cart Totals
              var subtotalEl = document.getElementById('cart-subtotal');
              var totalEl = document.getElementById('cart-total');
              var discountEl = document.getElementById('cart-discount-amount');

              if (data.original_total && subtotalEl) subtotalEl.textContent = '₹' + data.original_total.toFixed(2);
              if (data.cart_total && totalEl) totalEl.textContent = '₹' + data.cart_total.toFixed(2);
              if (data.discount_amount && discountEl) discountEl.textContent = '- ₹' + data.discount_amount.toFixed(2);

              if (data.new_quantity === 0 && row) {
                row.remove();
                if (data.cart_count === 0) location.reload(); // Show empty state
              }
            } else {
              showToast(data.error || 'Update failed', 'error');
            }
          })
          .catch(() => showToast('Network Error', 'error'));
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup); else setup();

  window.MicroInteractions = { showToast: showToast, updateBadge: updateBadge };
})();
