# Redesign & Optimization Plan: The Katana Layout

This document outlines the architectural specifications, frontend design patterns, and database optimizations planned for the Week 4 and Week 5 milestones of the Avis AI platform.

---

## 1. UI & UX Architecture (The "Katana" Layout)

### Fixed Sidebar Navigation
- Replace the standard top navigation bar with a collapsible vertical sidebar on the left side of the dashboard.
- Main menu items:
  - **Dashboard**: Core operational status feed.
  - **Inventory**: Product lists and stock levels.
  - **Orders**: Purchase requests and fulfillment logs.
  - **Vendors**: Supplier profile registry.
  - **Settings**: System configurations.

### Card-Based Metrics Grid
- Wrap key indicators in responsive Bootstrap cards to segregate information blocks:
  - Active weather warning counts.
  - Low stock warnings.
  - Pending orders needing verification.

### Status Indicators
- Enforce visual color-coding using Bootstrap badges:
  - **Low Stock Alerts**: Warning (Yellow).
  - **Pending Orders**: Secondary (Grey).
  - **Shipped Orders**: Info (Blue).
  - **Delivered / Fulfilled**: Success (Green).

---

## 2. Frontend & Styling Specifications

- **Responsive Tables**: Wrap all product inventory lists and vendor catalogs in Bootstrap's `.table-responsive` classes to ensure they scale on tablets and mobile screens.
- **Typography & Clean UI**: Enforce a modern sans-serif typeface (such as Inter or Roboto) with consistent line-heights and padding to maintain a clean, enterprise data dashboard feel.
- **Hero Overlays**: Implement dark-themed image overlays on the landing pages to guarantee high contrast for white header typography.

---

## 3. Backend & Database Optimization

### Query Performance (MVT Optimization)
- Optimize Django view controllers to minimize database connection loops.
- Use `select_related` for single-value foreign key relations (e.g., matching a Stock record to its parent Product).
- Use `prefetch_related` for multi-value relations (e.g., listing all Orders associated with a Vendor) to eliminate the N+1 query problem.

### Asynchronous Data Binding (AJAX/Fetch API)
- Shift critical dashboard components away from full page reloads:
  - **Logistics Weather Alerts**: Query the OpenWeatherMap endpoint asynchronously in the background.
  - **Reorder Alerts**: Periodically check inventory thresholds and update dashboard badges via the Fetch API.

### Security Foundation
- Secure database connections and API keys (such as OpenWeatherMap tokens) inside environment variables (`.env`).
- Restrict all view controllers using Django's authentication middleware and custom role decorators to separate Store Manager capabilities from Vendor access.

---

## 4. Implementation Timeline

### Week 4: Template Refactoring & Sidebar Layout
- Implement the fixed sidebar CSS grid.
- Move dashboard components, inventory sheets, and order logs into the unified dashboard container.
- Align Bootstrap styles across login and register views to match the new template schema.

### Week 5: Asynchronous Data Bindings & Cleanup
- Write AJAX endpoints in Django views to return JSON statuses.
- Integrate frontend Javascript Fetch routines to update metrics panels without page refreshes.
- Minify CSS and static script packages to improve overall page loading performance.
