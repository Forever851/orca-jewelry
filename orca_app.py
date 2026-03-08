import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. LOGIN SYSTEM ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "orca123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #00A89E;'>ORCA Jewelry Login</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True

# --- 2. CONFIG & BRANDING ---
# Change DB_PATH to work on GitHub/Cloud
DB_PATH = "orca_jewelry_db.json" 
ORCA_COLOR = "#00A89E"
SHOP_DETAILS = {
    "name": "ORCA JEWELRY",
    "phone": "+968 1234 5678",
    "address": "123 Gold Market, Muscat, Oman",
    "cn_code": "CN-99821"
}

st.set_page_config(page_title="ORCA Jewelry Pro", layout="wide", page_icon="💎")

if check_password():
    # --- DATA ENGINE ---
    def load_db():
        if not os.path.exists(DB_PATH):
            with open(DB_PATH, 'w') as f:
                json.dump({"stock": [], "sales": []}, f)
        with open(DB_PATH, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {"stock": [], "sales": []}
            if "sales" not in data: data["sales"] = []
            if "stock" not in data: data["stock"] = []
            for s in data["sales"]:
                s.setdefault("balance", 0.0)
                s.setdefault("advance", s.get("total", 0.0))
                s.setdefault("status", "Completed")
            return data

    def save_db(data):
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)

    db = load_db()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # --- HTML/JS PRINT TEMPLATE ---
    def get_bill_html(s, auto_print=False):
        print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
        return f"""
        <html>
        <head>
            <style>
                @media print {{ @page {{ size: A4; margin: 15mm; }} .no-print {{ display: none; }} }}
                body {{ font-family: 'Arial', sans-serif; color: #333; padding: 20px; }}
                .bill-card {{ border: 1px solid #EEE; padding: 40px; background: #FFF; max-width: 800px; margin: auto; }}
                .header {{ text-align: center; border-bottom: 4px solid {ORCA_COLOR}; padding-bottom: 10px; }}
                .info-grid {{ display: flex; justify-content: space-between; margin: 30px 0; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .table th {{ background: #F8F9FA; border: 1px solid #DDD; padding: 12px; text-align: left; }}
                .table td {{ border: 1px solid #DDD; padding: 12px; }}
                .totals {{ text-align: right; margin-top: 30px; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="bill-card">
                <div class="header">
                    <h1 style="margin:0; color:{ORCA_COLOR};">{SHOP_DETAILS['name']}</h1>
                    <p>{SHOP_DETAILS['address']} | {SHOP_DETAILS['phone']}</p>
                    <h2 style="letter-spacing: 2px;">TAX INVOICE</h2>
                </div>
                <div class="info-grid">
                    <div><p><b>Bill To:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p><p><b>Gender:</b> {s['gender']}</p></div>
                    <div style="text-align: right;"><p><b>Invoice ID:</b> #INV-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
                </div>
                <table class="table">
                    <thead><tr><th>Description</th><th style="text-align:right;">Total (OMR)</th></tr></thead>
                    <tbody><tr><td>{s['item']}</td><td style="text-align:right;">{s['total']:.3f}</td></tr></tbody>
                </table>
                <div class="totals">
                    <p>Net Amount: <b>{s['total']:.3f} OMR</b></p>
                    <p style="color: green;">Total Paid: <b>{s['advance']:.3f} OMR</b></p>
                    <p style="color: red;">Remaining Balance: <b>{s['balance']:.3f} OMR</b></p>
                    <hr><p>Status: <b>{s['status']}</b></p>
                </div>
            </div>
            {print_trigger}
        </body>
        </html>
        """

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h1 style='color:{ORCA_COLOR};'>ORCA PRO</h1>", unsafe_allow_html=True)
        menu = st.radio("Navigation", ["Dashboard", "New Invoice", "Inventory", "Sales History"])
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.markdown(f"<h1 style='color:{ORCA_COLOR}'>Business Dashboard</h1>", unsafe_allow_html=True)
        if db['sales']:
            df = pd.DataFrame(db['sales'])
            df['date'] = pd.to_datetime(df['date'])
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Cash Collected", f"{df['advance'].sum():.3f} OMR")
            with c2: st.metric("Outstanding Balance", f"{df['balance'].sum():.3f} OMR")
            with c3: st.metric("Total Invoices", len(df))
            st.divider()
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Daily Cash Flow")
                daily_rev = df.groupby('date')['advance'].sum().reset_index()
                fig = px.line(daily_rev, x='date', y='advance', template="simple_white", color_discrete_sequence=[ORCA_COLOR])
                st.plotly_chart(fig, use_container_width=True)
            with col_right:
                st.subheader("Order Status Distribution")
                fig2 = px.pie(df, names='status', color_discrete_sequence=[ORCA_COLOR, "#FF4B4B"])
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data recorded yet.")

    # --- 2. NEW INVOICE ---
    elif menu == "New Invoice":
        st.markdown(f"<h1 style='color:{ORCA_COLOR}'>Create Invoice</h1>", unsafe_allow_html=True)
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1: cust_name = st.text_input("Customer Name")
            with col2: phone = st.text_input("Phone Number")
            with col3: gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        
        sale_type = st.radio("Sale Type", ["Direct from Stock", "Manufacturing Order"], horizontal=True)
        price = 0.0
        item_desc = ""

        if sale_type == "Direct from Stock":
            items = [i['name'] for i in db['stock'] if i['quantity'] > 0]
            if items:
                item_desc = st.selectbox("Select Product", items)
                price = next(i['price'] for i in db['stock'] if i['name'] == item_desc)
                st.info(f"Unit Price: {price:.3f} OMR")
            else:
                st.warning("No stock available.")
        else:
            item_desc = st.text_input("Item Description")
            cc1, cc2, cc3 = st.columns(3)
            with cc1: m = st.number_input("Metal/Gold", format="%.3f")
            with cc2: s = st.number_input("Stone/Gem", format="%.3f")
            with cc3: l = st.number_input("Labor/Work", format="%.3f")
            price = m + s + l

        discount = st.slider("Discount (%)", 0, 100, 0)
        net_total = price * (1 - (discount/100))
        advance = st.number_input("Payment Received", value=net_total if sale_type == "Direct from Stock" else 0.0, format="%.3f")

        if st.button("Confirm Sale & Print", use_container_width=True):
            if not cust_name or not item_desc:
                st.error("Missing Customer Name or Item Description.")
            else:
                new_id = max([s.get('id', 0) for s in db['sales']] + [0]) + 1
                new_sale = {
                    "id": new_id, "date": today_str, "customer": cust_name, "phone": phone,
                    "gender": gender, "item": item_desc, "total": net_total,
                    "advance": advance, "balance": net_total - advance,
                    "status": "Pending" if (net_total - advance) > 0.001 else "Completed"
                }
                db['sales'].append(new_sale)
                if sale_type == "Direct from Stock":
                    for i in db['stock']:
                        if i['name'] == item_desc: i['quantity'] -= 1
                save_db(db)
                components.html(get_bill_html(new_sale, auto_print=True), height=600, scrolling=True)

    # --- 3. SALES HISTORY ---
    elif menu == "Sales History":
        st.markdown(f"<h1 style='color:{ORCA_COLOR}'>Sales Records</h1>", unsafe_allow_html=True)
        search_q = st.text_input("🔍 Search by Name or Phone")
        if db['sales']:
            df_hist = pd.DataFrame(db['sales'])
            if search_q:
                df_hist = df_hist[df_hist['customer'].str.contains(search_q, case=False) | df_hist['phone'].str.contains(search_q)]
            st.dataframe(df_hist[['id', 'date', 'customer', 'item', 'total', 'advance', 'balance', 'status']].sort_values(by='id', ascending=False), use_container_width=True)
            st.divider()
            target_id = st.selectbox("Select Invoice #", df_hist['id'].tolist())
            s_idx = next(i for i, s in enumerate(db['sales']) if s['id'] == target_id)
            s_data = db['sales'][s_idx]
            h1, h2 = st.columns(2)
            with h1:
                st.write(f"Current Balance: **{s_data['balance']:.3f} OMR**")
                new_pmt = st.number_input("New Payment Received (+)", format="%.3f", max_value=s_data['balance'])
                if st.button("Update and Save"):
                    db['sales'][s_idx]['advance'] += new_pmt
                    db['sales'][s_idx]['balance'] -= new_pmt
                    if db['sales'][s_idx]['balance'] <= 0.001: db['sales'][s_idx]['status'] = "Completed"
                    save_db(db)
                    st.rerun()
            with h2:
                if st.button("Reprint A4 Invoice"):
                    components.html(get_bill_html(s_data, auto_print=True), height=600, scrolling=True)

    # --- 4. INVENTORY ---
    elif menu == "Inventory":
        st.markdown(f"<h1 style='color:{ORCA_COLOR}'>Stock Management</h1>", unsafe_allow_html=True)
        with st.expander("Add New Product"):
            with st.form("inv_form"):
                n = st.text_input("Item Name")
                p = st.number_input("Retail Price", format="%.3f")
                q = st.number_input("Stock Quantity", min_value=1)
                if st.form_submit_button("Save"):
                    db['stock'].append({"name": n, "price": p, "quantity": q})
                    save_db(db)
                    st.rerun()
        st.table(db['stock'])