/**
 * app.js
 * Global client controller for CampusBite Canteen System.
 * Manages Cart state, Toast Alerts, Role switching, and Shared Modals.
 */

// Global state
const AppState = {
  cart: [],
  user: null,
  selectedTopupAmount: 500
};

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  loadCartFromStorage();
  updateCartBadge();
  fetchCurrentUser();
});

/* ==========================================================================
   User & Persona Switcher
   ========================================================================== */
async function fetchCurrentUser() {
  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    if (data.success && data.user) {
      AppState.user = data.user;
      updateWalletDisplay(data.user.wallet_balance);
      const selector = document.getElementById('persona-selector');
      if (selector) selector.value = data.user.role;
    }
  } catch (err) {
    console.error('Error loading current user:', err);
  }
}

async function switchDemoPersona(role) {
  try {
    const res = await fetch('/api/auth/switch-role', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      AppState.user = data.user;
      updateWalletDisplay(data.user.wallet_balance);
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } else {
      showToast(data.error || 'Failed to switch role', 'error');
    }
  } catch (err) {
    showToast('Network error while switching role', 'error');
  }
}

function updateWalletDisplay(balance) {
  const badge = document.getElementById('nav-wallet-balance');
  if (badge) {
    badge.textContent = `₹${parseFloat(balance).toFixed(2)}`;
  }
  const modalBal = document.getElementById('modal-current-balance');
  if (modalBal) {
    modalBal.textContent = `₹${parseFloat(balance).toFixed(2)}`;
  }
}

/* ==========================================================================
   Cart Drawer Management
   ========================================================================== */
function loadCartFromStorage() {
  try {
    const saved = localStorage.getItem('campusbite_cart');
    if (saved) {
      AppState.cart = JSON.parse(saved);
    }
  } catch (e) {
    AppState.cart = [];
  }
}

function saveCartToStorage() {
  localStorage.setItem('campusbite_cart', JSON.stringify(AppState.cart));
  updateCartBadge();
  renderCartDrawer();
}

function updateCartBadge() {
  const badge = document.getElementById('cart-count');
  if (!badge) return;
  const totalQty = AppState.cart.reduce((sum, it) => sum + it.quantity, 0);
  badge.textContent = totalQty;
  if (totalQty > 0) {
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

function toggleCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  if (!drawer || !overlay) return;

  const isOpen = drawer.classList.contains('open');
  if (isOpen) {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
  } else {
    renderCartDrawer();
    drawer.classList.add('open');
    overlay.classList.add('open');
  }
}

function addToCart(item) {
  const existing = AppState.cart.find(it => it.id === item.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    AppState.cart.push({
      id: item.id,
      name: item.name,
      price: parseFloat(item.price),
      quantity: 1,
      image_url: item.image_url
    });
  }
  saveCartToStorage();
  showToast(`Added "${item.name}" to tray!`, 'success');

  // Gentle pulse effect on cart button
  const cartBtn = document.getElementById('cart-toggle-btn');
  if (cartBtn) {
    cartBtn.style.transform = 'scale(1.2)';
    setTimeout(() => cartBtn.style.transform = '', 200);
  }
}

function updateItemQuantity(itemId, delta) {
  const idx = AppState.cart.findIndex(it => it.id === itemId);
  if (idx === -1) return;

  AppState.cart[idx].quantity += delta;
  if (AppState.cart[idx].quantity <= 0) {
    AppState.cart.splice(idx, 1);
  }
  saveCartToStorage();
}

function renderCartDrawer() {
  const container = document.getElementById('cart-items-container');
  const footer = document.getElementById('cart-footer');
  const subtotalEl = document.getElementById('cart-subtotal');
  const totalEl = document.getElementById('cart-total-payable');

  if (!container) return;

  if (AppState.cart.length === 0) {
    container.innerHTML = `
      <div class="cart-empty-state">
        <div style="font-size: 3rem;">🥗</div>
        <p style="font-weight: 600; color: #fff;">Your tray is empty</p>
        <span style="font-size: 0.85rem;">Browse the delicious menu and add freshly made meals or beverages.</span>
      </div>
    `;
    if (footer) footer.style.display = 'none';
    return;
  }

  let subtotal = 0;
  container.innerHTML = AppState.cart.map(it => {
    const itemTotal = it.price * it.quantity;
    subtotal += itemTotal;
    return `
      <div class="cart-item-row">
        <div class="cart-item-info">
          <div class="cart-item-name">${it.name}</div>
          <div class="cart-item-price">₹${it.price.toFixed(2)} each</div>
        </div>
        <div class="qty-control">
          <button class="qty-btn" onclick="updateItemQuantity(${it.id}, -1)">-</button>
          <span class="qty-val">${it.quantity}</span>
          <button class="qty-btn" onclick="updateItemQuantity(${it.id}, 1)">+</button>
        </div>
        <div style="font-weight: 700; color: #fff; font-size: 0.95rem; min-width: 55px; text-align: right;">
          ₹${itemTotal.toFixed(2)}
        </div>
      </div>
    `;
  }).join('');

  if (footer) {
    footer.style.display = 'flex';
    subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
    totalEl.innerHTML = `<span>₹${subtotal.toFixed(2)}</span>`;
  }
}

/* ==========================================================================
   Checkout & Order Placement
   ========================================================================== */
async function checkoutOrder() {
  if (AppState.cart.length === 0) {
    showToast('Your meal tray is empty!', 'error');
    return;
  }

  const specialInstructions = document.getElementById('special-instructions')?.value || '';
  const payload = {
    items: AppState.cart.map(it => ({ item_id: it.id, quantity: it.quantity })),
    payment_method: 'wallet',
    special_instructions: specialInstructions
  };

  const checkoutBtn = document.getElementById('btn-checkout');
  if (checkoutBtn) {
    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<span>⏳ Processing Payment...</span>';
  }

  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      // Clear cart
      AppState.cart = [];
      saveCartToStorage();
      toggleCartDrawer();

      // Update wallet balance on screen
      if (data.new_wallet_balance !== undefined) {
        updateWalletDisplay(data.new_wallet_balance);
      }

      showToast(`Order Placed! Token #${data.order.token_number}`, 'success');
      showReceiptModal(data.order);
    } else {
      showToast(data.error || 'Failed to place order', 'error');
      if (data.error && data.error.includes('Insufficient wallet')) {
        setTimeout(openWalletModal, 600);
      }
    }
  } catch (err) {
    showToast('Network error during checkout', 'error');
  } finally {
    if (checkoutBtn) {
      checkoutBtn.disabled = false;
      checkoutBtn.innerHTML = '<span>⚡ Place Order & Generate Token</span>';
    }
  }
}

/* ==========================================================================
   Receipt & Token Modal
   ========================================================================== */
function showReceiptModal(order) {
  const modal = document.getElementById('token-modal');
  if (!modal) return;

  document.getElementById('receipt-token-num').textContent = order.token_number;
  document.getElementById('receipt-order-ref').textContent = order.order_number;
  document.getElementById('receipt-customer-name').textContent = (AppState.user && AppState.user.full_name) || 'Campus Student';
  document.getElementById('receipt-date-time').textContent = new Date().toLocaleString();
  document.getElementById('receipt-total-price').textContent = `₹${parseFloat(order.total_amount).toFixed(2)}`;

  const body = document.getElementById('receipt-items-body');
  body.innerHTML = (order.items || []).map(it => `
    <tr>
      <td>${it.name || it.item_name}</td>
      <td style="text-align: center;">${it.quantity}</td>
      <td style="text-align: right;">₹${(it.subtotal || (it.price * it.quantity)).toFixed(2)}</td>
    </tr>
  `).join('');

  modal.classList.add('open');
}

function closeTokenModal() {
  const modal = document.getElementById('token-modal');
  if (modal) modal.classList.remove('open');
}

/* ==========================================================================
   Wallet Top-up Modal
   ========================================================================== */
function openWalletModal() {
  const modal = document.getElementById('wallet-modal');
  if (modal) modal.classList.add('open');
}

function closeWalletModal() {
  const modal = document.getElementById('wallet-modal');
  if (modal) modal.classList.remove('open');
}

function selectTopupAmount(amount) {
  AppState.selectedTopupAmount = amount;
  const input = document.getElementById('custom-recharge-amount');
  if (input) input.value = amount;
}

async function executeWalletRecharge() {
  const input = document.getElementById('custom-recharge-amount');
  const amount = parseFloat(input.value);

  if (!amount || amount <= 0) {
    showToast('Please enter a valid recharge amount', 'error');
    return;
  }

  try {
    const res = await fetch('/api/wallet/topup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      updateWalletDisplay(data.wallet_balance);
      closeWalletModal();
    } else {
      showToast(data.error || 'Recharge failed', 'error');
    }
  } catch (err) {
    showToast('Network error during wallet recharge', 'error');
  }
}

/* ==========================================================================
   Toast Notification System
   ========================================================================== */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? '✅' : type === 'error' ? '⚠️' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
