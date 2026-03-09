import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image
import random

# --- 1. DATABASE INITIALIZATION ---
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

# --- 2. CUSTOM THEME & SIDEBAR CSS ---
st.set_page_config(page_title="ORCA Jewelry Management", layout="wide")

st.markdown(f"""
    <style>
        /* Sidebar Menu Background Color */
        [data-testid="stSidebar"] {{
            background-color: {ORCA_COLOR} !important;
            min-width: 260px !important;
        }}
        
        /* Make Sidebar Text White */
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}

        /* Adjusting Logo Padding */
        .nav-logo-container {{
            text-align: center;
            padding: 10px 0 30px 0;
        }}

        /* Main Content Styling */
        .stApp {{ background-color: #f8fafc; color: #334155; }}
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

# --- 3. PRINT TEMPLATE ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    vat_included = s['total'] * 0.05 / 1.05
    return f"""
    <div style="font-family:sans-serif; padding:40px; background:white; color:#1e293b; max-width:800px; margin:auto; border:1px solid #EEE;">
        <div style="text-align:center; border-bottom:4px solid {ORCA_COLOR}; padding-bottom:20px;">
            <h1 style="color:{ORCA_COLOR}; margin:0;">ORCA JEWELRY</h1>
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
            <p>VAT (5%) Inc: {vat_included:.3f} OMR</p>
            <h2 style="color:{ORCA_COLOR};">Total: {s['total']:.3f} OMR</h2>
            <p>Paid: {s['advance']:.3f} OMR | <b>Balance: {s['balance']:.3f} OMR</b></p>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="nav-logo-container">', unsafe_allow_html=True)
    try:
        # Smaller logo as requested (width restricted)
        logo = Image.open("logo.png")
        st.image(logo, width=150)
    except:
        st.write("💎")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Title removed from here as per instructions
    menu = st.radio("MENU", ["Dashboard", "Inventory / Stock", "Invoice", "Sales History", "Customer Directory"], label_visibility="collapsed")

# --- 5. APP MODULES ---

if menu == "Dashboard":
    st.title("Business Analytics")
    if db_sales:
        df = pd.DataFrame(db_sales)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="card"><small>Revenue</small><h2>{df["total"].sum():.3f} OMR</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card"><small>Unpaid</small><h2>{df["balance"].sum():.3f} OMR</h2></div>', unsafe_allow_html=True)
    else:
        st.info("Welcome to Orca Jewelry. Use the sidebar to navigate.")

elif menu == "Inventory / Stock":
    st.title("Inventory")
    with st.expander("+ Add Stock Item"):
        with st.form("inv"):
            n = st.text_input("Name")
            p = st.number_input("Price", format="%.3f")
            q = st.number_input("Qty", min_value=1)
            if st.form_submit_button("Save"):
                db_stock.append({"serial": f"ORC-{random.randint(1000,9999)}", "name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.rerun()
    st.table(db_stock)

elif menu == "Invoice":
    st.title("New Invoice")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    phone = st.text_input("Customer Phone")
    c_name = db_cust.get(phone, {}).get("name", "")
    name = st.text_input("Customer Name", value=c_name)
    
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Price (Inc. VAT)", format="%.3f")
        discount = st.number_input("Discount", format="%.3f")
    with col2:
        paid = st.number_input("Payment", format="%.3f")
        desc = st.text_area("Item Details", height=100)
    
    total = price - discount
    if st.button("Confirm & Print"):
        db_cust[phone] = {"name": name}
        save_json(CUSTOMER_DB, db_cust)
        sale = {"id": len(db_sales)+1, "date": datetime.now().strftime("%Y-%m-%d"), "customer": name, "phone": phone, "item": desc, "total": total, "advance": paid, "balance": total-paid}
        db_sales.append(sale)
        save_json(SALES_DB, db_sales)
        components.html(get_bill_html(sale, True), height=600)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Sales & Updates")
    if db_sales:
        df_h = pd.DataFrame(db_sales)
        st.dataframe(df_h, use_container_width=True)
        
        st.subheader("Update Payment & Print")
        target = st.selectbox("Select Invoice ID", df_h['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == target)
        
        up_val = st.number_input("New Payment", format="%.3f")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Update Bill"):
                db_sales[idx]['advance'] += up_val
                db_sales[idx]['balance'] -= up_val
                save_json(SALES_DB, db_sales); st.rerun()
        with c2:
            if st.button("Print Updated Invoice"):
                components.html(get_bill_html(db_sales[idx], True), height=600)

elif menu == "Customer Directory":
    st.title("Customer Directory")
    
    # --- SEARCH FUNCTIONALITY ---
    search_query = st.text_input("🔍 Search by Name or Phone Number", "").lower()
    
    if db_cust:
        cust_list = [{"Phone": k, "Name": v['name']} for k, v in db_cust.items()]
        # Filter logic
        filtered_list = [
            c for c in cust_list 
            if search_query in c['Name'].lower() or search_query in c['Phone']
        ]
        
        if filtered_list:
            st.markdown(f"**Found {len(filtered_list)} customer(s)**")
            st.table(pd.DataFrame(filtered_list))
        else:
            st.warning("No customers matching your search.")
    else:
        st.info("No customers found in database.")