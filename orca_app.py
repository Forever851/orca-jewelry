import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image
import random

# --- 1. NEW DATABASE INITIALIZATION ---
# Using new filenames effectively clears/restarts the database
SALES_DB = "orca_sales_v2.json"
INVENTORY_DB = "orca_inventory_v2.json"
CUSTOMER_DB = "orca_customers_v2.json"
ORCA_COLOR = "#00A89E"

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

# --- 2. THEME & NAVIGATION CSS ---
st.set_page_config(page_title="ORCA Jewelry Pro", layout="wide")

st.markdown(f"""
    <style>
        :root {{
            --primary: {ORCA_COLOR};
            --primary-dark: #008f86;
            --bg-light: #f8fafc;
            --text-main: #334155;
            --border: #e2e8f0;
        }}

        /* Apply Sidebar CSS from your template */
        [data-testid="stSidebar"] {{
            background: #1e293b !important;
            min-width: 300px !important;
        }}
        
        /* Simulating your Nav structure in Streamlit sidebar */
        .nav-logo {{ text-align: center; padding-bottom: 20px; }}
        
        .nav-title {{
            color: var(--primary);
            font-size: 1.2rem;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
            font-weight: bold;
        }}

        /* Card & UI Styling */
        .stApp {{ background-color: var(--bg-light); color: var(--text-main); }}
        .card {{
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px; border: 1px solid var(--border);
        }}
        
        .footer-text {{
            position: fixed; bottom: 10px; left: 10px;
            color: #64748b; font-size: 0.75rem; z-index: 100;
        }}
        
        /* Streamlit Radio/Menu override to look like Nav Li */
        div[data-testid="stSidebarUserContent"] .st-emotion-cache-17l7m6r {{
            background: transparent; color: white; border-radius: 8px;
            padding: 12px 15px; transition: 0.3s;
        }}
    </style>
    <div class="footer-text">© All copyrights for Luqman Al Hoti</div>
""", unsafe_allow_html=True)

# --- 3. PRINT TEMPLATE ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    # VAT is 5%, already included in s['total']
    vat_included = s['total'] * 0.05 / 1.05
    return f"""
    <div style="font-family:'Segoe UI', sans-serif; padding:40px; background:white; color:#1e293b; max-width:800px; margin:auto; border: 1px solid #EEE;">
        <div style="text-align:center; border-bottom:4px solid {ORCA_COLOR}; padding-bottom:20px;">
            <h1 style="color:{ORCA_COLOR}; margin:0; letter-spacing:2px;">ORCA JEWELRY</h1>
            <p>Tax Registration No: 123456789 | Muscat, Oman</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin:30px 0;">
            <div><p><b>Customer:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p></div>
            <div style="text-align:right;"><p><b>Invoice:</b> #ORC-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
        </div>
        <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <thead><tr style="background:#f1f5f9;">
                <th style="padding:15px; border-bottom:2px solid #e2e8f0; text-align:left;">Description</th>
                <th style="padding:15px; border-bottom:2px solid #e2e8f0; text-align:right;">Total (Inc. VAT)</th>
            </tr></thead>
            <tbody><tr>
                <td style="padding:15px; border-bottom:1px solid #e2e8f0;">{s['item']}</td>
                <td style="padding:15px; border-bottom:1px solid #e2e8f0; text-align:right;">{s['total']:.3f} OMR</td>
            </tr></tbody>
        </table>
        <div style="text-align:right; font-size:1.1rem; line-height:1.8;">
            <p>VAT (5%) Included: {vat_included:.3f} OMR</p>
            <p style="font-size:1.4rem; font-weight:bold; color:{ORCA_COLOR};">Grand Total: {s['total']:.3f} OMR</p>
            <p style="color:#008f86;">Total Paid: {s['advance']:.3f} OMR</p>
            <p style="color:#e11d48; font-weight:bold;">Balance Due: {s['balance']:.3f} OMR</p>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="nav-logo">', unsafe_allow_html=True)
    try:
        logo = Image.open("logo.jpg")
        st.image(logo, use_container_width=True)
    except:
        st.write("💎")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-title">ORCA JEWELRY</div>', unsafe_allow_html=True)
    
    menu = st.radio("Navigation", ["Dashboard", "Inventory / Stock", "Invoice", "Sales History", "Customer Directory"], label_visibility="collapsed")

# --- 5. APP MODULES ---

if menu == "Dashboard":
    st.title("Stock & Sales Overview")
    c1, c2, c3 = st.columns(3)
    if db_sales:
        df = pd.DataFrame(db_sales)
        with c1: st.markdown(f'<div class="card"><small>Total Revenue</small><h2>{df["total"].sum():.3f}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card"><small>Unpaid Balance</small><h2>{df["balance"].sum():.3f}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card"><small>Items in Stock</small><h2>{len(db_stock)}</h2></div>', unsafe_allow_html=True)
    else:
        st.info("Start by adding inventory or creating an invoice.")

elif menu == "Inventory / Stock":
    st.title("Inventory Management")
    with st.expander("+ Add New Item"):
        with st.form("inv_form"):
            n = st.text_input("Item Name")
            p = st.number_input("Retail Price (Inc. VAT)", format="%.3f")
            q = st.number_input("Quantity", min_value=1)
            if st.form_submit_button("Generate Serial & Save"):
                serial = f"ORC-{random.randint(10000, 99999)}"
                db_stock.append({"serial": serial, "name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.rerun()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if db_stock:
        st.table(pd.DataFrame(db_stock))
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Invoice":
    st.title("New Invoice")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    phone = st.text_input("Customer Phone")
    c_name = db_cust.get(phone, {}).get("name", "")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Customer Name", value=c_name)
        item_opt = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
        selected = st.selectbox("Stock Item", ["Custom / Manufacturing"] + item_opt)
    with col2:
        base_price = 0.0
        if selected != "Custom / Manufacturing":
            serial_code = selected.split(" - ")[0]
            base_price = next(i['price'] for i in db_stock if i['serial'] == serial_code)
        price = st.number_input("Price (OMR)", value=base_price, format="%.3f")
        discount = st.number_input("Discount (OMR)", value=0.0, format="%.3f")
    
    final_total = price - discount
    paid = st.number_input("Amount Paid Now", format="%.3f")
    desc = st.text_area("Description", height=100)

    if st.button("Confirm & Print"):
        db_cust[phone] = {"name": name}
        save_json(CUSTOMER_DB, db_cust)
        new_id = len(db_sales) + 1
        sale_data = {
            "id": new_id, "date": datetime.now().strftime("%Y-%m-%d"),
            "customer": name, "phone": phone, "item": desc,
            "total": final_total, "advance": paid, "balance": final_total - paid
        }
        db_sales.append(sale_data)
        save_json(SALES_DB, db_sales)
        if selected != "Custom / Manufacturing":
            for i in db_stock:
                if i['serial'] == selected.split(" - ")[0]: i['quantity'] -= 1
            save_json(INVENTORY_DB, db_stock)
        components.html(get_bill_html(sale_data, auto_print=True), height=600, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Transaction History")
    if db_sales:
        df_h = pd.DataFrame(db_sales)
        st.dataframe(df_h, use_container_width=True)
        
        st.markdown('<div class="card"><h3>Update & Print Invoice</h3>', unsafe_allow_html=True)
        inv_id = st.selectbox("Select Invoice ID", df_h['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == inv_id)
        
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            st.write(f"Current Balance: **{db_sales[idx]['balance']:.3f} OMR**")
            new_payment = st.number_input("Additional Payment", format="%.3f")
            if st.button("Update Payment"):
                db_sales[idx]['advance'] += new_payment
                db_sales[idx]['balance'] -= new_payment
                save_json(SALES_DB, db_sales)
                st.success("Balance Updated!")
                st.rerun()
        with c_up2:
            if st.button("Print Invoice Now"):
                components.html(get_bill_html(db_sales[idx], auto_print=True), height=600)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Customer Directory":
    st.title("Customer Directory")
    if db_cust:
        st.table([{"Phone": k, "Name": v['name']} for k, v in db_cust.items()])