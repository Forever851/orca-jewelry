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

# --- 2. ELITE UI STYLING ---
st.set_page_config(page_title="ORCA | Haute Joaillerie", layout="wide")

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        /* Global Reset */
        .stApp {{
            background-color: #f8fafb;
            font-family: 'Inter', sans-serif;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #072e2b 0%, #001a18 100%) !important;
            box-shadow: 4px 0 15px rgba(0,0,0,0.2);
            min-width: 300px !important;
        }}

        /* CUSTOM LOGO AREA */
        .logo-section {{
            padding: 40px 20px;
            text-align: center;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            margin-bottom: 20px;
        }}
        .logo-text {{
            font-family: 'Cinzel', serif;
            color: {GOLD_ACCENT};
            font-size: 32px;
            letter-spacing: 8px;
            margin: 0;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
        }}
        .logo-subtext {{
            color: white;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 3px;
            opacity: 0.7;
            margin-top: 5px;
        }}

        /* NAVIGATION STYLING */
        /* Hiding the default radio label */
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
            display: none;
        }}
        
        /* Styling the radio buttons as a menu */
        div[role="radiogroup"] {{
            gap: 10px;
            padding: 0 15px;
        }}
        
        div[role="radiogroup"] label {{
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            padding: 12px 20px !important;
            border-radius: 12px !important;
            transition: all 0.4s ease !important;
            color: #ffffff !important;
        }}
        
        div[role="radiogroup"] label:hover {{
            background: rgba(212, 175, 55, 0.1) !important;
            border-color: {GOLD_ACCENT} !important;
            transform: translateX(5px);
        }}
        
        div[data-checked="true"] {{
            background: {ORCA_COLOR} !important;
            border-color: {ORCA_COLOR} !important;
            box-shadow: 0 4px 12px rgba(0, 168, 158, 0.3);
        }}

        /* Cards & Metrics */
        .card {{
            background: white;
            padding: 30px;
            border-radius: 20px;
            border: 1px solid #eef2f6;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02);
            margin-bottom: 25px;
        }}
        
        .stMetric {{
            background: #ffffff;
            border-radius: 15px;
            padding: 15px;
            border-left: 5px solid {ORCA_COLOR};
        }}

        /* Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, {ORCA_COLOR} 0%, #008981 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 12px 25px !important;
            font-weight: 600 !important;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 168, 158, 0.2);
        }}

        /* Footer */
        .footer-credit {{
            position: fixed;
            bottom: 15px;
            left: 30px;
            color: rgba(255,255,255,0.3);
            font-size: 9px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
    </style>
""", unsafe_allow_html=True)

# --- 3. REFINED BILL TEMPLATE ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    vat_included = s['total'] * 0.05 / 1.05
    return f"""
    <div style="font-family:'Inter', sans-serif; padding:60px; background:white; color:#1a202c; max-width:850px; margin:auto; border:1px solid #e2e8f0; position:relative;">
        <div style="position:absolute; top:20px; right:60px; color:{ORCA_COLOR}; font-weight:700; opacity:0.1; font-size:80px; z-index:0;">ORCA</div>
        <div style="position:relative; z-index:1;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #eee; padding-bottom:30px;">
                <div>
                    <h1 style="color:{ORCA_COLOR}; margin:0; font-family:'Cinzel'; letter-spacing:5px;">ORCA</h1>
                    <p style="margin:5px 0 0 0; font-size:10px; color:#64748b; text-transform:uppercase; letter-spacing:2px;">Muscat • Dubai • London</p>
                </div>
                <div style="text-align:right;">
                    <h2 style="margin:0; font-size:18px; color:#1e293b;">INVOICE</h2>
                    <p style="margin:0; color:#64748b; font-size:12px;">Ref: #ORC-{s['id']}</p>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:40px; margin:50px 0;">
                <div>
                    <p style="font-size:10px; color:#94a3b8; text-transform:uppercase; font-weight:700; margin-bottom:10px;">Client Information</p>
                    <p style="margin:0; font-weight:600; font-size:18px;">{s['customer']}</p>
                    <p style="margin:3px 0 0 0; color:#64748b;">{s['phone']}</p>
                </div>
                <div style="text-align:right;">
                    <p style="font-size:10px; color:#94a3b8; text-transform:uppercase; font-weight:700; margin-bottom:10px;">Date of Issue</p>
                    <p style="margin:0; font-weight:600; font-size:18px;">{s['date']}</p>
                </div>
            </div>

            <table style="width:100%; border-collapse:collapse; margin-top:30px;">
                <thead>
                    <tr style="background:#fcfcfc;">
                        <th style="padding:15px; text-align:left; border-bottom:2px solid {ORCA_COLOR}; font-size:12px; color:#64748b;">DESCRIPTION</th>
                        <th style="padding:15px; text-align:right; border-bottom:2px solid {ORCA_COLOR}; font-size:12px; color:#64748b;">TOTAL (OMR)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding:30px 15px; border-bottom:1px solid #f1f5f9;">
                            <span style="font-weight:600; font-size:15px;">Official Jewelry Item</span><br>
                            <small style="color:#64748b; line-height:1.6;">{s['item']}</small>
                        </td>
                        <td style="padding:30px 15px; text-align:right; border-bottom:1px solid #f1f5f9; font-weight:600;">{s['total']:.3f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top:40px; display:flex; justify-content:flex-end;">
                <div style="width:280px;">
                    <div style="display:flex; justify-content:space-between; padding:8px 0; font-size:13px; color:#64748b;">
                        <span>VAT (5% Inc.)</span>
                        <span>{vat_included:.3f}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:8px 0; font-size:13px; color:#64748b;">
                        <span>Paid Deposit</span>
                        <span>{s['advance']:.3f}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:15px 0; margin-top:10px; border-top:1px solid #eee; font-weight:700; font-size:20px; color:{ORCA_COLOR};">
                        <span>Balance Due</span>
                        <span>{s['balance']:.3f}</span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top:100px; text-align:center; border-top:1px solid #eee; padding-top:20px;">
                <p style="font-size:11px; color:#94a3b8;">Authenticity Guaranteed • No returns on custom pieces • ORCA 2024</p>
            </div>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR & NAVIGATION ---
with st.sidebar:
    # Luxury Logo Header
    st.markdown(f"""
        <div class="logo-section">
            <h1 class="logo-text">ORCA</h1>
            <div class="logo-subtext">Haute Joaillerie</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Custom Styled Navigation
    menu = st.radio(
        "NAVIGATION",
        ["Analytics", "Inventory", "New Invoice", "Sales History", "Clients"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="footer-credit">© Luqman Al Hoti</div>', unsafe_allow_html=True)

# --- 5. APPLICATION LOGIC ---

if menu == "Analytics":
    st.title("Business Dashboard")
    c1, c2, c3 = st.columns(3)
    if db_sales:
        df_sales = pd.DataFrame(db_sales)
        with c1: st.metric("Revenue (OMR)", f"{df_sales['total'].sum():.3f}")
        with c2: st.metric("Sales Count", len(df_sales))
    else:
        with c1: st.metric("Revenue (OMR)", "0.000")
        with c2: st.metric("Sales Count", "0")
    with c3: st.metric("Vault Stock", sum(i["quantity"] for i in db_stock))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Performance Trends")
    if db_sales:
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        daily = df_sales.groupby('date')['total'].sum().reset_index()
        fig = px.line(daily, x='date', y='total', color_discrete_sequence=[ORCA_COLOR])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "New Invoice":
    st.title("Bespoke Invoice")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    p_col1, p_col2 = st.columns(2)
    with p_col1: phone = st.text_input("Client Phone")
    with p_col2: name = st.text_input("Client Name", value=db_cust.get(phone, {}).get("name", ""))
    
    st.divider()
    inv_mode = st.radio("Item Selection", ["Ready Stock", "Custom Order"], horizontal=True)
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        if inv_mode == "Ready Stock":
            options = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
            choice = st.selectbox("Search Stock", options) if options else st.error("Out of stock")
            price = st.number_input("Retail Price", value=next(i['price'] for i in db_stock if i['serial'] == choice.split(" - ")[0]) if options else 0.0, format="%.3f")
        else:
            item_name = st.text_input("Custom Design Title")
            price = st.number_input("Quoted Price", format="%.3f")
            
    with m_col2:
        disc = st.number_input("Discount", format="%.3f")
        paid = st.number_input("Deposit Paid", format="%.3f")
        
    desc = st.text_area("Order Details (Karat, Weight, Gemstones)", height=100)
    total = price - disc

    if st.button("Confirm Transaction & Print"):
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
    st.title("The Vault")
    with st.expander("Catalog New Item"):
        with st.form("stock_form", clear_on_submit=True):
            n = st.text_input("Product Title")
            p = st.number_input("Base Price", format="%.3f")
            q = st.number_input("Quantity", min_value=1)
            if st.form_submit_button("Add to Collection"):
                db_stock.append({"serial": f"ORC-{random.randint(1000,9999)}", "name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.rerun()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.table(db_stock)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Sales Records")
    if db_sales:
        df = pd.DataFrame(db_sales)
        st.dataframe(df, use_container_width=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        target = st.selectbox("Select Invoice ID", df['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == target)
        
        up_val = st.number_input("Record Installment Payment", format="%.3f")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Apply Payment"):
                db_sales[idx]['advance'] += up_val
                db_sales[idx]['balance'] -= up_val
                save_json(SALES_DB, db_sales)
                st.rerun()
        with b2:
            if st.button("Reprint Bill"):
                components.html(get_bill_html(db_sales[idx], True), height=900, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Clients":
    st.title("Client Directory")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    query = st.text_input("Search Name or Phone...").lower()
    if db_cust:
        res = [{"Phone": k, "Client Name": v['name']} for k, v in db_cust.items() if query in k or query in v['name'].lower()]
        st.table(res)
    st.markdown('</div>', unsafe_allow_html=True)