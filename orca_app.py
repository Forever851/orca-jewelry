import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image
import random

# --- 1. DATABASE ENGINE ---
SALES_DB = "orca_sales_v2.json"
INVENTORY_DB = "orca_inventory_v2.json"
CUSTOMER_DB = "orca_customers_v2.json"
PRIMARY_COLOR = "#00A89E"

def load_json(path, default_data):
    if not os.path.exists(path):
        with open(path, 'w') as f: json.dump(default_data, f)
    with open(path, 'r') as f:
        try: return json.load(f)
        except: return default_data

def save_json(path, data):
    with open(path, 'w') as f: json.dump(data, f, indent=4)

db_sales = load_json(SALES_DB, [])
db_stock = load_json(INVENTORY_DB, [])
db_cust = load_json(CUSTOMER_DB, {})

# --- 2. THEME & EXACT NAVIGATION CSS ---
st.set_page_config(page_title="ORCA Jewelry", layout="wide")

st.markdown(f"""
    <style>
        :root {{
            --primary: {PRIMARY_COLOR};
        }}
        
        /* Sidebar Navigation Container */
        [data-testid="stSidebar"] {{
            background: #1e293b !important;
            min-width: 280px !important;
        }}

        /* Sidebar content styling to match your 'nav' css */
        .nav-container {{
            padding: 20px;
            text-align: center;
        }}

        .nav-container h2 {{
            color: var(--primary);
            font-size: 1.2rem;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-family: 'Segoe UI', sans-serif;
        }}

        /* Styling Streamlit's radio buttons to look like 'nav li' */
        div[data-testid="stSidebarUserContent"] .st-emotion-cache-17l7m6r {{
            background-color: transparent;
            color: white !important;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            transition: 0.3s;
            border: none;
        }}

        div[data-testid="stSidebarUserContent"] .st-emotion-cache-17l7m6r:hover {{
            background-color: var(--primary) !important;
        }}

        /* Active State */
        div[data-testid="stSidebarUserContent"] input:checked + div {{
            background-color: var(--primary) !important;
            color: white !important;
        }}

        /* Main UI Cards */
        .stApp {{ background-color: #f8fafc; }}
        .card {{
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px; border: 1px solid #e2e8f0;
        }}
        
        .footer-text {{
            position: fixed; bottom: 10px; left: 10px;
            color: #64748b; font-size: 0.75rem; z-index: 100;
        }}
    </style>
    <div class="footer-text">© All copyrights for Luqman Al Hoti</div>
""", unsafe_allow_html=True)

# --- 3. INVOICE PRINTING TOOL ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    vat_amt = s['total'] * 0.05 / 1.05
    return f"""
    <div style="font-family:sans-serif; padding:40px; background:white; color:#1e293b; max-width:800px; margin:auto; border:1px solid #EEE;">
        <div style="text-align:center; border-bottom:4px solid {PRIMARY_COLOR}; padding-bottom:20px;">
            <h1 style="color:{PRIMARY_COLOR}; margin:0;">ORCA JEWELRY</h1>
            <p>Muscat, Oman | Tax Invoice</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin:30px 0;">
            <div><p><b>Customer:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p></div>
            <div style="text-align:right;"><p><b>Invoice:</b> #ORC-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#f8fafc;"><th style="padding:12px; border:1px solid #DDD; text-align:left;">Description</th><th style="padding:12px; border:1px solid #DDD; text-align:right;">Total (Inc. VAT)</th></tr>
            <tr><td style="padding:12px; border:1px solid #DDD;">{s['item']}</td><td style="padding:12px; border:1px solid #DDD; text-align:right;">{s['total']:.3f} OMR</td></tr>
        </table>
        <div style="text-align:right; margin-top:20px;">
            <p>VAT (5%) Included: {vat_amt:.3f} OMR</p>
            <h2 style="color:{PRIMARY_COLOR};">Grand Total: {s['total']:.3f} OMR</h2>
            <p>Paid: {s['advance']:.3f} OMR | <b>Balance: {s['balance']:.3f} OMR</b></p>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=100) # Small centered logo
    except:
        st.write("💎")
    st.markdown("<h2>💎 ORCA JEWELRY</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    menu = st.radio("NAV", ["Dashboard", "Inventory / Stock", "Invoice", "Sales History", "Customer Directory"], label_visibility="collapsed")

# --- 5. PAGE LOGIC ---

if menu == "Dashboard":
    st.title("Business Dashboard")
    # Statistics
    c1, c2, c3 = st.columns(3)
    stock_count = sum(i['quantity'] for i in db_stock)
    rev = sum(s['total'] for s in db_sales)
    
    with c1: st.markdown(f'<div class="card"><small>Total Revenue</small><h2>{rev:.3f} OMR</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><small>Stock Units</small><h2>{stock_count}</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><small>Total Invoices</small><h2>{len(db_sales)}</h2></div>', unsafe_allow_html=True)

    # Charts
    if db_sales:
        df_sales = pd.DataFrame(db_sales)
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Daily Sales Performance")
        fig = px.line(df_sales.groupby('date')['total'].sum().reset_index(), x='date', y='total', color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    

elif menu == "Inventory / Stock":
    st.title("Inventory Management")
    with st.expander("+ Add New Item"):
        with st.form("stock_add"):
            n = st.text_input("Item Name")
            p = st.number_input("Unit Price (Inc. VAT)", format="%.3f")
            q = st.number_input("Initial Quantity", min_value=1)
            if st.form_submit_button("Save Item"):
                db_stock.append({"serial": f"ORC-{random.randint(1000,9999)}", "name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.rerun()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if db_stock:
        st.table(db_stock)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Invoice":
    st.title("Generate Invoice")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    phone = st.text_input("Customer Phone")
    cust_name = db_cust.get(phone, {}).get("name", "")
    name = st.text_input("Customer Name", value=cust_name)
    
    mode = st.radio("Source", ["Stock Item", "Manufacturing"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if mode == "Stock Item":
            opts = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
            selected = st.selectbox("Select Product", opts)
            item_price = next(i['price'] for i in db_stock if i['serial'] == selected.split(" - ")[0])
            price = st.number_input("Retail Price", value=item_price, format="%.3f")
        else:
            price = st.number_input("Agreed Price", format="%.3f")
        
        discount = st.number_input("Discount", format="%.3f")
    
    with col2:
        paid = st.number_input("Advance Payment", format="%.3f")
        desc = st.text_area("Item Description (4 Lines)", height=100)
    
    total = price - discount
    if st.button("Confirm & Print"):
        db_cust[phone] = {"name": name}
        save_json(CUSTOMER_DB, db_cust)
        
        sale = {"id": len(db_sales)+1, "date": datetime.now().strftime("%Y-%m-%d"), "customer": name, "phone": phone, "item": desc, "total": total, "advance": paid, "balance": total-paid}
        db_sales.append(sale)
        save_json(SALES_DB, db_sales)
        
        if mode == "Stock Item":
            s_id = selected.split(" - ")[0]
            for i in db_stock:
                if i['serial'] == s_id: i['quantity'] -= 1
            save_json(INVENTORY_DB, db_stock)
            
        components.html(get_bill_html(sale, True), height=600)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Sales & Bill Updates")
    if db_sales:
        df_h = pd.DataFrame(db_sales)
        st.dataframe(df_h, use_container_width=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        target = st.selectbox("Select Invoice to Update/Print", df_h['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == target)
        
        st.write(f"Remaining Balance: **{db_sales[idx]['balance']:.3f} OMR**")
        add_pay = st.number_input("New Payment", format="%.3f")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Update Payment"):
                db_sales[idx]['advance'] += add_pay
                db_sales[idx]['balance'] -= add_pay
                save_json(SALES_DB, db_sales); st.rerun()
        with c2:
            if st.button("Reprint Invoice"):
                components.html(get_bill_html(db_sales[idx], True), height=600)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Customer Directory":
    st.title("Directory")
    search = st.text_input("🔍 Search Name or Phone Number").lower()
    if db_cust:
        results = [{"Phone": k, "Name": v['name']} for k, v in db_cust.items() if search in k or search in v['name'].lower()]
        st.table(results)