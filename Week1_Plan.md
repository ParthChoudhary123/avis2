# Week 1: Foundational Setup, Database Design & User Security

This document outlines the planning, design choices, and implementation details for the Week 1 milestones of the Avis AI project.

---

## 1. Project Objectives
The main goal of Week 1 was to establish a secure, multi-role workspace for Store Managers and Vendors (Suppliers), ensuring complete data isolation and a clean database design.

---

## 2. Implementation Milestones

### Sandbox & Environment Setup
- Isolated all Python dependencies using a virtual environment (`venv`) to prevent version conflicts.
- Listed all required packages (Django, Pandas, Scikit-Learn) inside the `requirements.txt` file.
- Created a `.gitignore` file to ensure local environment files (`.env`) and database logs are kept out of GitHub.

### Relational Database Design
- Designed the core database models: `User`, `Product`, `Stock`, `Vendor`, and `Order`.
- Connected the models using standard foreign keys to maintain referential integrity (e.g. Products link to Stock levels, and Orders link to Vendors).

### Custom User Authentication
- Created a custom `User` model to replace Django's default.
- Added specific role flags (`is_manager`, `is_vendor`) to distinguish user accounts.
- Set up a dynamic registration form: selecting the "Vendor" role dynamically displays fields for Business Name, City, and Address, while selecting "Store Manager" keeps the form clean.

### Access Control & Routing
- Mapped all core URLs: `/login/`, `/register/`, and `/logout/`.
- Wrote custom Python decorators (`@manager_required` and `@vendor_required`) to prevent users from accessing unauthorized pages.
- Configured CSRF token checks on all forms to protect against Cross-Site Request Forgery.

---

## 3. Design Decisions & Rationale

- **Why a Custom User Model?**  
  Django's default user model only supports basic fields (username, email, password). Since Avis AI needs to route users to different dashboards and store logistics coordinates for suppliers, a custom model allowed us to attach these attributes directly to the user profile.
  
- **Why Custom Decorators?**  
  Writing permission decorators follows the DRY (Don't Repeat Yourself) principle. Instead of copying permission check blocks into every controller file, we can apply the decorator to any view that needs protection.

---

## 4. Verification & Testing

- **Route Protection**: If an unauthenticated user tries to visit a manager's URL directly, the system blocks the request and redirects them to log in.
- **Form Validation**: Registration fields adapt dynamically in the front-end, validating inputs before database writes.
- **Automated Tests**: Developed a standard testing suite (`tests.py`) to confirm registration logic, permission blocks, and routing isolation.
