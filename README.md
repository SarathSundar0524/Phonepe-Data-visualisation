# Phonepe-Data-visualisation
 Interactive PhonePe Pulse Analytics Dashboard using Streamlit, Plotly &amp; Python |  State-Wise Transactions, Users, Insurance | 12 CSV Data Engineered into Master Dataset | Tabbed Maps + 5 Business Insights Visualization
🖼️ Project Overview
🧩 Project Structure
📦 phonepe-pulse-analytics
 ┣ 📂 data/
 ┣ 📂 assets/
 ┣ 📄 app.py
 ┣ 📄 README.md
 ┣ 📄 requirements.txt
 ┣ 📄 LICENSE
 ┣ 📄 project_structure.md

This project is a fully interactive analytics dashboard built using Streamlit, Plotly, Pandas, and GeoJSON maps.
It analyzes PhonePe Pulse (India’s digital payment dataset) and provides rich insights such as:
State-wise Transactions
👥 User Metrics
🛡️ Insurance Metrics
🗺️ District & Pincode–level maps
📈 5 Business Case Studies with custom insights
🗂️ 12 CSV datasets merged into one unified master dataset
The application features:
✔ Master India Map (with all 12 datasets processed & merged)
✔ Separate tabs for Transaction | User | Insurance
✔ 5 dedicated Business Scenarios dashboards
✔ Clean UI with dynamic tooltips for each state
✔ Fully production-ready for deployment

🚀 Features
1. Master India Map (Combined View)
Displays all key metrics per state:
                                  Total Transaction Amount
                                  Total Transaction Count
                                  Total Registered Users
                                  Total App Opens
                                  Total Insurance Amount
                                  Total Insurance Count
                                  District + Pincode Highlights
                                  Aggregated + Map + Top Datasets Combined
                                  Hover on any state → complete stats appear instantly.

2. Category Tabs
💵 Transactions:
                                  Aggregated Transactions
                                  Map Transactions
                                  Top District Transactions
                                  Top Pincode Transactions
👤 Users
                                  Aggregated Users
                                  Map Users
                                  Top District Users
                                  Top Pincode Users
🛡️Insurance
                                  Aggregated Insurance
                                  Map Insurance
                                  Top District Insurance
                                  Top Pincode Insurance

3. Business Case Studies (5 scenarios)

These appear in a dropdown, each opening a dedicated insights page:

1️. Top 10 States by Transaction Value

2. Yearly Transaction Growth Trend
3️. Insurance Penetration by State (%)
4️. User Engagement by Mobile Brand
5️. Top 10 Mobile Brands by Transaction Count
Each scenario uses interactive Plotly charts.
Dataset Description (12 CSVs)
Type	Files
Aggregated	Avg_trans.csv, Avg_user.csv, Avg_Insurance.csv
Map Level	Map_trans.csv, Map_user.csv, Map_Insurance.csv
Top Level	Top_Transaction_District.csv, Top_Transaction_Pincode.csv
	Top_user_District.csv, Top_user_Pincode.csv
	Top_insurance_District.csv, Top_insurance_Pincode.csv

All datasets are normalized and state names mapped using a custom standardization dictionary.

🏗️ Tech Stack
Category	Tools
Language	Python
Frontend	Streamlit
Visualization	Plotly
Backend	Pandas, GeoJSON
Deployment	Streamlit Cloud / GitHub Pages
Version Control	Git, GitHub
📦 Installation
1. Clone the Repository
git clone https://github.com/<your-username>/phonepe-pulse-analytics.git
cd phonepe-pulse-analytics

2. Install Dependencies
pip install -r requirements.txt

3. Run the Application
streamlit run app.py

Deployment Guide (Streamlit Cloud)
Push project → GitHub
Go to → https://share.streamlit.io
Connect repository
Select app.py
Deploy → Done 🎉
