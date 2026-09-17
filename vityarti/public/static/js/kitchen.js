/**
 * kitchen.js
 * Kitchen Display System (KDS) and POS Queue management.
 * Real-time polling and Kanban state transitions.
 */

let pollInterval = null;

document.addEventListener('DOMContentLoaded', () => {
  startClock();
  fetchKitchenQueue();
  // Poll live queue every 4 seconds
  pollInterval = setInterval(fetchKitchenQueue, 4000);
});

function startClock() {
  const clockEl = document.getElementById('kds-live-clock');
  setInterval(() => {
    if (clockEl) {
      clockEl.textContent = new Date().toLocaleTimeString();
    }
  }, 1000);
}

async function fetchKitchenQueue() {
  try {
    const res = await fetch('/api/orders/kitchen-queue');
    const data = await res.json();
    if (data.success) {
      renderKitchenBoard(data.queue);
    }
  } catch (err) {
    console.error('Error polling kitchen queue:', err);
  }
}

function renderKitchenBoard(orders) {
  const pendingContainer = document.getElementById('kds-pending-cards');
  const preparingContainer = document.getElementById('kds-preparing-cards');
  const readyContainer = document.getElementById('kds-ready-cards');

  const countPending = document.getElementById('count-pending');
  const countPreparing = document.getElementById('count-preparing');
  const countReady = document.getElementById('count-ready');

  const pending = orders.filter(o => o.order_status === 'pending');
  const preparing = orders.filter(o => o.order_status === 'preparing');
  const ready = orders.filter(o => o.order_status === 'ready');

  if (countPending) countPending.textContent = pending.length;
  if (countPreparing) countPreparing.textContent = preparing.length;
  if (countReady) countReady.textContent = ready.length;

  if (pendingContainer) {
    pendingContainer.innerHTML = pending.length === 0
      ? '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">No pending tickets in queue</div>'
      : pending.map(o => createKDSCardHtml(o, 'pending')).join('');
  }

  if (preparingContainer) {
    preparingContainer.innerHTML = preparing.length === 0
      ? '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">No items currently on grill</div>'
      : preparing.map(o => createKDSCardHtml(o, 'preparing')).join('');
  }

  if (readyContainer) {
    readyContainer.innerHTML = ready.length === 0
      ? '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">Counter is clear</div>'
      : ready.map(o => createKDSCardHtml(o, 'ready')).join('');
  }
}

function createKDSCardHtml(order, stage) {
  const itemsHtml = (order.items || []).map(it => `
    <div class="kds-item-line">
      <span><strong>${it.quantity}x</strong> ${it.item_name}</span>
    </div>
  `).join('');

  let actionBtn = '';
  if (stage === 'pending') {
    actionBtn = `<button class="btn-kds-action btn-prep" onclick="advanceOrderStatus(${order.id}, 'preparing')">🔥 Start Preparation</button>`;
  } else if (stage === 'preparing') {
    actionBtn = `<button class="btn-kds-action btn-ready" onclick="advanceOrderStatus(${order.id}, 'ready')">🔔 Mark Ready for Counter</button>`;
  } else if (stage === 'ready') {
    actionBtn = `<button class="btn-kds-action btn-done" onclick="advanceOrderStatus(${order.id}, 'completed')">✓ Complete & Handover</button>`;
  }

  const orderTime = new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return `
    <div class="kds-card" id="kds-ticket-${order.id}">
      <div class="kds-card-top">
        <div>
          <span style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Token</span>
          <div class="kds-token">${order.token_number}</div>
        </div>
        <div style="text-align: right;">
          <div class="kds-timer">🕒 ${orderTime}</div>
          <span style="font-size: 0.75rem; color: var(--accent-amber);">${order.customer_name || 'Student'}</span>
        </div>
      </div>

      <div class="kds-items">
        ${itemsHtml}
      </div>

      ${order.special_instructions ? `<div class="kds-note">Note: "${order.special_instructions}"</div>` : ''}

      <div class="kds-actions">
        ${actionBtn}
      </div>
    </div>
  `;
}

async function advanceOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch(`/api/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      fetchKitchenQueue();
    } else {
      showToast(data.error || 'Failed to update order status', 'error');
    }
  } catch (err) {
    showToast('Network error updating order status', 'error');
  }
}
