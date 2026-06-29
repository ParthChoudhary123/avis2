# Software Requirements Specification (SRS) - AVIS

## 1. Introduction
AVIS (AI-Assisted Smart Vendor & Automated Inventory Management System) is an intelligent retail inventory and supply chain tracking system designed for small-to-medium retail operations. It combines traditional inventory tracking (CRUD), API-driven weather forecasts, machine learning sales predictions, and a tamper-proof cryptographic ledger for order verification.

## 2. System Architecture
The application uses a monolithic MVC architecture implemented via Django:
- **Backend:** Python / Django (utilizing Django ORM, pandas, scikit-learn, hashlib).
- **Frontend:** Django Templates + Bootstrap 5 + custom CSS for a premium glassmorphic visual aesthetic.
- **Database:** PostgreSQL (with SQLite fallback for local developer setups).
- **External Integration:** OpenWeatherMap API for supply chain logistics alerts.

## 3. Explicit System Constraints
1. **Role-Based Isolation:** Users are categorized into two roles:
   - **Store Managers:** Can manage products, view stock, check smart reorder recommendations, view weather logistics warnings, and review the order verification chain.
   - **Vendors:** Can only view orders assigned to them, confirm/fulfill orders, and update their own profiles.
2. **Cryptographic Integrity:** Once a Purchase Order (PO) is finalized, it must write a block into an audit log chain using SHA-256 cryptographic hashing. Any modification to the data must invalidate the chain verification.
3. **Logistics Delay Logic:** If a vendor's city has active alerts or forecasts for heavy rain (>10mm/h), snow, or thunderstorms, the system must trigger visual badges on the store manager dashboard alerting them to potential shipping delays.
4. **Predictive Analytics Performance:** The Linear Regression sales forecasting model must run asynchronously or be cached to avoid blocking the main thread during request-response cycles.

## 4. Relational Database Schema Design
The normalized relational database schema consists of:
- **Custom User Model (`User`):** Stores credentials, role (`manager` or `vendor`), and profile info.
- **Product (`Product`):**
  - `id` (PK)
  - `sku` (Unique string)
  - `name` (String)
  - `description` (Text)
  - `price` (Decimal)
  - `created_at` (Datetime)
- **Stock (`Stock`):**
  - `id` (PK)
  - `product` (One-to-One with Product)
  - `current_quantity` (Integer)
  - `min_threshold` (Integer) - baseline safety stock.
- **Vendor (`Vendor`):**
  - `id` (PK)
  - `user` (One-to-One with custom User)
  - `name` (String)
  - `email` (String)
  - `city` (String - for weather checks)
  - `address` (Text)
- **Order (`Order`):**
  - `id` (PK)
  - `product` (FK to Product)
  - `vendor` (FK to Vendor)
  - `quantity` (Integer)
  - `status` (String: Pending, Shipped, Delivered)
  - `created_at` (Datetime)
  - `updated_at` (Datetime)

## 5. Security Protocols
- CSRF token verification on all mutating requests.
- Argon2 or PBKDF2 hashing for passwords (built into Django).
- Secret variables stored in `.env`.
- Strict Django view permissions using role validation mixins or decorators.
