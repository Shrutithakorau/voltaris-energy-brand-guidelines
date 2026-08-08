# Voltaris Energy — Brand Guidelines & Lead Manager

Brand system documentation and lead capture app derived from [voltarisenergy.com.au](https://www.voltarisenergy.com.au).

## Lead Manager (with SQLite database)

Leads are stored in a local **SQLite** database via a small Python API.

### Start (Windows)

1. Double-click `start-leads.bat`  
   or run: `py -3 server/app.py`
2. Open **http://127.0.0.1:8787/leads.html**

### Database

- File: `data/leads.db`
- Table: `leads` (customer name, mobile, email, address, product type, NMI, phase, created_at)
- API:
  - `GET /api/leads`
  - `POST /api/leads`
  - `DELETE /api/leads/:id`
  - `GET /api/health`

### Note on GitHub Pages

GitHub Pages is static only. The live Pages copy of `leads.html` needs the local server running to save/load from the database. Use `http://127.0.0.1:8787/leads.html` for full database functionality.

## Brand guidelines

**Live HTML guidelines:** https://shrutithakorau.github.io/voltaris-energy-brand-guidelines/

**Website feedback:** https://shrutithakorau.github.io/voltaris-energy-brand-guidelines/website-feedback.html

## Files

| File | Description |
| --- | --- |
| `leads.html` | Lead form + dashboard UI |
| `server/app.py` | SQLite API + static server |
| `data/leads.db` | Database file (created on first run) |
| `start-leads.bat` | One-click server start |
| `Voltaris-Energy-Brand-Guidelines.html` | Visual brand guidelines |
| `website-feedback.html` | Website review notes |
