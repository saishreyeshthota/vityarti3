# CampusBite — Smart Canteen Management System

> **A modern, responsive, full-stack campus dining platform featuring digital token generation, interactive food ordering, digital student wallet, live Kitchen Display POS, and real-time sales analytics.**

---

## 📌 Project Overview
**CampusBite** is designed to eliminate counter congestion, billing delays, and paper-token confusion across university dining facilities. The system digitizes the entire lifecycle of campus food ordering: students and faculty browse menus, place orders, and pay using a digital wallet; the kitchen receives real-time tickets on a digital Kanban display; and canteen administrators monitor live revenue, sales trends, and inventory levels.

---

## ✨ Key Features

### 1. Student & Faculty Ordering Portal (`/`)
- **Dynamic Menu Catalog**: Categorized into *Breakfast*, *Lunch*, *Snacks*, *Beverages*, and *Healthy Bowls*.
- **Multi-Criteria Search & Filtering**: Real-time keystroke search and dietary filters (*Pure Veg*, *Vegan*, *Non-Veg*).
- **Interactive Meal Tray (Cart Drawer)**: Seamless quantity increments, custom special cooking notes, and live subtotal calculations.
- **Digital Student Wallet**: Pre-loaded mock balances (₹450 / ₹1,200), instant top-ups (₹50, ₹100, ₹200, ₹500), and auto-deduction.
- **Unique Digital Token Slip**: Sequential token issuance (e.g. `TK-105`) with a printable thermal ticket and QR code simulation.

### 2. Kitchen Display System (KDS) & POS (`/kitchen`)
- **Real-Time Kanban Board**: 3 operational swimlanes — *Pending Orders*, *In Preparation*, and *Ready for Pickup*.
- **Auto-Sync Polling**: Background polling every 4 seconds ensures newly placed orders show up automatically without page reloads.
- **Quick Status Transitions**: One-click actions to advance orders through kitchen cooking stages.

### 3. Canteen Admin & Sales Analytics (`/admin`)
- **Real-Time KPI Scorecards**: Gross Revenue, Total Orders, Active Kitchen Queue, and Average Order Value (AOV).
- **Interactive Visual Charts**: Revenue breakdown by dish category and Top-5 selling dishes.
- **Inventory & Stock Management**: Live stock counters, low-stock warnings, and one-click stock toggles (*In Stock* / *Out of Stock*).
- **Audit CSV Export**: Downloadable spreadsheet report with timestamps, customer names, roles, and order totals.

### 4. Evaluator / Demo Role Switcher
- Built-in top-navigation switcher allowing teachers, evaluators, and viva examiners to instantly alternate between **Student (Aarav)**, **Faculty (Dr. Priya)**, **Kitchen Staff (Chef Ramesh)**, and **Admin (Vikram)**.

---

## 🛠️ Technologies & Tools Used
| Component | Technology | Description |
|---|---|---|
| **Backend Framework** | Python 3 + Flask 3.1 | Modular MVC application with Blueprint architecture |
| **Database Layer** | SQLite3 | Embedded ACID-compliant database with foreign keys & indexes |
| **Security & Auth** | Werkzeug Security | PBKDF2 password hashing and session-based RBAC decorators |
| **Frontend Styling** | Vanilla CSS3 | Custom glassmorphic design system, CSS variables, and micro-animations |
| **Typography** | Google Fonts | `Outfit` (display headings) & `Plus Jakarta Sans` (body interface) |
| **Frontend Logic** | Vanilla JavaScript (ES6+) | Modular architecture (`app.js`, `student.js`, `kitchen.js`, `admin.js`) |
| **Test Framework** | Pytest 9.0+ | Automated unit and integration test suite |

---

## 📁 Repository Structure
```
vityarti/
├── app.py                     # Main Flask application & route blueprint registry
├── auth.py                    # Authentication, session manager & RBAC decorators
├── conftest.py                # Pytest configuration & sys.path resolution
├── database.py                # SQLite schema setup, connection manager & seed data
├── models.py                  # Domain models (User, MenuItem, Order, OrderItem)
├── routes_admin.py            # Analytics KPIs, inventory management & CSV export
├── routes_menu.py             # Menu retrieval, search, filter & admin CRUD
├── routes_order.py            # Order placement, wallet debit, tokens & kitchen queue
├── statement.md               # Rubric Section 5.2 requirement document
├── project_report.md          # Comprehensive course submission report with UML/ER diagrams
├── README.md                  # Rubric Section 5.1 requirement document
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphic responsive design system
│   ├── js/
│   │   ├── admin.js           # Admin analytics charts & inventory CRUD
│   │   ├── app.js             # Cart engine, wallet recharge & toast alerts
│   │   ├── kitchen.js         # KDS live queue board & status transitions
│   │   └── student.js         # Menu filtering, live search & ordering
│   └── images/                # Menu photography assets (burger, dosa, coffee, salad)
├── templates/
│   ├── base.html              # Shared layout, navbar, persona switcher & modals
│   ├── index.html             # Student ordering portal
│   ├── kitchen.html           # Kitchen Display POS
│   ├── admin.html             # Admin analytics & inventory dashboard
│   └── orders.html            # Customer order history & token viewer
└── tests/
    ├── test_auth.py           # Unit tests for authentication & roles
    ├── test_menu.py           # Unit tests for menu queries & stock toggles
    └── test_orders.py         # Unit tests for order workflow & wallet deduction
```

---

## 🚀 Steps to Install & Run Locally

### Prerequisites
- Python 3.8+ (Anaconda Python or standard Python 3)
- Modern web browser (Chrome, Safari, Edge, Firefox)

### 1. Clone or Open the Repository
```bash
cd /Users/saishreyeshthota/Desktop/vityarti
```

### 2. Install Dependencies (if not already installed)
```bash
pip install flask pytest werkzeug
```

### 3. Run the Application
```bash
python app.py
```
*Note: The SQLite database (`canteen.db`) and realistic seed data (users, menu items, active orders) are automatically created on initial launch!*

### 4. Access the Portals
Open your web browser and navigate to:
- **Student Ordering Portal**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Kitchen POS Display**: [http://127.0.0.1:5000/kitchen](http://127.0.0.1:5000/kitchen)
- **Admin & Analytics**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
- **My Orders**: [http://127.0.0.1:5000/my-orders](http://127.0.0.1:5000/my-orders)

---

## 🧪 Instructions for Testing

Run the automated test suite with `pytest`:
```bash
pytest tests/ -v
```

Expected output:
```
============================== 12 passed in 0.73s ==============================
```

### Test Coverage Highlights:
1. `test_auth.py`: Validates user authentication, credential rejection, and dynamic role switching.
2. `test_menu.py`: Validates category filtering, vegan dietary filtering, search queries, and stock availability toggles.
3. `test_orders.py`: Validates order placement, token creation, wallet balance deductions, insufficient balance rejections, and the full kitchen status lifecycle (`pending` $\rightarrow$ `preparing` $\rightarrow$ `ready` $\rightarrow$ `completed`).

---

## 👤 Default Demo Accounts
All pre-seeded accounts share the password: `password123`

| Role | Username / Email | Full Name | Starting Wallet |
|---|---|---|---|
| **Student** | `student@campus.edu` | Aarav Sharma | ₹450.00 |
| **Faculty** | `faculty@campus.edu` | Dr. Priya Raman | ₹1,200.00 |
| **Kitchen Staff** | `staff@canteen.edu` | Chef Ramesh | — |
| **Admin** | `admin@campus.edu` | Vikram Malhotra | — |

*(Tip: You can also switch roles instantly using the top-bar Role Selector without typing passwords).*
