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
ORCA_COLOR = "#00A89E"
GOLD_ACCENT = "#D4AF37"

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

# --- 2. LOGIN LOGIC ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login():
    if st.session_state['authenticated']:
        return True
    
    # Login Screen UI
    st.markdown(f"""
        <style>
            .login-card {{
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                max-width: 400px;
                margin: 100px auto;
                text-align: center;
                border-top: 5px solid {ORCA_COLOR};
            }}
            .stApp {{ background-color: #f0f2f6; }}
            h1 {{ font-family: 'Cinzel', serif; color: {ORCA_COLOR}; }}
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown(f"<h1 style='letter-spacing:5px;'>Orca Jewellery</h1><p style='color:#666; font-size:12px; margin-bottom:30px;'></p>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Enter username")
        pw = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login"):
            if user == "admin" and pw == "orca123":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown('</div>', unsafe_allow_html=True)
    return False

# --- 3. MAIN APP START ---
if check_login():
    # --- UI STYLING ---
    st.set_page_config(page_title="ORCA Jewelry | Management", layout="wide")

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');
            
            .stApp {{ background-color: #f8fafb; font-family: 'Inter', sans-serif; }}

            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #072e2b 0%, #001a18 100%) !important;
                box-shadow: 4px 0 15px rgba(0,0,0,0.2);
                min-width: 300px !important;
            }}

            .logo-section {{
                padding: 45px 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 30px;
            }}
            .logo-text {{
                font-family: 'Cinzel', serif;
                color: {GOLD_ACCENT};
                font-size: 24px;
                letter-spacing: 4px;
                margin: 0;
                font-weight: 700;
            }}
            .logo-subtext {{
                color: white;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 4px;
                opacity: 0.8;
                margin-top: 8px;
            }}

            /* Sidebar Tabs */
            [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{ display: none; }}
            [data-testid="stSidebar"] div[role="radiogroup"] {{ display: flex; flex-direction: column; gap: 12px; padding: 0 20px; }}
            [data-testid="stSidebar"] div[role="radiogroup"] label {{
                background: rgba(255,255,255,0.05) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                padding: 15px 20px !important;
                border-radius: 20px !important;
                min-height: 55px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
            }}
            [data-testid="stSidebar"] div[role="radiogroup"] label p {{ color: white !important; font-weight: 400 !important; margin-bottom: 0 !important; }}
            [data-testid="stSidebar"] div[data-checked="true"] {{ background: {ORCA_COLOR} !important; border-color: {ORCA_COLOR} !important; }}

            /* Black Font for Main Content Items */
            [data-testid="stMain"] div[role="radiogroup"] label p {{ color: #1a1a1a !important; font-weight: 500 !important; }}

            .card {{ background: white; padding: 35px; border-radius: 24px; border: 1px solid #eef2f6; box-shadow: 0 10px 40px rgba(0,0,0,0.03); margin-bottom: 25px; }}
            
            .logout-btn {{ text-align: center; margin-top: 20px; }}
        </style>
    """, unsafe_allow_html=True)

    # --- INVOICE GENERATOR ---
    def get_bill_html(s, auto_print=False):
        print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
        vat_included = s['total'] * 0.05 / 1.05
        return f"""
        <div style="font-family:'Inter', sans-serif; padding:60px; background:white; color:#1a202c; max-width:850px; margin:auto; border:1px solid #e2e8f0;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid {ORCA_COLOR}; padding-bottom:30px;">
                <div>
                    <h1 style="color:{ORCA_COLOR}; margin:0; font-family:'Cinzel'; letter-spacing:4px; font-size:28px;">ORCA JEWELRY</h1>
                    <p style="margin:5px 0 0 0; font-size:11px; color:#64748b; text-transform:uppercase;">Luxury & Quality Guaranteed</p>
                </div>
                <div style="text-align:right;">
                    <h2 style="margin:0; font-size:16px; color:#1e293b; letter-spacing:1px;">TAX INVOICE</h2>
                    <p style="margin:0; color:#64748b; font-size:12px;">Ref: #ORC-{s['id']}</p>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:40px; margin:50px 0;">
                <div style="background:#f8fafc; padding:20px; border-radius:12px;">
                    <p style="font-size:10px; color:#94a3b8; text-transform:uppercase; font-weight:700; margin-bottom:8px;">Customer Details</p>
                    <p style="margin:0; font-weight:600; font-size:17px;">{s['customer']}</p>
                    <p style="margin:3px 0 0 0; color:#64748b; font-size:14px;">{s['phone']}</p>
                </div>
                <div style="text-align:right; padding:20px;">
                    <p style="font-size:10px; color:#94a3b8; text-transform:uppercase; font-weight:700; margin-bottom:8px;">Date</p>
                    <p style="margin:0; font-weight:600; font-size:17px;">{s['date']}</p>
                </div>
            </div>
            <table style="width:100%; border-collapse:collapse;">
                <thead><tr style="border-bottom:1px solid #edf2f7;"><th style="padding:15px 0; text-align:left;">DESCRIPTION</th><th style="padding:15px 0; text-align:right;">AMOUNT</th></tr></thead>
                <tbody><tr><td style="padding:30px 0;">{s['item']}</td><td style="padding:30px 0; text-align:right;">{s['total']:.3f} OMR</td></tr></tbody>
            </table>
            <div style="margin-top:30px; display:flex; justify-content:flex-end;">
                <div style="width:280px; background:#f8fafc; padding:20px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-top:1px solid #e2e8f0; font-weight:700; font-size:20px; color:{ORCA_COLOR};">
                        <span>Balance:</span><span>{s['balance']:.3f}</span>
                    </div>
                </div>
            </div>
        </div>{print_trigger}"""

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"""
            <div class="logo-section">
                <h1 class="logo-text">ORCA Jewelry</h1>
                <div class="logo-subtext">Luqman Al Hoti</div>
            </div>
        """, unsafe_allow_html=True)
        
        menu = st.radio("NAV", ["Dashboard", "Inventory", "New Invoice", "History", "Customers"], label_visibility="collapsed")
        
        st.divider()
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.rerun()

    # --- APP MODULES ---
    if menu == "Dashboard":
        st.title("Business Intelligence")
        c1, c2, c3 = st.columns(3)
        if db_sales:
            df_sales = pd.DataFrame(db_sales)
            with c1: st.metric("Total Revenue", f"{df_sales['total'].sum():.3f} OMR")
            with c2: st.metric("Sales Volume", len(df_sales))
        else:
            with c1: st.metric("Total Revenue", "0.000 OMR")
            with c2: st.metric("Sales Volume", "0")
        with c3: st.metric("Vault Stock", sum(i["quantity"] for i in db_stock))
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if db_sales:
            df_sales['date'] = pd.to_datetime(df_sales['date'])
            daily = df_sales.groupby('date')['total'].sum().reset_index()
            fig = px.area(daily, x='date', y='total', color_discrete_sequence=[ORCA_COLOR])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "New Invoice":
        st.title("Bespoke Invoice")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        p_col1, p_col2 = st.columns(2)
        with p_col1: phone = st.text_input("Customer Phone")
        with p_col2: name = st.text_input("Customer Name", value=db_cust.get(phone, {}).get("name", ""))
        st.divider()
        inv_mode = st.radio("Item Source", ["Ready Stock", "Manufacturing"], horizontal=True)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if inv_mode == "Ready Stock":
                options = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
                choice = st.selectbox("Select Product", options) if options else st.error("Out of stock")
                price = st.number_input("Retail Price", value=next(i['price'] for i in db_stock if i['serial'] == choice.split(" - ")[0]) if options else 0.0, format="%.3f")
            else:
                item_name = st.text_input("Manufacturing Title")
                price = st.number_input("Agreed Price", format="%.3f")
        with m_col2:
            disc = st.number_input("Discount", format="%.3f")
            paid = st.number_input("Advance", format="%.3f")
        desc = st.text_area("Description (Weight, Karat, Details)", height=100)
        total = price - disc
        if st.button("Confirm & Print"):
            db_cust[phone] = {"name": name}
            save_json(CUSTOMER_DB, db_cust)
            sale = {"id": len(db_sales)+1, "date": datetime.now().strftime("%Y-%m-%d"), "customer": name, "phone": phone, "item": desc, "total": total, "advance": paid, "balance": total-paid}
            db_sales.append(sale)
            save_json(SALES_DB, db_sales)
            if inv_mode == "Ready Stock" and options:
                s_id = choice.split(" - ")[0]
                for i in db_stock:
                    if i['serial'] == s_id: i['quantity'] -= 1
                save_json(INVENTORY_DB, db_stock)
            components.html(get_bill_html(sale, True), height=900, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Inventory":
        st.title("Vault Collection")
        with st.expander("+ Log New Item"):
            with st.form("stock_form", clear_on_submit=True):
                n = st.text_input("Item Name")
                p = st.number_input("Unit Price", format="%.3f")
                q = st.number_input("Quantity", min_value=1)
                if st.form_submit_button("Add to Vault"):
                    db_stock.append({"serial": f"ORC-{random.randint(1000,9999)}", "name": n, "price": p, "quantity": q})
                    save_json(INVENTORY_DB, db_stock)
                    st.rerun()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.table(db_stock)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "History":
        st.title("Sales Ledger")
        if db_sales:
            df = pd.DataFrame(db_sales)
            st.dataframe(df, use_container_width=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            target = st.selectbox("Select Invoice", df['id'].tolist())
            idx = next(i for i, s in enumerate(db_sales) if s['id'] == target)
            up_val = st.number_input("Update Payment", format="%.3f")
            if st.button("Update Ledger"):
                db_sales[idx]['advance'] += up_val
                db_sales[idx]['balance'] -= up_val
                save_json(SALES_DB, db_sales)
                st.rerun()
            if st.button("Print Receipt"):
                components.html(get_bill_html(db_sales[idx], True), height=900, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Customers":
        st.title("Client Directory")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        query = st.text_input("Search...").lower()
        if db_cust:
            res = [{"Phone": k, "Client Name": v['name']} for k, v in db_cust.items() if query in k or query in v['name'].lower()]
            st.table(res)
        st.markdown('</div>', unsafe_allow_html=True)

