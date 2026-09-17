/**
 * student.js
 * Menu catalog management, live filtering, and product interactions for student ordering.
 */

let allMenuItems = [];
let activeCategory = 'all';
let activeDietary = 'all';
let searchQuery = '';

document.addEventListener('DOMContentLoaded', () => {
  fetchMenuItems();
});

async function fetchMenuItems() {
  const grid = document.getElementById('menu-grid');
  const countBadge = document.getElementById('items-count-badge');
  if (!grid) return;

  grid.innerHTML = '<div style="color: var(--text-secondary); text-align: center; grid-column: 1/-1; padding: 3rem;">Loading today\'s canteen delights...</div>';

  try {
    const res = await fetch('/api/menu');
    const data = await res.json();
    if (data.success) {
      allMenuItems = data.items;
      applyFilters();
    } else {
      grid.innerHTML = '<div style="color: var(--accent-rose); text-align: center; grid-column: 1/-1;">Failed to load canteen menu.</div>';
    }
  } catch (err) {
    console.error(err);
    grid.innerHTML = '<div style="color: var(--accent-rose); text-align: center; grid-column: 1/-1;">Network error fetching menu.</div>';
  }
}

function selectCategory(category, btn) {
  activeCategory = category;
  document.querySelectorAll('.category-pill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  applyFilters();
}

function selectDietary(diet, btn) {
  activeDietary = diet;
  document.querySelectorAll('.diet-tag-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  applyFilters();
}

function filterMenuItems() {
  const input = document.getElementById('menu-search-input');
  searchQuery = input ? input.value.trim().toLowerCase() : '';
  applyFilters();
}

function applyFilters() {
  const filtered = allMenuItems.filter(item => {
    // Category match
    const catMatch = activeCategory === 'all' || item.category.toLowerCase() === activeCategory.toLowerCase();
    
    // Dietary match
    const dietMatch = activeDietary === 'all' || item.dietary_type.toLowerCase() === activeDietary.toLowerCase();

    // Search query match
    const searchMatch = !searchQuery || 
      item.name.toLowerCase().includes(searchQuery) || 
      item.description.toLowerCase().includes(searchQuery) ||
      item.category.toLowerCase().includes(searchQuery);

    return catMatch && dietMatch && searchMatch;
  });

  renderMenuGrid(filtered);
}

function renderMenuGrid(items) {
  const grid = document.getElementById('menu-grid');
  const countBadge = document.getElementById('items-count-badge');
  if (!grid) return;

  if (countBadge) {
    countBadge.textContent = `(${items.length} dishes available)`;
  }

  if (items.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem 2rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-glass);">
        <div style="font-size: 3.5rem; margin-bottom: 0.8rem;">🔍</div>
        <h3 style="color: #fff; margin-bottom: 0.4rem;">No matching canteen dishes</h3>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">Try selecting a different category or clearing your search keywords.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = items.map(item => {
    // Diet badge
    let dietClass = 'diet-veg';
    let dietIcon = '🌱 Veg';
    if (item.dietary_type === 'non-veg') {
      dietClass = 'diet-non-veg';
      dietIcon = '🍗 Non-Veg';
    } else if (item.dietary_type === 'vegan') {
      dietClass = 'diet-vegan';
      dietIcon = '🌿 Vegan';
    }

    const isAvailable = item.is_available && item.stock_quantity > 0;
    const actionBtn = isAvailable
      ? `<button class="btn-add-cart" onclick='addToCart(${JSON.stringify(item)})'>
           <span>+ Add to Tray</span>
         </button>`
      : `<button class="btn-out-stock" disabled>Sold Out</button>`;

    return `
      <article class="food-card" id="dish-card-${item.id}">
        <div class="card-img-wrapper">
          <img src="${item.image_url}" alt="${item.name}" loading="lazy" onerror="this.src='/static/images/burger.jpg'">
          <div class="card-badge-top">
            <span class="diet-pill ${dietClass}">${dietIcon}</span>
          </div>
          <div class="rating-badge">
            <span>★</span>
            <span>${parseFloat(item.rating).toFixed(1)}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="card-category">${item.category}</div>
          <h4 class="card-title">${item.name}</h4>
          <p class="card-desc">${item.description}</p>

          <div class="card-meta">
            <span>⏱️ ${item.prep_time_minutes} mins</span>
            <span>🔥 ${item.calories} kcal</span>
            <span>📦 ${item.stock_quantity} left</span>
          </div>

          <div class="card-footer">
            <div class="card-price">
              <span>₹</span>${parseFloat(item.price).toFixed(2)}
            </div>
            ${actionBtn}
          </div>
        </div>
      </article>
    `;
  }).join('');
}
