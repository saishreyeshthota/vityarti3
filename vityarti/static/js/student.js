/**
 * student.js
 * Menu catalog management, live filtering, and product interactions for student ordering.
 */

const FALLBACK_STUDENT_ITEMS = [
  {
    id: 1,
    name: "Artisan Veggie Burger Combo",
    category: "Snacks",
    description: "Char-grilled herb patty, melted cheddar, crisp lettuce, farm tomato on a brioche bun with golden fries & dip.",
    price: 120.00,
    is_available: 1,
    stock_quantity: 40,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 12,
    calories: 540,
    rating: 4.9
  },
  {
    id: 2,
    name: "Royal Mysore Masala Dosa",
    category: "Breakfast",
    description: "Crispy golden crepe smeared with spicy red chutney, stuffed with spiced potato mash, served with coconut chutney & sambar.",
    price: 85.00,
    is_available: 1,
    stock_quantity: 60,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 8,
    calories: 380,
    rating: 4.9
  },
  {
    id: 3,
    name: "Signature Caramel Iced Macchiato",
    category: "Beverages",
    description: "Velvety cold-brew espresso with chilled whole milk, rich vanilla syrup, and decadent golden caramel swirl.",
    price: 95.00,
    is_available: 1,
    stock_quantity: 75,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 4,
    calories: 210,
    rating: 4.8
  },
  {
    id: 4,
    name: "Mediterranean Nourish Bowl",
    category: "Healthy",
    description: "Fluffy quinoa, creamy avocado, crisp chickpeas, heirloom tomatoes, English cucumber ribbons, and tahini drizzle.",
    price: 140.00,
    is_available: 1,
    stock_quantity: 35,
    dietary_type: "vegan",
    image_url: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 10,
    calories: 390,
    rating: 4.7
  },
  {
    id: 5,
    name: "Steaming Idli Sambar Platter (3 pcs)",
    category: "Breakfast",
    description: "Melt-in-mouth fermented steamed rice-lentil cakes immersed in hot aromatic drumstick sambar and fresh mint chutney.",
    price: 55.00,
    is_available: 1,
    stock_quantity: 50,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 5,
    calories: 260,
    rating: 4.6
  },
  {
    id: 6,
    name: "Paneer Butter Masala Thali",
    category: "Lunch",
    description: "Tender cottage cheese cubes simmered in rich buttery tomato cashew gravy, served with 2 butter naans, jeera rice, and salad.",
    price: 160.00,
    is_available: 1,
    stock_quantity: 45,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 15,
    calories: 680,
    rating: 4.9
  },
  {
    id: 7,
    name: "Schezwan Wok Hakka Noodles",
    category: "Lunch",
    description: "Wok-tossed noodles with shredded bell peppers, cabbage, spring onion, and house spicy garlic Schezwan sauce.",
    price: 110.00,
    is_available: 1,
    stock_quantity: 50,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 10,
    calories: 480,
    rating: 4.6
  },
  {
    id: 8,
    name: "Classic Bombay Vada Pav (2 pcs)",
    category: "Snacks",
    description: "Spiced potato fritters encased in fluffy pav buns, layered with fiery garlic chutney and fried green chillies.",
    price: 45.00,
    is_available: 1,
    stock_quantity: 80,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 5,
    calories: 320,
    rating: 4.8
  },
  {
    id: 9,
    name: "Spiced Kulhad Adrak Chai",
    category: "Beverages",
    description: "Slow-brewed Assam tea leaves infused with crushed fresh ginger, green cardamom, and served steaming in an earthen kulhad.",
    price: 25.00,
    is_available: 1,
    stock_quantity: 120,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 3,
    calories: 90,
    rating: 4.9
  },
  {
    id: 10,
    name: "Fresh Alphonso Mango Smoothie",
    category: "Beverages",
    description: "Thick blend of real Alphonso mango pulp, chilled Greek yogurt, honey, and crushed pistachio garnish.",
    price: 75.00,
    is_available: 1,
    stock_quantity: 40,
    dietary_type: "veg",
    image_url: "https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 5,
    calories: 230,
    rating: 4.8
  },
  {
    id: 11,
    name: "Peri-Peri Golden Crinkle Fries",
    category: "Snacks",
    description: "Crispy golden crinkle-cut potato fries dusted with tangy, spicy African peri-peri seasoning and garlic mayo dip.",
    price: 65.00,
    is_available: 1,
    stock_quantity: 60,
    dietary_type: "vegan",
    image_url: "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 6,
    calories: 310,
    rating: 4.7
  },
  {
    id: 12,
    name: "Protein Sprouted Chickpea Salad",
    category: "Healthy",
    description: "Sprouted organic chickpeas, pomegranate pearls, diced cucumber, tomatoes, tossed with extra virgin olive oil & chaat masala.",
    price: 90.00,
    is_available: 1,
    stock_quantity: 30,
    dietary_type: "vegan",
    image_url: "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80",
    prep_time_minutes: 6,
    calories: 220,
    rating: 4.8
  }
];

let allMenuItems = (window.INITIAL_MENU_ITEMS && window.INITIAL_MENU_ITEMS.length > 0)
  ? window.INITIAL_MENU_ITEMS
  : FALLBACK_STUDENT_ITEMS;

let activeCategory = 'all';
let activeDietary = 'all';
let searchQuery = '';

document.addEventListener('DOMContentLoaded', () => {
  // If no items were pre-rendered, render them immediately from memory
  const grid = document.getElementById('menu-grid');
  if (grid && (!grid.children || grid.children.length === 0)) {
    renderMenuGrid(allMenuItems);
  }
  fetchMenuItems();
});

async function fetchMenuItems() {
  const grid = document.getElementById('menu-grid');
  const countBadge = document.getElementById('items-count-badge');
  if (!grid) return;

  // Only show loading placeholder if grid is completely empty
  if (allMenuItems.length === 0 && (!grid.children || grid.children.length === 0)) {
    grid.innerHTML = '<div style="color: var(--text-secondary); text-align: center; grid-column: 1/-1; padding: 3rem;">Loading today\'s canteen delights...</div>';
  }

  try {
    const res = await fetch('/api/menu');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.success && Array.isArray(data.items) && data.items.length > 0) {
      allMenuItems = data.items;
      applyFilters();
    }
  } catch (err) {
    console.warn('Notice fetching menu API (using rendered/cached items):', err);
    if (allMenuItems.length === 0) {
      allMenuItems = FALLBACK_STUDENT_ITEMS;
      applyFilters();
    }
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
    const catMatch = activeCategory === 'all' || (item.category && item.category.toLowerCase() === activeCategory.toLowerCase());
    
    // Dietary match
    const dietMatch = activeDietary === 'all' || (item.dietary_type && item.dietary_type.toLowerCase() === activeDietary.toLowerCase());

    // Search query match
    const searchMatch = !searchQuery || 
      (item.name && item.name.toLowerCase().includes(searchQuery)) || 
      (item.description && item.description.toLowerCase().includes(searchQuery)) ||
      (item.category && item.category.toLowerCase().includes(searchQuery));

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
          <img src="${item.image_url}" alt="${item.name}" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80'">
          <div class="card-badge-top">
            <span class="diet-pill ${dietClass}">${dietIcon}</span>
          </div>
          <div class="rating-badge">
            <span>★</span>
            <span>${parseFloat(item.rating || 4.8).toFixed(1)}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="card-category">${item.category}</div>
          <h4 class="card-title">${item.name}</h4>
          <p class="card-desc">${item.description}</p>

          <div class="card-meta">
            <span>⏱️ ${item.prep_time_minutes || 10} mins</span>
            <span>🔥 ${item.calories || 300} kcal</span>
            <span>📦 ${item.stock_quantity || 30} left</span>
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
