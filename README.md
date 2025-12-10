# PhonePe Pulse Data Visualization – Full Stack End-to-End Project

This project is an end-to-end analytical dashboard built using Python, Streamlit, PostgreSQL, and Plotly.  
It visualizes India’s digital payment ecosystem using real PhonePe Pulse data across multiple dimensions:

- Aggregated Transactions  
- Aggregated User Metrics  
- Aggregated Insurance  
- Map-Level Transactions, Users, Insurance  
- Top District & Pincode Insights  

All data is extracted from the official PhonePe Pulse GitHub repository, transformed into 12 CSVs, loaded into PostgreSQL, and visualized using Streamlit with an interactive India map.

---

## Project Pipeline

1. **Data Extraction**  
   - Extracted raw JSON files from PhonePe Pulse Github repository.
   - Parsed and combined into 12 cleaned CSV files.

2. **Data Transformation**  
   - Normalized column names  
   - Standardized state names (mapping applied)  
   - Validated district & pincode level data  
   - Created master aggregated datasets

3. **Database Creation**  
   - Designed a relational PostgreSQL database  
   - Created 12 tables  
   - Loaded cleaned CSV data using SQLAlchemy and psycopg2  

4. **Business Scenario Development (4 Key Insights)**  
   - Top Transaction States  
   - Yearly Transaction Growth  
   - Insurance Penetration  
   - User Engagement by Device Brand  

5. **Streamlit Dashboard**  
   - Home page containing a unified India map  
   - Displays all transaction, user, and insurance metrics when hovering over a state  
   - A dropdown menu to select any of the four business scenarios  
   - Each scenario loads its own dedicated Plotly analytics view

---

## Features

### 1. Home Page: Master India Map
Displays all metrics combined (from all 12 CSVs).  
Hovering over any state reveals:

- Total transaction amount  
- Total transaction count  
- Total users  
- Total app opens  
- Insurance premiums  
- Insurance count  
- Top districts  
- Top pincodes  

Everything is automatically mapped and normalized.

---

## Business Scenarios (Dropdown)

### Scenario 1 – Top Transaction States
<img width="1422" height="520" alt="Screenshot 2025-11-15 161324" src="https://github.com/user-attachments/assets/774611fe-4811-4847-bcf3-a8d44a5856f1" />


### Scenario 2 – Yearly Transaction Growth
![](screenshots/yearly_growth.png)

### Scenario 3 – Insurance Penetration by State
![](screenshots/insurance_penetration.png)

### Scenario 4 – Top Mobile Brands by User Count
![](screenshots/top_brands.png)

---

## Tech Stack

### Backend
- Python  
- PostgreSQL  
- SQLAlchemy  
- psycopg2  

### Frontend
- Streamlit  
- Plotly Express  
- Plotly Graph Objects  

### Data Source
- Official PhonePe Pulse GitHub Repository  

---

## Installation

### Clone the repository
```bash
git clone https://github.com/your-username/phonepe-pulse-dashboard.git
cd phonepe-pulse-dashboard


Deployment Guide (Streamlit Cloud)
Push project → GitHub
Go to → https://share.streamlit.io
Connect repository
Select app.py
Deploy → Done 🎉
