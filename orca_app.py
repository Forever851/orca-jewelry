import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATA ENGINE (KEEPING ALL ORIGINAL FUNCTIONS) ---
DB_PATH = "orca_jewelry_db.json"
ORCA_COLOR = "#00A89E"
SHOP_DETAILS = {
    "name": "ORCA JEWELRY",
    "phone": "+968 1234 5678",
    "address": "123 Gold Market, Muscat, Oman",
}

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

# --- 2. CUSTOM HTML/CSS INJECTION (YOUR STYLE) ---
def apply_gemportal_style():
    st.markdown(f"""
    <style>
        /* Sidebar Navigation Style */
        [data-testid="stSidebar"] {{
            background-color: #1e293b !important;
            width: 260px !important;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Main Content Background */
        .stApp {{
            background-color: #f8fafc;
        }}

        /* Card Style */
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            border: 1px solid #e2e8f0;
            color: #334155;
        }}

        /* Buttons */
        .stButton>button {{
            background: {ORCA_COLOR} !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            width: 100%;
        }}

        /* Table Headers */
        th {{
            background: #f1f5f9 !important;
            color: #64748b !important;
        }}
        
        /* Badges */
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            background: #e0f2f1;
            color: #008f86;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
def check_password():
    if "authenticated" not in st.session_state:
        st.markdown("<div class='card' style='max-width:400px; margin:100px auto; text-align:center;'>", unsafe_allow_html=True)
        st.header("💎 GemPortal Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "admin" and p == "orca123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# --- 4. PRINT TEMPLATE ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    return f"""
    <div style="font-family:Arial; padding:40px; border:1px solid #EEE; background:white; color:black;">
        <div style="text-align:center; border-bottom:4px solid {ORCA_COLOR}; padding-bottom:10px;">
            <h1 style="color:{ORCA_COLOR}; margin:0;">{SHOP_DETAILS['name']}</h1>
            <p>{SHOP_DETAILS['address']} | {SHOP_DETAILS['phone']}</p>
            <h2>TAX INVOICE</h2>
        </div>
        <div style="display:flex; justify-content:space-between; margin:30px 0;">
            <div><p><b>Bill To:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p></div>
            <div style="text-align:right;"><p><b>Invoice:</b> #INV-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
        </div>
        <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <thead><tr style="background:#F8F9FA;">
                <th style="padding:12px; border:1px solid #DDD; text-align:left;">Description</th>
                <th style="padding:12px; border:1px solid #DDD; text-align:right;">Total (OMR)</th>
            </tr></thead>
            <tbody><tr>
                <td style="padding:12px; border:1px solid #DDD;">{s['item']}</td>
                <td style="padding:12px; border:1px solid #DDD; text-align:right;">{s['total']:.3f}</td>
            </tr></tbody>
        </table>
        <div style="text-align:right; font-size:1.2em;">
            <p>Net Amount: <b>{s['total']:.3f} OMR</b></p>
            <p style="color:green;">Paid: {s['advance']:.3f} OMR</p>
            <p style="color:red;">Balance: {s['balance']:.3f} OMR</p>
        </div>
    </div>
    {print_trigger}
    """

# --- MAIN APP EXECUTION ---
st.set_page_config(page_title="GemPortal | ORCA", layout="wide")

if check_password():
    apply_gemportal_style()
    db = load_db()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # SIDEBAR NAV (Your Template Style)
    with st.sidebar:
        st.markdown(f"<h2 style='letter-spacing:2px;'>💎 GemPortal</h2>", unsafe_allow_html=True)
        menu = st.radio("MENU", ["Dashboard", "Inventory / Stock", "New Invoice", "Sales History"])
        st.divider()
        if st.button("Logout"):
            del st.session_state["authenticated"]
            st.rerun()

    # 1. DASHBOARD
    if menu == "Dashboard":
        st.markdown("<div class='header'><h1>Stock Overview</h1></div>", unsafe_allow_html=True)
        
        # Stats Grid
        c1, c2, c3 = st.columns(3)
        with c1:
            total_val = sum(i['price'] * i['quantity'] for i in db['stock'])
            st.markdown(f"<div class='card'><small>Total Stock Value</small><h2>{total_val:,.3f} OMR</h2></div>", unsafe_allow_html=True)
        with c2:
            units = sum(i['quantity'] for i in db['stock'])
            st.markdown(f"<div class='card'><small>Inventory Units</small><h2>{units}</h2></div>", unsafe_allow_html=True)
        with c3:
            sales_count = len(db['sales'])
            st.markdown(f"<div class='card'><small>Total Invoices</small><h2>{sales_count}</h2></div>", unsafe_allow_html=True)

        st.markdown("<div class='card'><h3>Recent Inventory</h3>", unsafe_allow_html=True)
        if db['stock']:
            st.table(pd.DataFrame(db['stock']))
        else:
            st.info("No items in stock.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. NEW INVOICE
    elif menu == "New Invoice":
        st.markdown("<div class='header'><h1>Create New Invoice</h1></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cust_name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        
        with col2:
            sale_type = st.radio("Sale Type", ["Stock", "Manufacturing"], horizontal=True)
            if sale_type == "Stock":
                item_names = [i['name'] for i in db['stock'] if i['quantity'] > 0]
                item_desc = st.selectbox("Select Item", item_names) if item_names else st.error("No Stock")
                price = next((i['price'] for i in db['stock'] if i['name'] == item_desc), 0.0)
            else:
                item_desc = st.text_input("Item Description")
                price = st.number_input("Total Price", format="%.3f")
            
            discount = st.slider("Discount (%)", 0, 100, 0)
            net_total = price * (1 - (discount/100))
            advance = st.number_input("Advance Payment", format="%.3f", value=net_total if sale_type=="Stock" else 0.0)
        
        if st.button("Confirm Sale & Print"):
            new_id = max([s.get('id', 0) for s in db['sales']] + [0]) + 1
            new_sale = {
                "id": new_id, "date": today_str, "customer": cust_name, "phone": phone,
                "gender": gender, "item": item_desc, "total": net_total,
                "advance": advance, "balance": net_total - advance,
                "status": "Pending" if (net_total - advance) > 0.001 else "Completed"
            }
            db['sales'].append(new_sale)
            if sale_type == "Stock":
                for i in db['stock']:
                    if i['name'] == item_desc: i['quantity'] -= 1
            save_db(db)
            components.html(get_bill_html(new_sale, auto_print=True), height=600, scrolling=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. SALES HISTORY
    elif menu == "Sales History":
        st.markdown("<div class='header'><h1>Sales Records</h1></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if db['sales']:
            df = pd.DataFrame(db['sales'])
            st.dataframe(df[['id', 'date', 'customer', 'total', 'advance', 'balance', 'status']].sort_values(by='id', ascending=False), use_container_width=True)
            
            st.divider()
            target_id = st.selectbox("Select Invoice # to update/reprint", df['id'].tolist())
            s_idx = next(i for i, s in enumerate(db['sales']) if s['id'] == target_id)
            s_rec = db['sales'][s_idx]
            
            c_up1, c_up2 = st.columns(2)
            with c_up1:
                st.write(f"Current Balance: {s_rec['balance']:.3f} OMR")
                add_pay = st.number_input("Add Payment", format="%.3f", max_value=s_rec['balance'])
                if st.button("Update Bill"):
                    db['sales'][s_idx]['advance'] += add_pay
                    db['sales'][s_idx]['balance'] -= add_pay
                    if db['sales'][s_idx]['balance'] <= 0.001: db['sales'][s_idx]['status'] = "Completed"
                    save_db(db); st.rerun()
            with c_up2:
                if st.button("Reprint A4"):
                    components.html(get_bill_html(s_rec, auto_print=True), height=600)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. INVENTORY
    elif menu == "Inventory / Stock":
        st.markdown("<div class='header'><h1>Inventory Management</h1></div>", unsafe_allow_html=True)
        with st.expander("+ Add New Item"):
            with st.form("inv_form"):
                n = st.text_input("Item Name")
                p = st.number_input("Retail Price", format="%.3f")
                q = st.number_input("Quantity", min_value=1)
                if st.form_submit_button("Save to Inventory"):
                    db['stock'].append({"name": n, "price": p, "quantity": q})
                    save_db(db); st.rerun()
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.table(db['stock'])
        st.markdown("</div>", unsafe_allow_html=True)