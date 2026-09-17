/**
 * admin.js
 * Canteen administration, real-time analytics graphs, and inventory management.
 */

document.addEventListener('DOMContentLoaded', () => {
  fetchAnalytics();
  fetchInventory();
});

/* ==========================================================================
   Analytics & KPIs
   ========================================================================== */
async function fetchAnalytics() {
  try {
    const res = await fetch('/api/admin/analytics');
    const data = await res.json();
    if (!data.success) return;

    const m = data.metrics;
    document.getElementById('kpi-revenue').textContent = `₹${parseFloat(m.total_revenue).toFixed(2)}`;
    document.getElementById('kpi-total-orders').textContent = m.total_orders;
    document.getElementById('kpi-active-orders').textContent = m.active_orders;
    document.getElementById('kpi-aov').textContent = `₹${parseFloat(m.avg_order_value).toFixed(2)}`;

    renderCategoryBars(data.category_stats, m.total_revenue);
    renderTopItems(data.top_items);
  } catch (err) {
    console.error('Error fetching analytics:', err);
  }
}

function renderCategoryBars(catStats, totalRevenue) {
  const container = document.getElementById('category-bars');
  if (!container) return;

  if (!catStats || catStats.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted);">No sales data recorded yet.</div>';
    return;
  }

  const maxVal = Math.max(...catStats.map(c => c.total_sales), 1);

  container.innerHTML = catStats.map(c => {
    const pct = Math.min(100, Math.round((c.total_sales / maxVal) * 100));
    return `
      <div class="bar-row">
        <span class="bar-label">${c.category}</span>
        <div class="bar-track">
          <div class="bar-fill fill-amber" style="width: ${pct}%;"></div>
        </div>
        <span class="bar-val">₹${parseFloat(c.total_sales).toFixed(0)}</span>
      </div>
    `;
  }).join('');
}

function renderTopItems(items) {
  const container = document.getElementById('top-items-list');
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted);">No orders recorded yet.</div>';
    return;
  }

  container.innerHTML = items.map((it, idx) => `
    <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.03); padding: 0.75rem 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-glass);">
      <div style="display: flex; align-items: center; gap: 0.8rem;">
        <span style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 800; color: var(--accent-amber); min-width: 20px;">#${idx + 1}</span>
        <div>
          <div style="font-weight: 600; color: #fff; font-size: 0.92rem;">${it.item_name}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${it.category || 'General'} • ${it.total_quantity} portions sold</div>
        </div>
      </div>
      <div style="font-weight: 700; color: var(--accent-emerald); font-size: 0.95rem;">
        ₹${parseFloat(it.total_sales).toFixed(2)}
      </div>
    </div>
  `).join('');
}

/* ==========================================================================
   Inventory & Menu Item CRUD
   ========================================================================== */
async function fetchInventory() {
  const tbody = document.getElementById('inventory-table-body');
  if (!tbody) return;

  try {
    const res = await fetch('/api/menu');
    const data = await res.json();
    if (!data.success) return;

    tbody.innerHTML = data.items.map(it => {
      const isAvailable = it.is_available && it.stock_quantity > 0;
      const statusBadge = isAvailable
        ? '<span class="badge-status" style="background: rgba(16,185,129,0.2); color: var(--accent-emerald);">In Stock</span>'
        : '<span class="badge-status" style="background: rgba(244,63,94,0.2); color: var(--accent-rose);">Out of Stock</span>';

      return `
        <tr>
          <td>
            <strong>${it.name}</strong>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${it.calories} kcal • ${it.prep_time_minutes}m prep</div>
          </td>
          <td>${it.category}</td>
          <td>
            <span style="text-transform: capitalize; font-size: 0.8rem; color: ${it.dietary_type === 'non-veg' ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
              ${it.dietary_type}
            </span>
          </td>
          <td><strong>₹${parseFloat(it.price).toFixed(2)}</strong></td>
          <td>
            <span style="font-weight: 700; color: ${it.stock_quantity <= 15 ? 'var(--accent-rose)' : '#fff'};">
              ${it.stock_quantity}
            </span>
          </td>
          <td>
            <button class="diet-tag-btn" onclick="toggleItemStock(${it.id})" title="Click to toggle availability" style="font-size: 0.75rem; padding: 0.25rem 0.6rem;">
              ${statusBadge}
            </button>
          </td>
          <td>
            <div style="display: flex; gap: 0.4rem;">
              <button class="diet-tag-btn" onclick='openEditItemModal(${JSON.stringify(it)})' style="font-size: 0.75rem;">✏️ Edit</button>
              <button class="diet-tag-btn" onclick="deleteMenuItem(${it.id})" style="font-size: 0.75rem; color: var(--accent-rose);">🗑️</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading inventory:', err);
  }
}

async function toggleItemStock(itemId) {
  try {
    const res = await fetch(`/api/menu/${itemId}/toggle-stock`, {
      method: 'PATCH'
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      fetchInventory();
      fetchAnalytics();
    } else {
      showToast(data.error || 'Failed to toggle stock', 'error');
    }
  } catch (err) {
    showToast('Network error toggling stock', 'error');
  }
}

async function deleteMenuItem(itemId) {
  if (!confirm('Are you sure you want to delete this menu dish?')) return;

  try {
    const res = await fetch(`/api/menu/${itemId}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      fetchInventory();
      fetchAnalytics();
    } else {
      showToast(data.error || 'Failed to delete dish', 'error');
    }
  } catch (err) {
    showToast('Network error deleting dish', 'error');
  }
}

function openAddItemModal() {
  document.getElementById('edit-item-id').value = '';
  document.getElementById('item-modal-title').textContent = '➕ Add New Menu Dish';
  document.getElementById('item-name').value = '';
  document.getElementById('item-desc').value = '';
  document.getElementById('item-price').value = '';
  document.getElementById('item-stock').value = '50';
  document.getElementById('item-prep').value = '10';
  document.getElementById('item-cals').value = '350';

  const modal = document.getElementById('item-modal');
  if (modal) modal.classList.add('open');
}

function openEditItemModal(item) {
  document.getElementById('edit-item-id').value = item.id;
  document.getElementById('item-modal-title').textContent = `✏️ Edit: ${item.name}`;
  document.getElementById('item-name').value = item.name;
  document.getElementById('item-category').value = item.category;
  document.getElementById('item-dietary').value = item.dietary_type;
  document.getElementById('item-desc').value = item.description || '';
  document.getElementById('item-price').value = item.price;
  document.getElementById('item-stock').value = item.stock_quantity;
  document.getElementById('item-prep').value = item.prep_time_minutes;
  document.getElementById('item-cals').value = item.calories;

  const modal = document.getElementById('item-modal');
  if (modal) modal.classList.add('open');
}

function closeItemModal() {
  const modal = document.getElementById('item-modal');
  if (modal) modal.classList.remove('open');
}

async function saveMenuItem(event) {
  event.preventDefault();
  const editId = document.getElementById('edit-item-id').value;
  const isEdit = Boolean(editId);

  const payload = {
    name: document.getElementById('item-name').value.trim(),
    category: document.getElementById('item-category').value,
    dietary_type: document.getElementById('item-dietary').value,
    description: document.getElementById('item-desc').value.trim(),
    price: parseFloat(document.getElementById('item-price').value),
    stock_quantity: parseInt(document.getElementById('item-stock').value),
    prep_time_minutes: parseInt(document.getElementById('item-prep').value),
    calories: parseInt(document.getElementById('item-cals').value),
    image_url: '/static/images/burger.jpg'
  };

  const url = isEdit ? `/api/menu/${editId}` : '/api/menu';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      closeItemModal();
      fetchInventory();
      fetchAnalytics();
    } else {
      showToast(data.error || 'Failed to save menu dish', 'error');
    }
  } catch (err) {
    showToast('Network error saving menu item', 'error');
  }
}
