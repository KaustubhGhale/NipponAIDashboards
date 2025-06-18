# ERP Sales Dashboard using Dash & Oracle

---

A powerful, multi-page ERP analytics dashboard that connects to an Oracle database, allowing users to:

- Run SQL queries
- Visualize sales data
- Drill down from State → City → Customer → Item
- Export filtered results to Excel & PDF
- Deployable via Render or locally

---

## Features

- **Dynamic SQL Integration** using `main.py`
- **Interactive Dashboards** with filters and chart type selection
- **Multi-page layout**: Sales, Inventory, Payroll (Dash pages)
- **Export options**: Excel (.xlsx) and PDF (.pdf)
- **Render-compatible** with `render.yaml`
- Built using Plotly Dash & Flask

---

## Tech Stack

- Python
- Dash (multi-page)
- Plotly
- Flask (backend server)
- Oracle DB (data source)
- SQLAlchemy + oracledb (DB connection)
- Pandas
- Kaleido / OpenPyXL (for export)

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run SQL input script (manual entry)
python main.py

# 3. Launch the dashboard
python app.py
