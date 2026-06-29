# AVIS: AI-Assisted Smart Vendor & Automated Inventory Management System

AVIS is a modern retail inventory tracking and supply chain planning web application.

## Key Features
- **Predictive Sales Forecasting**: Linear Regression model (scikit-learn + pandas) to project next month's sales and set Smart Reorder Points.
- **Logistics Weather Radar**: Connects to the OpenWeatherMap API to display logistics delay warnings on shipping lines.
- **Cryptographic Audit Ledger**: An immutable, SHA-256 block-linked transaction ledger recording order finalization events.
- **Glassmorphic Dashboards**: Responsive visual panel layouts for Store Managers and Suppliers.

## Setup & Execution

### 1. Active Workspace
For the best experience in Antigravity, open the project directory in your editor workspace:
`C:\Users\ASUS\.gemini\antigravity\scratch\avis`

### 2. Launch Local Server
Activate the virtual environment and run the Django server:
```powershell
.\venv\Scripts\activate
python manage.py runserver
```
Visit the control center at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### 3. Run Automated Tests
Execute the logic suite to test modules and fallback states:
```powershell
python manage.py test
```

## Link to GitHub
To push this local repository to your remote GitHub account:
1. Create a new, blank repository on [GitHub](https://github.com/new) (do not add a README, license, or gitignore).
2. Run the following commands in your shell inside the project folder:
   ```powershell
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```
