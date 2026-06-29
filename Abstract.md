# Project Abstract: Avis AI
**Project Title:** Avis AI: An Intelligent Enterprise Decision-Support System Powered by Katana AI  
**Technologies Used:** Python, Django, PostgreSQL (with SQLite compatibility), Scikit-Learn, Pandas, hashlib, Bootstrap 5, HTML5

---

### Abstract
In the modern digital retail landscape, businesses face severe data fragmentation and the critical challenge of converting raw operational data into actionable, real-time logistics intelligence. This project introduces **Avis AI**, a robust, scalable, and intelligent enterprise decision-support and inventory coordination web application. Designed to bridge the gap between complex backend data processing and user-centric retail operations, Avis AI integrates the advanced predictive capabilities of the **Katana AI Engine** within a high-performance web architecture.

The core infrastructure of Avis AI is built using the **Django framework** powered by **Python**, ensuring secure, maintainable, and rapid backend logic execution. Data persistence, transactional integrity, and complex relational queries are managed via **PostgreSQL**, providing the enterprise-grade database foundation required to handle large-scale catalogs, stocks, and order tables. 

Avis AI incorporates three primary intelligent subsystems:
1. **Katana AI Predictive Engine**: Powered by **Scikit-Learn** and **Pandas**, this cognitive engine automates demand forecasting and seasonal consumption trends directly from historical sales logs. It calculates dynamic **Smart Reorder Points (ROP)** and initiates alerts when stock levels fall below projected thresholds. To eliminate latency, Katana AI runs its mathematical fitting routines asynchronously inside background threads, caching results to prevent main-thread freezing.
2. **Logistics Delay Radar**: An external weather API parsing engine that screens weather alerts (heavy rain, snow, storms) in supplier operating cities to immediately flag in-transit orders at risk of shipping delays.
3. **Cryptographic Order Audit Ledger**: A secure, block-linked transaction ledger using **SHA-256 hashes** to serialize purchase order histories sequentially. Any unauthorized modification to database transaction data immediately invalidates the ledger chain, enabling instant security breach detection.

On the frontend, Avis AI delivers a seamless, responsive, and premium user experience by leveraging **HTML5** and **Bootstrap 5** styled with a modern glassmorphic theme. The control center features real-time interactive dashboards that visualize AI-driven forecasts, weather alarms, and cryptographic audit states, rendering fluidly across mobile, tablet, and desktop viewports.

Ultimately, Avis AI demonstrates how modern web frameworks can be successfully paired with state-of-the-art predictive modeling and cryptographic auditing to deliver a secure, responsive, and highly intelligent business tool. By automating data interpretation and forecasting, the platform reduces decision-making latency, optimizes resource allocation, and provides retail organizations with a definitive competitive advantage.

**Keywords:** Artificial Intelligence, Django, Katana AI, Predictive Analytics, PostgreSQL, Cryptographic Audit Ledger, Responsive Web Design, Python.

---

### Key Components Breakdown

*   **Backend (Python & Django):** Handles the core business logic, role-based authentication (Store Manager vs. Vendor), decorator-enforced permissions, API routing, and the asynchronous thread scheduler for the Katana AI engine.
*   **Database (PostgreSQL / SQLite):** Safely persists user credentials, product profiles, real-time stock quantities, supplier directories, and historical transaction blocks.
*   **AI Engine (Katana AI / Scikit-Learn & Pandas):** Processes historical sales data via regression modeling to discover seasonal patterns, automate reordering triggers, and provide smart operational recommendations.
*   **Cryptographic Chain (hashlib):** Validates the sequential integrity of purchase order finalizations, creating a tamper-proof blockchain audit trail.
*   **Logistics Radar (requests & OpenWeatherMap):** Monitors atmospheric conditions of vendor locations, feeding logistics delay warnings directly into the manager's panel.
*   **Frontend (HTML5 & Bootstrap 5 CSS):** Displays complex AI projections, audit statuses, and weather badges in a premium, glassmorphic layout optimized for cross-platform responsiveness.
