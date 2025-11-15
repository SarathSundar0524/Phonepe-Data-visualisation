import os
from functools import lru_cache
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# -----------------------------
# USER CONFIG - update paths if needed
# -----------------------------
CSV_PATHS = {
    "agg_trans": r"C:\Users\USER\OneDrive\Desktop\Avg_trans.csv",
    "agg_user": r"C:\Users\USER\OneDrive\Desktop\Avg_user.csv",
    "agg_ins": r"C:\Users\USER\OneDrive\Desktop\Avg_Insurance.csv",
    "map_trans": r"C:\Users\USER\OneDrive\Desktop\Map_trans.csv",
    "map_user": r"C:\Users\USER\OneDrive\Desktop\Map_user.csv",
    "map_ins": r"C:\Users\USER\OneDrive\Desktop\Map_Insurance.csv",
    "top_tx_dist": r"C:\Users\USER\OneDrive\Desktop\Top_Transaction_District.csv",
    "top_tx_pin": r"C:\Users\USER\OneDrive\Desktop\Top_Transaction_Pincode.csv",
    "top_user_dist": r"C:\Users\USER\OneDrive\Desktop\Top_user_District.csv",
    "top_user_pin": r"C:\Users\USER\OneDrive\Desktop\Top_user_Pincode.csv",
    "top_ins_dist": r"C:\Users\USER\OneDrive\Desktop\Top_insurance_District.csv",
    "top_ins_pin": r"C:\Users\USER\OneDrive\Desktop\Top_insurance_Pincode.csv",
}

GEOJSON_URL = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="PhonePe Data Visualisation — Master Map + Scenarios", layout="wide")
st.title("📊 PhonePe Data Visualisation — Master Map ")

# -----------------------------
# Helpers: load, normalize, aggregate
# -----------------------------
@st.cache_data
def load_geojson(url: str):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def normalize_state_col(df, col='state'):
    """Normalize state names using the mapping you provided."""
    if col not in df.columns:
        return df
    s = df[col].astype(str).str.strip().str.lower()

    mapping = {
        'maharashtra': 'Maharashtra',
        'uttar-pradesh': 'Uttar Pradesh',
        'karnataka': 'Karnataka',
        'rajasthan': 'Rajasthan',
        'west-bengal': 'West Bengal',
        'tamil-nadu': 'Tamil Nadu',
        'bihar': 'Bihar',
        'madhya-pradesh': 'Madhya Pradesh',
        'telangana': 'Telangana',
        'andhra-pradesh': 'Andhra Pradesh',
        'kerala': 'Kerala',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'assam': 'Assam',
        'jharkhand': 'Jharkhand',
        'odisha': 'Odisha',
        'himachal-pradesh': 'Himachal Pradesh',
        'chandigarh': 'Chandigarh',
        'tripura': 'Tripura',
        'jammu-and-kashmir': 'Jammu & Kashmir',
        'jammu-&-kashmir': 'Jammu & Kashmir',
        'punjab': 'Punjab',
        'sikkim': 'Sikkim',
        'uttarakhand': 'Uttarakhand',
        'nagaland': 'Nagaland',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'arunachal-pradesh': 'Arunachal Pradesh',
        'manipur': 'Manipur',
        'dadra-and-nagar-haveli-and-daman-and-diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'delhi': 'Delhi',
        'andaman-and-nicobar-islands': 'Andaman & Nicobar',
        'andaman-&-nicobar-islands': 'Andaman & Nicobar',
        'ladakh': 'Ladakh',
        'puducherry': 'Puducherry',
        'goa': 'Goa',
        'chhattisgarh': 'Chhattisgarh',
        'lakshadweep': 'Lakshadweep'
    }

    # Normalize common separators
    s = s.str.replace('&', 'and', regex=False)
    s = s.str.replace('-', ' ', regex=False)
    s = s.str.replace('  ', ' ', regex=False).str.strip()

    normalized = []
    for val in s:
        if val in mapping:
            normalized.append(mapping[val])
        else:
            normalized.append(val.title())
    df[col] = normalized
    return df

@st.cache_data
def load_all_csvs(paths: dict):
    """Load all CSVs; return dict of dataframes. Missing CSV -> empty DataFrame."""
    dfs = {}
    for k, p in paths.items():
        if not os.path.exists(p):
            dfs[k] = pd.DataFrame()
            continue
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip().str.lower()
        if 'state' in df.columns:
            df = normalize_state_col(df, 'state')
        dfs[k] = df
    return dfs

def sum_if_present(df, candidates, newname):
    """If any of the candidate columns exists in df, group by state sum it and rename to newname."""
    col = next((c for c in candidates if c in df.columns), None)
    if col:
        s = df.groupby('state', as_index=False)[col].sum().rename(columns={col:newname})
        return s
    else:
        return pd.DataFrame(columns=['state', newname])

def aggregate_master_state(dfs, geo_states):
    """
    Aggregate each CSV to state-level metrics and merge into master_df.
    final master_df columns include:
    - transaction_amount, transaction_count, map_trans_amount, map_trans_count, dist_trans_amount, pin_trans_amount
    - total_users, map_users, map_app_opens, dist_user_count, pin_user_count
    - insurance_amount, insurance_count, map_ins_amount, map_ins_count, dist_ins_amount, pin_ins_amount
    - total_activity (sum of all numeric columns)
    """
    # TRANSACTIONS
    agg_trans = pd.DataFrame(columns=['state','transaction_amount','transaction_count'])
    if not dfs.get('agg_trans', pd.DataFrame()).empty:
        t = dfs['agg_trans']
        amt_col = 'transaction_amount' if 'transaction_amount' in t.columns else next((c for c in ['amount','total_amount'] if c in t.columns), None)
        cnt_col = 'transaction_count' if 'transaction_count' in t.columns else next((c for c in ['count','total_count'] if c in t.columns), None)
        agg = {}
        if amt_col: agg[amt_col] = 'sum'
        if cnt_col: agg[cnt_col] = 'sum'
        if agg:
            agg_trans = t.groupby('state', as_index=False).agg(agg)
            if amt_col and amt_col != 'transaction_amount': agg_trans = agg_trans.rename(columns={amt_col:'transaction_amount'})
            if cnt_col and cnt_col != 'transaction_count': agg_trans = agg_trans.rename(columns={cnt_col:'transaction_count'})

    # MAP TRANSACTIONS
    map_trans = pd.DataFrame(columns=['state','map_trans_amount','map_trans_count'])
    if not dfs.get('map_trans', pd.DataFrame()).empty:
        mt = dfs['map_trans']
        amt = next((c for c in ['amount','transaction_amount','p_amount'] if c in mt.columns), None)
        cnt = next((c for c in ['count','transaction_count','p_count'] if c in mt.columns), None)
        sums={}
        if amt: sums[amt]='sum'
        if cnt: sums[cnt]='sum'
        if sums:
            map_trans = mt.groupby('state', as_index=False).agg(sums)
            if amt and amt != 'map_trans_amount': map_trans = map_trans.rename(columns={amt:'map_trans_amount'})
            if cnt and cnt != 'map_trans_count': map_trans = map_trans.rename(columns={cnt:'map_trans_count'})

    # TOP TRANSACTIONS (district/pincode)
    top_tx_dist = sum_if_present(dfs.get('top_tx_dist', pd.DataFrame()), ['d_amount','d_amount '], 'dist_trans_amount')
    top_tx_pin = sum_if_present(dfs.get('top_tx_pin', pd.DataFrame()), ['p_amount','p_amount '], 'pin_trans_amount')

    # USERS
    agg_user = pd.DataFrame(columns=['state','total_users'])
    if not dfs.get('agg_user', pd.DataFrame()).empty:
        u = dfs['agg_user']
        user_col = next((c for c in ['brand_count','registered_users','registeredusers','total_users'] if c in u.columns), None)
        if user_col:
            agg_user = u.groupby('state', as_index=False)[user_col].sum().rename(columns={user_col:'total_users'})

    map_user = pd.DataFrame(columns=['state','map_users','map_app_opens'])
    if not dfs.get('map_user', pd.DataFrame()).empty:
        mu = dfs['map_user']
        reg = next((c for c in ['registered_users','registeredusers'] if c in mu.columns), None)
        app = next((c for c in ['app_opens','appopens'] if c in mu.columns), None)
        sums={}
        if reg: sums[reg]='sum'
        if app: sums[app]='sum'
        if sums:
            map_user = mu.groupby('state', as_index=False).agg(sums)
            if reg and reg != 'map_users': map_user = map_user.rename(columns={reg:'map_users'})
            if app and app != 'map_app_opens': map_user = map_user.rename(columns={app:'map_app_opens'})

    top_user_dist = sum_if_present(dfs.get('top_user_dist', pd.DataFrame()), ['registeredusers_d','registered_users','registeredusers'], 'dist_user_count')
    top_user_pin = sum_if_present(dfs.get('top_user_pin', pd.DataFrame()), ['registeredusers_p','registeredusers_p '], 'pin_user_count')

    # INSURANCE
    agg_ins = pd.DataFrame(columns=['state','insurance_amount','insurance_count'])
    if not dfs.get('agg_ins', pd.DataFrame()).empty:
        ins = dfs['agg_ins']
        ins_amt = next((c for c in ['insurance_amount','amount','total_amount'] if c in ins.columns), None)
        ins_cnt = next((c for c in ['insurance_count','count'] if c in ins.columns), None)
        sums={}
        if ins_amt: sums[ins_amt]='sum'
        if ins_cnt: sums[ins_cnt]='sum'
        if sums:
            agg_ins = ins.groupby('state', as_index=False).agg(sums)
            if ins_amt and ins_amt != 'insurance_amount': agg_ins = agg_ins.rename(columns={ins_amt:'insurance_amount'})
            if ins_cnt and ins_cnt != 'insurance_count': agg_ins = agg_ins.rename(columns={ins_cnt:'insurance_count'})

    map_ins = pd.DataFrame(columns=['state','map_ins_amount','map_ins_count'])
    if not dfs.get('map_ins', pd.DataFrame()).empty:
        mi = dfs['map_ins']
        amt = next((c for c in ['insurance_amount','amount','p_amount'] if c in mi.columns), None)
        cnt = next((c for c in ['insurance_count','count','p_count'] if c in mi.columns), None)
        sums={}
        if amt: sums[amt]='sum'
        if cnt: sums[cnt]='sum'
        if sums:
            map_ins = mi.groupby('state', as_index=False).agg(sums)
            if amt and amt != 'map_ins_amount': map_ins = map_ins.rename(columns={amt:'map_ins_amount'})
            if cnt and cnt != 'map_ins_count': map_ins = map_ins.rename(columns={cnt:'map_ins_count'})

    top_ins_dist = sum_if_present(dfs.get('top_ins_dist', pd.DataFrame()), ['d_amount','d_amount '], 'dist_ins_amount')
    top_ins_pin = sum_if_present(dfs.get('top_ins_pin', pd.DataFrame()), ['p_amount','p_amount '], 'pin_ins_amount')

    # Merge all pieces into master
    parts = [agg_trans, map_trans, top_tx_dist, top_tx_pin,
             agg_user, map_user, top_user_dist, top_user_pin,
             agg_ins, map_ins, top_ins_dist, top_ins_pin]
    master = None
    for p in parts:
        if master is None:
            master = p.copy()
        else:
            master = master.merge(p, on='state', how='outer')
    if master is None:
        master = pd.DataFrame({'state': list(geo_states)})
    # add missing states
    if 'state' in master.columns:
        missing = set(geo_states) - set(master['state'].unique())
        if missing:
            add = pd.DataFrame({'state': list(missing)})
            master = pd.concat([master, add], ignore_index=True, sort=False)
    # numeric conversions and fill
    for c in master.columns:
        if c != 'state':
            master[c] = pd.to_numeric(master[c], errors='coerce').fillna(0)
    # compute total_activity
    numeric_cols = [c for c in master.columns if c != 'state']
    master['total_activity'] = master[numeric_cols].sum(axis=1)
    master = master.sort_values('state').reset_index(drop=True)
    return master

# -----------------------------
# Load CSVs and build master
# -----------------------------
dfs = load_all_csvs(CSV_PATHS)
geojson = load_geojson(GEOJSON_URL)
geo_states = [feat["properties"]["ST_NM"] for feat in geojson["features"]]
master_df = aggregate_master_state(dfs, geo_states)

# -----------------------------
# Sidebar: scenarios (Key1..Key4)
# -----------------------------
st.sidebar.header("Business Insights (Key1..Key5)")
page = st.sidebar.radio("Choose page", [
    "Home (Transactions / Users / Insurance)",
    "Scenario 1: Top States by Transactions (Key1)",
    "Scenario 2: Yearly Transaction Growth (Key2)",
    "Scenario 3: Insurance Penetration (Key3)",
    "Scenario 4: User Engagement by Brand (Key4)"
])

# HOME

if page == "Home (Transactions / Users / Insurance)":
    st.header("Home — Category Views (Transactions / Users / Insurance)")
    #st.markdown("Select a category. The India map is colored by the main metric for that category. Hover a state to see all related metrics for that category.")
    category = st.selectbox("Category", options=["Transactions", "Users", "Insurance"])

    if category == "Transactions":
        selected_metric = "transaction_amount"
        hover_cols = [
            'state', 'transaction_amount', 'transaction_count',
            'map_trans_amount', 'map_trans_count',
            'dist_trans_amount', 'pin_trans_amount'
        ]
        title = "Transactions — transaction_amount"
    elif category == "Users":
        selected_metric = "total_users"
        hover_cols = [
            'state', 'total_users',
            'map_users', 'map_app_opens',
            'dist_user_count', 'pin_user_count'
        ]
        title = "Users — total_users"
    else:  # Insurance
        selected_metric = "insurance_amount"
        hover_cols = [
            'state', 'insurance_amount', 'insurance_count',
            'map_ins_amount', 'map_ins_count',
            'dist_ins_amount', 'pin_ins_amount'
        ]
        title = "Insurance — insurance_amount"

    # Only keep hover columns that exist in master_df
    hover_cols = [c for c in hover_cols if c in master_df.columns]

    # Warn if selected_metric missing; fallback to total_activity
    if selected_metric not in master_df.columns:
        st.warning(f"Main metric '{selected_metric}' not found. Coloring by total_activity instead.")
        color_metric = 'total_activity'
    else:
        color_metric = selected_metric

    # build and display choropleth
    fig = px.choropleth(
        master_df,
        geojson=geojson,
        locations='state',
        featureidkey="properties.ST_NM",
        color=color_metric,
        hover_data=hover_cols,
        color_continuous_scale='Viridis',
        title=f"India — {title}"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0}, height=720)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### Top 5 states by {color_metric}")
    if color_metric in master_df.columns:
        st.dataframe(master_df[['state', color_metric]].sort_values(color_metric, ascending=False).head(5).style.format({color_metric:'{:,.0f}'}), height=220)
    else:
        st.info("No metric available to show top states.")

# -----------------------------
# Scenario 1 (Key1)
# -----------------------------
elif page == "Scenario 1: Top States by Transactions (Key1)":
    st.header("Scenario 1 — Top 10 States by Transaction Value (Key1)")
    if not dfs.get('agg_trans', pd.DataFrame()).empty:
        t = dfs['agg_trans']
        amt_col = 'transaction_amount' if 'transaction_amount' in t.columns else next((c for c in ['amount','total_amount'] if c in t.columns), None)
        if amt_col:
            top_states = t.groupby('state', as_index=False)[amt_col].sum().rename(columns={amt_col:'total_amount'}).sort_values('total_amount', ascending=False).head(10)
            fig = px.bar(top_states, x='state', y='total_amount', text_auto=True, title='Top 10 States by Transaction Amount')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top_states.style.format({'total_amount':'{:,.0f}'}), height=300)
        else:
            st.info("Transaction amount column not found in agg_trans CSV.")
    else:
        st.info("agg_trans CSV not available.")

# -----------------------------
# Scenario 2 (Key2)
# -----------------------------
elif page == "Scenario 2: Yearly Transaction Growth (Key2)":
    st.header("Scenario 2 — Yearly Transaction Growth (Key2)")
    if not dfs.get('agg_trans', pd.DataFrame()).empty:
        t = dfs['agg_trans']
        if 'year' in t.columns:
            amt_col = 'transaction_amount' if 'transaction_amount' in t.columns else next((c for c in ['amount','total_amount'] if c in t.columns), None)
            if amt_col:
                yearly = t.groupby('year', as_index=False)[amt_col].sum().rename(columns={amt_col:'total_amount'}).sort_values('year')
                fig = px.line(yearly, x='year', y='total_amount', markers=True, title='Yearly Transaction Growth')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(yearly.style.format({'total_amount':'{:,.0f}'}), height=300)
            else:
                st.info("Transaction amount column not found in agg_trans CSV.")
        else:
            st.info("Year column not present in agg_trans CSV.")
    else:
        st.info("agg_trans CSV not available.")

# -----------------------------
# Scenario 3 (Key3)
# -----------------------------
elif page == "Scenario 3: Insurance Penetration (Key3)":
    st.header("Scenario 3 — Insurance Penetration & Growth (Key3)")
    if not dfs.get('agg_ins', pd.DataFrame()).empty and not dfs.get('agg_trans', pd.DataFrame()).empty:
        ins = dfs['agg_ins']
        trans = dfs['agg_trans']
        ins_amt_col = 'insurance_amount' if 'insurance_amount' in ins.columns else next((c for c in ['amount','total_amount'] if c in ins.columns), None)
        trans_amt_col = 'transaction_amount' if 'transaction_amount' in trans.columns else next((c for c in ['amount','total_amount'] if c in trans.columns), None)
        if ins_amt_col and trans_amt_col:
            ins_state = ins.groupby('state', as_index=False)[ins_amt_col].sum().rename(columns={ins_amt_col:'insurance_amount'})
            trans_state = trans.groupby('state', as_index=False)[trans_amt_col].sum().rename(columns={trans_amt_col:'transaction_amount'})
            merged = ins_state.merge(trans_state, on='state', how='outer').fillna(0)
            merged['penetration_pct'] = (merged['insurance_amount'] / merged['transaction_amount'].replace({0:np.nan})) * 100
            merged['penetration_pct'] = merged['penetration_pct'].fillna(0)
            fig1 = px.bar(merged.sort_values('penetration_pct', ascending=False).head(15), x='state', y='penetration_pct', text_auto=True, title='Top States by Insurance Penetration (%)')
            st.plotly_chart(fig1, use_container_width=True)
            fig2 = px.bar(merged.sort_values('insurance_amount', ascending=False).head(15), x='state', y='insurance_amount', text_auto=True, title='Top States by Insurance Amount')
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(merged.sort_values('penetration_pct', ascending=False).head(15).style.format({'insurance_amount':'{:,.0f}','transaction_amount':'{:,.0f}','penetration_pct':'{:,.2f}'}), height=300)
        else:
            st.info("Insurance or transaction amount column missing in agg_ins/agg_trans.")
    else:
        st.info("agg_ins or agg_trans CSV not available.")

# -----------------------------
# Scenario 4 (Key4)
# -----------------------------
elif page == "Scenario 4: User Engagement by Brand (Key4)":
    st.header("Scenario 4 — Device Dominance & User Engagement (Key4)")
    if not dfs.get('agg_user', pd.DataFrame()).empty:
        u = dfs['agg_user']
        brand_col = next((c for c in ['brand','device','manufacturer'] if c in u.columns), None)
        user_col = next((c for c in ['brand_count','registered_users','registeredusers','total_users'] if c in u.columns), None)
        if brand_col and user_col:
            brand_tot = u.groupby(brand_col, as_index=False)[user_col].sum().rename(columns={brand_col:'brand', user_col:'brand_count'}).sort_values('brand_count', ascending=False)
            fig = px.bar(brand_tot.head(15), x='brand', y='brand_count', text_auto=True, title='Top 15 Mobile Brands by User Count')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(brand_tot.head(50).style.format({'brand_count':'{:,.0f}'}), height=300)
        else:
            st.info("Brand/user columns not found in agg_user CSV.")
    else:
        st.info("agg_user CSV not available.")

    # engagement ratio
    if not dfs.get('map_user', pd.DataFrame()).empty and not dfs.get('agg_user', pd.DataFrame()).empty:
        mu = dfs['map_user']
        au = dfs['agg_user']
        app_col = next((c for c in ['app_opens','appopens'] if c in mu.columns), None)
        reg_col = next((c for c in ['brand_count','registered_users','registeredusers','total_users'] if c in au.columns), None)
        if app_col and reg_col:
            app_state = mu.groupby('state', as_index=False)[app_col].sum().rename(columns={app_col:'app_opens'})
            reg_state = au.groupby('state', as_index=False)[reg_col].sum().rename(columns={reg_col:'registered_users'})
            merged = app_state.merge(reg_state, on='state', how='outer').fillna(0)
            merged['engagement_ratio'] = merged['app_opens'] / merged['registered_users'].replace({0:np.nan})
            merged['engagement_ratio'] = merged['engagement_ratio'].fillna(0)
            fig2 = px.bar(merged.sort_values('engagement_ratio', ascending=False).head(15), x='state', y='engagement_ratio', text_auto=True, title='Top States by App Opens per Registered User')
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(merged.sort_values('engagement_ratio', ascending=False).head(15).style.format({'app_opens':'{:,.0f}','registered_users':'{:,.0f}','engagement_ratio':'{:,.2f}'}), height=300)
        else:
            st.info("app_opens or registered user column missing in map_user/agg_user.")
    else:
        st.info("map_user or agg_user CSV not available for engagement ratio.")


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("### Data visualisation dashboard built with Streamlit and Plotly.")

