import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image
import random

# --- 1. CONFIG & DB ENGINE ---
SALES_DB = "orca_sales.json"
INVENTORY_DB = "orca_inventory.json"
CUSTOMER_DB = "orca_customers.json"
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

st.set_page_config(page_title="ORCA Jewelry Pro", layout="wide")

# --- 2. CUSTOM CSS (NAVBAR & UI) ---
st.markdown(f"""
    <style>
        /* Navbar Style */
        [data-testid="stSidebar"] {{
            background-color: #1e293b !important;
            min-width: 300px !important;
        }}
        .nav-header {{
            text-align: center;
            padding: 20px 0;
            color: {ORCA_COLOR};
        }}
        .nav-header h2 {{
            font-size: 1.2rem;
            letter-spacing: 2px;
            margin-top: 10px;
        }}
        /* Main UI */
        .stApp {{ background-color: #f8fafc; }}
        .card {{
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }}
        .footer-text {{
            position: fixed; bottom: 10px; left: 10px;
            color: #64748b; font-size: 0.75rem; z-index: 100;
        }}
    </style>
    <div class="footer-text">© All copyrights for Luqman Al Hoti</div>
""", unsafe_allow_html=True)

# --- 3. PRINT TEMPLATES (INVOICE & BARCODE) ---
def get_bill_html(s, auto_print=False):
    # s['total'] is already VAT inclusive from the logic below
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    return f"""
    <div style="font-family:sans-serif; padding:30px; border:1px solid #EEE; background:white; max-width:800px; margin:auto; color:#333;">
        <div style="text-align:center; border-bottom:3px solid {ORCA_COLOR}; padding-bottom:15px;">
            <h1 style="color:{ORCA_COLOR}; margin:0;">ORCA JEWELRY</h1>
            <p>Muscat, Oman | +968 1234 5678</p>
            <h2 style="letter-spacing:3px;">TAX INVOICE</h2>
        </div>
        <div style="display:flex; justify-content:space-between; margin:20px 0;">
            <div><p><b>Bill To:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p></div>
            <div style="text-align:right;"><p><b>Invoice:</b> #ORC-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#F8F9FA;"><th style="padding:10px; border:1px solid #DDD; text-align:left;">Description</th><th style="padding:10px; border:1px solid #DDD; text-align:right;">Total (Inc. VAT)</th></tr>
            <tr><td style="padding:15px; border:1px solid #DDD;">{s['item']}</td><td style="padding:15px; border:1px solid #DDD; text-align:right;">{s['total']:.3f} OMR</td></tr>
        </table>
        <div style="text-align:right; margin-top:20px;">
            <p>VAT (5%) Included: {(s['total'] * 0.05 / 1.05):.3f} OMR</p>
            <h3 style="color:{ORCA_COLOR};">Grand Total: {s['total']:.3f} OMR</h3>
            <p style="color:green;">Paid: {s['advance']:.3f} OMR</p>
            <p style="color:red;">Balance: {s['balance']:.3f} OMR</p>
        </div>
    </div>
    {print_trigger}
    """

def get_barcode_html(serial, name, price):
    return f"""
    <div style="border:1px solid #000; padding:10px; width:200px; text-align:center; font-family:monospace;">
        <div style="font-weight:bold; font-size:14px;">ORCA JEWELRY</div>
        <div style="font-size:10px;">{name}</div>
        <div style="background:#000; color:#fff; margin:5px 0; padding:2px;">{serial}</div>
        <div style="font-size:12px;">{price:.3f} OMR</div>
        <button onclick="window.print()" style="margin-top:5px; font-size:8px;">Print Label</button>
    </div>
    """

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="nav-header">', unsafe_allow_html=True)
    try:
        logo = Image.open("logo.jpg")
        st.image(logo, use_container_width=True)
    except:
        st.write("LOGO MISSING")
    st.markdown("<h2>💎 ORCA JEWELRY</h2></div>", unsafe_allow_html=True)
    
    menu = st.radio("", ["Dashboard", "Inventory / Stock", "Invoice", "Sales History", "Customer Directory"], label_visibility="collapsed")

# --- 5. APP MODULES ---

if menu == "Dashboard":
    st.title("Orca Business Overview")
    if db_sales:
        df = pd.DataFrame(db_sales)
        df['date'] = pd.to_datetime(df['date'])
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Revenue (Inc. VAT)", f"{df['total'].sum():.3f} OMR")
        with c2: st.metric("Outstanding Balance", f"{df['balance'].sum():.3f} OMR")
        with c3: st.metric("Active Inventory", len(db_stock))
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Daily Invoice Volume")
        daily_inv = df.groupby('date').size().reset_index(name='count')
        st.plotly_chart(px.line(daily_inv, x='date', y='count', color_discrete_sequence=[ORCA_COLOR]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Inventory / Stock":
    st.title("Inventory & Barcoding")
    with st.expander("+ Add New Item & Generate Serial"):
        with st.form("inv_form"):
            n = st.text_input("Item Name")
            p = st.number_input("Price (OMR)", format="%.3f")
            q = st.number_input("Quantity", min_value=1)
            if st.form_submit_button("Generate Serial & Save"):
                serial = f"ORC-{random.randint(10000, 99999)}"
                db_stock.append({"serial": serial, "name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.success(f"Generated Serial: {serial}")
                st.rerun()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if db_stock:
        df_s = pd.DataFrame(db_stock)
        st.dataframe(df_s, use_container_width=True)
        sel_item = st.selectbox("Select Item to Print Barcode", df_s['serial'].tolist())
        item_data = next(i for i in db_stock if i['serial'] == sel_item)
        components.html(get_barcode_html(item_data['serial'], item_data['name'], item_data['price']), height=150)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Invoice":
    st.title("New Tax Invoice")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    phone = st.text_input("Customer Phone")
    c_name = db_cust.get(phone, {}).get("name", "")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Customer Name", value=c_name)
        item_opt = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
        selected = st.selectbox("Select from Stock", ["Custom / Manufacturing"] + item_opt)
    
    with col2:
        if selected == "Custom / Manufacturing":
            price = st.number_input("Base Price (OMR)", format="%.3f")
        else:
            serial_code = selected.split(" - ")[0]
            price = next(i['price'] for i in db_stock if i['serial'] == serial_code)
            st.info(f"Stock Price: {price:.3f} OMR")
        
        discount_amt = st.number_input("Apply Discount (OMR)", format="%.3f", value=0.0)

    # VAT Logic: (Base - Discount) + 5% VAT
    subtotal = price - discount_amt
    vat = subtotal * 0.05
    grand_total = subtotal + vat
    
    st.markdown(f"### Total Amount (Inclusive of 5% VAT): **{grand_total:.3f} OMR**")
    paid = st.number_input("Payment Received", format="%.3f")
    desc = st.text_area("Item Description (4 lines)", height=100)

    if st.button("Confirm Sale"):
        db_cust[phone] = {"name": name}
        save_json(CUSTOMER_DB, db_cust)
        
        new_id = len(db_sales) + 1
        sale_data = {
            "id": new_id, "date": datetime.now().strftime("%Y-%m-%d"),
            "customer": name, "phone": phone, "item": desc,
            "total": grand_total, "advance": paid, "balance": grand_total - paid
        }
        db_sales.append(sale_data)
        save_json(SALES_DB, db_sales)
        
        if selected != "Custom / Manufacturing":
            for i in db_stock:
                if i['serial'] == selected.split(" - ")[0]: i['quantity'] -= 1
            save_json(INVENTORY_DB, db_stock)
        
        components.html(get_bill_html(sale_data, auto_print=True), height=600)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Transaction History")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if db_sales:
        df_h = pd.DataFrame(db_sales)
        st.dataframe(df_h, use_container_width=True)
        
        st.subheader("Update Bill / Balance")
        inv_to_edit = st.selectbox("Select Invoice ID", df_h['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == inv_to_edit)
        
        u_col1, u_col2 = st.columns(2)
        with u_col1:
            st.write(f"Remaining Balance: **{db_sales[idx]['balance']:.3f} OMR**")
            new_payment = st.number_input("New Payment Received", format="%.3f")
        with u_col2:
            if st.button("Update Transaction"):
                db_sales[idx]['advance'] += new_payment
                db_sales[idx]['balance'] -= new_payment
                save_json(SALES_DB, db_sales)
                st.success("Payment Updated!")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Customer Directory":
    st.title("Customer Records")
    if db_cust:
        st.table([{"Phone": k, "Name": v['name']} for k, v in db_cust.items()])