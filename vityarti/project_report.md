# PROJECT REPORT
## CAMPUSBITE: SMART CANTEEN MANAGEMENT SYSTEM
### Advanced Full-Stack Campus Food Ordering, Kitchen POS & Sales Analytics System

---

## 1. Project Cover Page
- **Project Title**: CampusBite — Smart Canteen Management System
- **Subject / Portal**: Vityarthi Learning Destination Course Project
- **Domain**: Web Application Development / Software Engineering
- **Architecture**: Modular Python Flask RESTful API + SQLite3 + Vanilla ES6/CSS3 Client
- **Author**: Student Submission
- **Academic Year**: 2026

---

## 2. Introduction
University campuses cater to thousands of students, faculty, and administrative staff daily. The campus canteen is a central hub of activity, particularly during standard recess and lunch hours. However, traditional operational workflows rely heavily on manual ordering, cash transactions, handwritten paper tokens, and verbal callouts. These legacy practices cause counter congestion, billing discrepancies, order errors, and prolonged wait times.

**CampusBite** is an advanced, full-stack web application developed to eliminate counter bottlenecks and introduce an efficient, transparent, and user-centric dining experience. By integrating digital menus, a cashless student wallet, automated token generation, a live kitchen production board (KDS), and real-time administrative analytics, CampusBite establishes a reliable digital ecosystem for modern academic institutions.

---

## 3. Problem Statement & Objectives

### 3.1 Problem Statement
During peak campus intervals, students and faculty experience:
1. **Prolonged Waiting Times**: Standing in consecutive queues for billing, payment, and meal collection.
2. **Order Errors & Mismanagement**: Paper tokens being lost or miscommunicated between billing clerks and cooks.
3. **Lack of Dietary Transparency**: Inability to quickly inspect ingredients, allergens, or caloric counts.
4. **Suboptimal Kitchen & Inventory Operations**: Kitchen staff lack visibility into incoming order spikes, resulting in either food shortages or end-of-day wastage.

### 3.2 Objectives
- **Automate Ordering & Billing**: Provide students and faculty with self-service digital ordering and instant checkout.
- **Enable Cashless Transactions**: Integrate an internal digital wallet system with instant mock top-ups and automatic deductions.
- **Streamline Kitchen Production**: Equip canteen kitchen staff with a real-time Kitchen Display System (KDS) displaying pending, cooking, and ready states.
- **Provide Actionable Business Intelligence**: Empower canteen managers with live KPI dashboards, category revenue breakdowns, and audit-ready CSV exports.
- **Deliver High Usability**: Ensure responsive, glassmorphic UI design accessible across laptops, tablets, and smartphones.

---

## 4. Scope & Requirements

### 4.1 Functional Requirements (Section 2.1)
The application is structured into four core functional modules:

1. **User Management & Authentication Module**:
   - Role-Based Access Control (RBAC) supporting four distinct roles: *Student*, *Faculty*, *Kitchen Staff*, and *System Admin*.
   - Secure PBKDF2 password hashing and session management.
   - Built-in Evaluator Role Switcher enabling instantaneous persona changes for grading demonstrations.
   - User wallet balance ledger recording credits, debits, and timestamps.

2. **Interactive Menu & Customer Ordering Module**:
   - Menu browsing segmented by categories (*Breakfast*, *Lunch*, *Snacks*, *Beverages*, *Healthy*).
   - Instant text search across item names and descriptions.
   - Dietary filtering for *Pure Veg*, *Vegan*, and *Non-Veg*.
   - Interactive slide-out cart drawer supporting quantity updates and chef notes.
   - Digital token generator generating sequential identifiers (e.g. `TK-105`) and printable thermal slips with simulated QR codes.

3. **Kitchen Order POS & Production Module (KDS)**:
   - 3-column Kanban interface categorizing tickets into *Pending*, *In Preparation*, and *Ready for Pickup*.
   - Automated 4-second polling to ingest incoming orders asynchronously without page reload.
   - One-click order state transitions (*Start Preparation* $\rightarrow$ *Mark Ready* $\rightarrow$ *Complete*).

4. **Admin Dashboard & Inventory Analytics Module**:
   - Real-time KPI cards: Gross Revenue, Total Orders, Active Queue, Average Order Value (AOV).
   - Category sales breakdown and volume ranking for top-selling items.
   - Full CRUD operations for menu items (create, read, update, delete).
   - Instant availability/stock toggles.
   - One-click CSV audit report generation.

### 4.2 Non-Functional Requirements (Section 2.2)
1. **Performance**: Sub-50ms API query response times for SQLite operations; zero heavy external client bundles ensuring instant page loads.
2. **Security**: Defense against SQL injection via parameterized queries, session cookies, and PBKDF2 password hashing.
3. **Usability**: Adheres to modern web aesthetics featuring dark-mode glassmorphism, responsive grid layouts, and high contrast ratios.
4. **Reliability & Scalability**: ACID-compliant SQLite transactions guarantee atomic wallet deductions and order creation.
5. **Maintainability & Modularity**: Decoupled MVC-style code separation across 8+ specialized Python modules with docstrings.
6. **Error Handling**: Graceful fallback handling with consistent JSON error responses and client-side toast notifications.

---

## 5. Design Artefacts & UML Diagrams

### 5.1 System Architecture Diagram
```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer (Browser)"]
        UI_Student["Student Menu & Wallet UI"]
        UI_KDS["Kitchen Display (KDS)"]
        UI_Admin["Admin Dashboard & Analytics"]
    end

    subgraph ControllerLayer["Flask Application Layer (app.py)"]
        AuthBP["Auth Blueprint (auth.py)"]
        MenuBP["Menu Blueprint (routes_menu.py)"]
        OrderBP["Order Blueprint (routes_order.py)"]
        AdminBP["Admin Blueprint (routes_admin.py)"]
    end

    subgraph ServiceLayer["Domain & Service Models"]
        UserM["User & Role Model"]
        MenuM["MenuItem Model"]
        OrderM["Order & Item Model"]
    end

    subgraph StorageLayer["Data Storage Layer (SQLite3)"]
        DB[(canteen.db)]
        UsersT[users]
        MenuT[menu_items]
        OrdersT[orders]
        ItemsT[order_items]
        WalletT[wallet_transactions]
    end

    ClientLayer -->|HTTP/REST JSON| ControllerLayer
    ControllerLayer --> ServiceLayer
    ServiceLayer --> StorageLayer
    DB --- UsersT
    DB --- MenuT
    DB --- OrdersT
    DB --- ItemsT
    DB --- WalletT
```

---

### 5.2 Process Flow / Ordering Workflow Diagram
```mermaid
sequenceDiagram
    autonumber
    actor Customer as Student / Faculty
    participant UI as Web Frontend
    participant Server as Flask API Server
    participant DB as SQLite Database
    participant Kitchen as Kitchen POS

    Customer->>UI: Browse Menu & Add Dishes to Cart
    Customer->>UI: Enter Cooking Instructions & Checkout
    UI->>Server: POST /api/orders {items, wallet_payment}
    Server->>DB: Check Item Stock & User Wallet Balance
    alt Insufficient Balance
        Server-->>UI: 400 Bad Request (Insufficient Balance)
        UI-->>Customer: Display "Recharge Wallet" Alert
    else Balance & Stock Valid
        Server->>DB: Deduct Wallet & Decrement Stock
        Server->>DB: Create Order & Generate Token (e.g. TK-105)
        Server-->>UI: 201 Created {token_number, order_details}
        UI-->>Customer: Render Printable Digital Token Slip
        Note over Kitchen: Live Poll detects new order
        Kitchen->>Server: GET /api/orders/kitchen-queue
        Server-->>Kitchen: Display New Ticket under "Pending"
        Kitchen->>Server: PATCH /api/orders/{id}/status (Preparing -> Ready)
        Server->>DB: Update order_status = 'ready'
        Customer->>Kitchen: Presents Token Slip at Counter & Collects Meal
        Kitchen->>Server: PATCH /api/orders/{id}/status (Completed)
    end
```

---

### 5.3 UML Use Case Diagram
```mermaid
flowchart LR
    Student((Student / Faculty))
    Chef((Kitchen Chef))
    Admin((Canteen Admin))

    subgraph SystemBoundary["CampusBite System Boundary"]
        UC1["Browse Menu & Dietary Filters"]
        UC2["Recharge Digital Wallet"]
        UC3["Place Order & Receive Token"]
        UC4["Track Active Order Status"]
        UC5["View Live Kitchen Queue"]
        UC6["Update Cooking Stage (Pending -> Ready)"]
        UC7["Manage Menu Items & Prices (CRUD)"]
        UC8["Toggle Stock Availability"]
        UC9["View Financial Sales Analytics"]
        UC10["Export Order Audit CSV"]
    end

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4

    Chef --> UC5
    Chef --> UC6
    Chef --> UC8

    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
```

---

### 5.4 Database Storage Design (ER Diagram)
```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ WALLET_TRANSACTIONS : owns
    ORDERS ||--|{ ORDER_ITEMS : contains
    MENU_ITEMS ||--o{ ORDER_ITEMS : references

    USERS {
        int id PK
        string username
        string email
        string password_hash
        string full_name
        string role
        float wallet_balance
        string roll_no
        datetime created_at
    }

    MENU_ITEMS {
        int id PK
        string name
        string category
        string description
        float price
        int is_available
        int stock_quantity
        string dietary_type
        string image_url
        int prep_time_minutes
        int calories
        float rating
        datetime created_at
    }

    ORDERS {
        int id PK
        string order_number
        string token_number
        int user_id FK
        float total_amount
        float discount_amount
        float final_amount
        string payment_method
        string payment_status
        string order_status
        string special_instructions
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int item_id FK
        string item_name
        int quantity
        float unit_price
        float subtotal
    }

    WALLET_TRANSACTIONS {
        int id PK
        int user_id FK
        float amount
        string transaction_type
        string reference
        float balance_after
        datetime created_at
    }
```

---

## 6. Testing and Verification

An automated test suite was constructed using `pytest`, executing 12 unit tests verifying core system behavior:

| Test Case | Module | Description | Result |
|---|---|---|---|
| `test_login_success` | Auth | Valid credentials successfully log in student | **PASSED** |
| `test_login_invalid_password` | Auth | Incorrect password produces 401 Unauthorized | **PASSED** |
| `test_demo_role_switcher` | Auth | Persona toggle dynamically modifies session | **PASSED** |
| `test_get_menu_items` | Menu | Retrieval of 12+ pre-seeded canteen dishes | **PASSED** |
| `test_category_filter` | Menu | Filters catalog strictly by category | **PASSED** |
| `test_dietary_filter` | Menu | Filters dishes strictly by vegan/veg/non-veg tags | **PASSED** |
| `test_search_menu` | Menu | Text matching across dish titles & descriptions | **PASSED** |
| `test_toggle_stock_staff` | Menu | Staff toggles item between In-Stock & Out-of-Stock | **PASSED** |
| `test_place_order_success` | Orders | Creates order, generates token, debits wallet balance | **PASSED** |
| `test_insufficient_wallet_balance` | Orders | Rejects order exceeding current balance | **PASSED** |
| `test_order_status_lifecycle` | Orders | Verifies lifecycle: pending $\rightarrow$ preparing $\rightarrow$ ready $\rightarrow$ completed | **PASSED** |
| `test_wallet_topup` | Orders | Adds mock funds to digital student wallet | **PASSED** |

**Execution Result**: `12 passed in 0.73s` (100% pass rate).

---

## 7. Conclusion & Future Enhancements
The **CampusBite Smart Canteen Management System** successfully addresses the operational challenges of campus food ordering. It satisfies all functional and non-functional requirements outlined by the Vityarthi curriculum, featuring modular architecture, robust automated test suites, responsive glassmorphic interfaces, and comprehensive design documentation.

Future enhancements include:
1. Integration with physical campus RFID/NFC smart cards.
2. WebPush notifications when orders reach the *Ready for Pickup* counter stage.
3. Predictive AI forecasting to estimate demand based on exam schedules and historical trends.
