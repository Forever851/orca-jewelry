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

# --- 2. MODERN THEME & UI STYLING ---
st.set_page_config(page_title="ORCA Jewelry | Management", layout="wide")

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            background-color: #fcfdfd;
        }}

        /* Sidebar Customization */
        [data-testid="stSidebar"] {{
            background-image: linear-gradient(180deg, #007d75 0%, {ORCA_COLOR} 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
            min-width: 280px !important;
        }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        
        .nav-logo-container {{
            padding: 2.5rem 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 1.5rem;
        }}

        /* Modern Card Styling */
        .card {{
            background: white;
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid #eef2f6;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
            margin-bottom: 1.5rem;
        }}

        /* Metric Styling */
        [data-testid="stMetricValue"] {{
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            color: {ORCA_COLOR} !important;
        }}
        
        h1, h2, h3 {{
            color: #1e293b;
            font-weight: 600 !important;
            margin-bottom: 1rem !important;
        }}

        /* Refined Buttons */
        .stButton>button {{
            background-color: {ORCA_COLOR} !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.6rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            width: 100%;
        }}
        .stButton>button:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 168, 158, 0.25);
        }}

        /* Dataframes & Tables */
        [data-testid="stTable"], .stDataFrame {{
            background: white;
            border-radius: 12px;
            padding: 10px;
            border: 1px solid #eef2f6;
        }}

        /* Footer Overlay */
        .footer-text {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            color: rgba(255,255,255,0.5);
            font-size: 0.7rem;
            letter-spacing: 2px;
            z-index: 100;
            text-transform: uppercase;
        }}
    </style>
    <div class="footer-text">© All copyrights for Luqman Al Hoti</div>
""", unsafe_allow_html=True)

# --- 3. PRINT TEMPLATE (BOUTIQUE LUXURY) ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    vat_included = s['total'] * 0.05 / 1.05
    return f"""
    <div style="font-family:'Inter', sans-serif; padding:50px; background:white; color:#1a202c; max-width:850px; margin:auto; border:1px solid #e2e8f0;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid {ORCA_COLOR}; padding-bottom:30px;">
            <div style="text-align:left;">
                <h1 style="color:{ORCA_COLOR}; margin:0; letter-spacing:5px; font-size:32px;">ORCA</h1>
                <p style="margin:5px 0 0 0; font-size:12px; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Luxury Jewelry & Manufacturing</p>
            </div>
            <div style="text-align:right;">
                <h3 style="margin:0; color:#1e293b; letter-spacing:1px;">TAX INVOICE</h3>
                <p style="margin:0; color:#64748b; font-size:14px;">#ORC-{s['id']}</p>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:40px; margin:40px 0;">
            <div style="background:#f8fafc; padding:25px; border-radius:12px;">
                <p style="font-size:11px; color:#94a3b8; margin:0 0 8px 0; text-transform:uppercase; font-weight:700;">Customer Details</p>
                <p style="margin:0; font-weight:600; font-size:18px;">{s['customer']}</p>
                <p style="margin:5px 0 0 0; font-size:14px; color:#475569;">Ph: {s['phone']}</p>
            </div>
            <div style="text-align:right; padding:25px;">
                <p style="font-size:11px; color:#94a3b8; margin:0 0 8px 0; text-transform:uppercase; font-weight:700;">Transaction Date</p>
                <p style="margin:0; font-weight:600; font-size:18px;">{s['date']}</p>
                <p style="margin:5px 0 0 0; font-size:14px; color:#475569;">Muscat, Sultanate of Oman</p>
            </div>
        </div>

        <table style="width:100%; border-collapse:collapse; margin-bottom:40px;">
            <thead>
                <tr style="border-bottom:2px solid #f1f5f9;">
                    <th style="padding:15px 0; text-align:left; color:#94a3b8; font-size:12px; text-transform:uppercase;">Item Description</th>
                    <th style="padding:15px 0; text-align:right; color:#94a3b8; font-size:12px; text-transform:uppercase;">Amount (OMR)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding:30px 0; border-bottom:1px solid #f1f5f9;">
                        <p style="margin:0; font-weight:600; font-size:16px; color:#0f172a;">Fine Jewelry Piece</p>
                        <p style="margin:8px 0 0 0; font-size:14px; color:#64748b; line-height:1.6; white-space: pre-wrap;">{s['item']}</p>
                    </td>
                    <td style="padding:30px 0; text-align:right; border-bottom:1px solid #f1f5f9; font-weight:600; font-size:16px;">{s['total']:.3f}</td>
                </tr>
            </tbody>
        </table>

        <div style="display:flex; justify-content:flex-end; margin-top:20px;">
            <div style="width:320px; background:#f8fafc; padding:20px; border-radius:12px;">
                <div style="display:flex; justify-content:space-between; padding:8px 0; color:#64748b; font-size:14px;">
                    <span>VAT (5% Included):</span>
                    <span>{vat_included:.3f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:8px 0; color:#64748b; font-size:14px;">
                    <span>Paid Advance:</span>
                    <span>{s['advance']:.3f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:15px 0 5px 0; border-top:2px solid {ORCA_COLOR}; margin-top:10px; font-weight:700; font-size:22px; color:{ORCA_COLOR};">
                    <span>Balance Due:</span>
                    <span>{s['balance']:.3f}</span>
                </div>
            </div>
        </div>

        <div style="margin-top:80px; border-top:1px solid #e2e8f0; padding-top:25px; text-align:center;">
            <p style="font-size:12px; color:#94a3b8; line-height:1.5;">This is a computer-generated invoice. <br> Thank you for your business at ORCA Jewelry.</p>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="nav-logo-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=160)
    except:
        st.markdown("<h1 style='color:white; letter-spacing:3px;'>ORCA</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    menu = st.radio("MAIN NAVIGATION", ["Dashboard", "Inventory / Stock", "Invoice", "Sales History", "Customer Directory"])

# --- 5. APP MODULES ---

if menu == "Dashboard":
    st.title("Business Insights")
    
    # Statistics Grid
    c1, c2, c3 = st.columns(3)
    if db_sales:
        df_sales = pd.DataFrame(db_sales)
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        with c1: st.metric("Total Sales Revenue", f"{df_sales['total'].sum():.3f} OMR")
        with c2: st.metric("Daily Invoices", len(df_sales[df_sales["date"].dt.date == datetime.now().date()]))
    else:
        with c1: st.metric("Total Sales Revenue", "0.000 OMR")
        with c2: st.metric("Daily Invoices", "0")
    
    with c3: st.metric("Stock Units", sum(i["quantity"] for i in db_stock))

    # Graphs Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Performance Analytics")
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        if db_sales:
            st.markdown("**Revenue Trends**")
            daily_rev = df_sales.groupby('date')['total'].sum().reset_index()
            fig_rev = px.area(daily_rev, x='date', y='total', color_discrete_sequence=[ORCA_COLOR])
            fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rev, use_container_width=True)
        else: st.info("Awaiting sales data...")

    with g_col2:
        if db_stock:
            st.markdown("**Stock Allocation**")
            df_st = pd.DataFrame(db_stock)
            fig_stock = px.pie(df_st, names='name', values='quantity', hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_stock, use_container_width=True)
        else: st.info("Awaiting inventory data...")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Invoice":
    st.title("Create Tax Invoice")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        phone = st.text_input("Customer Phone Number")
    with col_cust2:
        name = st.text_input("Customer Name", value=db_cust.get(phone, {}).get("name", ""))
    
    st.divider()
    invoice_type = st.radio("Source of Item:", ["Existing Stock Item", "New Manufacturing"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if invoice_type == "Existing Stock Item":
            item_options = [f"{i['serial']} - {i['name']}" for i in db_stock if i['quantity'] > 0]
            selected_item = st.selectbox("Select Product", item_options) if item_options else st.error("No items in stock")
            item_price = next(i['price'] for i in db_stock if i['serial'] == selected_item.split(" - ")[0]) if item_options else 0.0
            price = st.number_input("Retail Price (Inc. VAT)", value=item_price, format="%.3f")
        else:
            item_name = st.text_input("Custom Design Name")
            price = st.number_input("Quoted Price (Inc. VAT)", format="%.3f")
    
    with col2:
        discount = st.number_input("Seasonal Discount (OMR)", format="%.3f")
        paid = st.number_input("Advance Payment (OMR)", format="%.3f")
    
    desc = st.text_area("Detailed Item Description", height=100, placeholder="Enter gold karat, weight, or special design notes...")
    final_total = price - discount

    if st.button("Generate & Print Invoice"):
        if not phone or not name:
            st.warning("Please enter customer details.")
        else:
            db_cust[phone] = {"name": name}
            save_json(CUSTOMER_DB, db_cust)
            
            sale = {"id": len(db_sales)+1, "date": datetime.now().strftime("%Y-%m-%d"), "customer": name, "phone": phone, "item": desc, "total": final_total, "advance": paid, "balance": final_total-paid}
            db_sales.append(sale)
            save_json(SALES_DB, db_sales)
            
            if invoice_type == "Existing Stock Item" and item_options:
                s_id = selected_item.split(" - ")[0]
                for i in db_stock:
                    if i['serial'] == s_id: i['quantity'] -= 1
                save_json(INVENTORY_DB, db_stock)
                
            components.html(get_bill_html(sale, True), height=800, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Inventory / Stock":
    st.title("Inventory Management")
    
    with st.expander("+ Add New Stock Entry", expanded=False):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("inv_form", clear_on_submit=True):
            fn = st.text_input("Product Name")
            fp = st.number_input("Unit Price (Inc. VAT)", format="%.3f")
            fq = st.number_input("Initial Quantity", min_value=1)
            if st.form_submit_button("Confirm Addition"):
                db_stock.append({"serial": f"ORC-{random.randint(1000,9999)}", "name": fn, "price": fp, "quantity": fq})
                save_json(INVENTORY_DB, db_stock)
                st.success("Item added to vault.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if db_stock:
        st.table(pd.DataFrame(db_stock))
    else:
        st.info("Vault is currently empty.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Sales History":
    st.title("Transaction History")
    if db_sales:
        df_h = pd.DataFrame(db_sales)
        st.dataframe(df_h, use_container_width=True)
        
        st.markdown('<div class="card"><h3>Update Payments & Reprints</h3>', unsafe_allow_html=True)
        target = st.selectbox("Select Invoice Reference", df_h['id'].tolist())
        idx = next(i for i, s in enumerate(db_sales) if s['id'] == target)
        
        up_val = st.number_input("Additional Payment Received", format="%.3f")
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            if st.button("Record Payment"):
                db_sales[idx]['advance'] += up_val
                db_sales[idx]['balance'] -= up_val
                save_json(SALES_DB, db_sales)
                st.success("Balance Updated.")
                st.rerun()
        with col_up2:
            if st.button("Regenerate Invoice"):
                components.html(get_bill_html(db_sales[idx], True), height=800, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Customer Directory":
    st.title("Client Relationship Manager")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    search = st.text_input("🔍 Search clients by name or phone...").lower()
    if db_cust:
        list_c = [{"Phone": k, "Name": v['name']} for k, v in db_cust.items() if search in k or search in v['name'].lower()]
        st.table(list_c)
    st.markdown('</div>', unsafe_allow_html=True)