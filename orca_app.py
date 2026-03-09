import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
from PIL import Image

# --- 1. CONFIG & DB ENGINE ---
# Split databases for better organization
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

# Load all databases
db_sales = load_json(SALES_DB, [])
db_stock = load_json(INVENTORY_DB, [])
db_cust = load_json(CUSTOMER_DB, {}) # {phone: {name: x, gender: y}}

st.set_page_config(page_title="ORCA Jewelry Management", layout="wide", page_icon="💎")

# --- 2. CUSTOM STYLING (GemPortal Nav Style) ---
st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{ background-color: #1e293b !important; width: 300px !important; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        .stApp {{ background-color: #f8fafc; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        .stButton>button {{ background: {ORCA_COLOR} !important; color: white !important; border-radius: 6px !important; width: 100%; font-weight: 600; border: none; }}
        .footer-text {{ position: fixed; bottom: 10px; left: 10px; color: #64748b; font-size: 0.8rem; z-index: 100; }}
    </style>
    <div class="footer-text">© All copyrights for Luqman Al Hoti</div>
""", unsafe_allow_html=True)

# --- 3. PRINT TEMPLATE WITH LOGO & VAT ---
def get_bill_html(s, auto_print=False):
    vat_amt = s['total'] * 0.05
    grand_total = s['total'] + vat_amt
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    
    return f"""
    <div style="font-family:sans-serif; padding:30px; border:1px solid #EEE; background:white; max-width:800px; margin:auto;">
        <div style="text-align:center; border-bottom:3px solid {ORCA_COLOR}; padding-bottom:15px;">
            <h1 style="color:{ORCA_COLOR}; margin:0;">ORCA JEWELRY</h1>
            <p>123 Gold Market, Muscat, Oman | +968 1234 5678</p>
            <h2 style="letter-spacing:3px;">TAX INVOICE</h2>
        </div>
        <div style="display:flex; justify-content:space-between; margin:20px 0;">
            <div><p><b>Customer:</b> {s['customer']}</p><p><b>Phone:</b> {s['phone']}</p></div>
            <div style="text-align:right;"><p><b>Invoice:</b> #ORC-{s['id']}</p><p><b>Date:</b> {s['date']}</p></div>
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#F8F9FA;"><th style="padding:10px; border:1px solid #DDD; text-align:left;">Description</th><th style="padding:10px; border:1px solid #DDD; text-align:right;">Total (OMR)</th></tr>
            <tr><td style="padding:15px; border:1px solid #DDD;">{s['item']}</td><td style="padding:15px; border:1px solid #DDD; text-align:right;">{s['total']:.3f}</td></tr>
        </table>
        <div style="text-align:right; margin-top:20px; line-height:1.6;">
            <p>Sub-Total: {s['total']:.3f} OMR</p>
            <p>VAT (5%): {vat_amt:.3f} OMR</p>
            <h3 style="color:{ORCA_COLOR};">Grand Total: {grand_total:.3f} OMR</h3>
            <p style="color:green;">Amount Paid: {s['advance']:.3f} OMR</p>
            <p style="color:red;">Balance: {(grand_total - s['advance']):.3f} OMR</p>
        </div>
    </div>
    {print_trigger}
    """

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    # Display Logo
    try:
        logo = Image.open("logo.jpg")
        st.image(logo, use_container_width=True)
    except:
        st.header("ORCA JEWELRY")
    
    st.markdown("---")
    menu = st.radio("MAIN MENU", ["Dashboard", "Inventory / Stock", "New Invoice", "Sales History", "Customer Directory"])
    st.markdown("---")
    st.write("Logged in as: Admin")

# --- 5. APP MODULES ---

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("Orca Business Intelligence")
    if db_sales:
        df = pd.DataFrame(db_sales)
        df['date'] = pd.to_datetime(df['date'])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Sales (Incl. VAT)", f"{(df['total'].sum() * 1.05):.3f} OMR")
        with c2: st.metric("Cash Collected", f"{df['advance'].sum():.3f} OMR")
        with c3: st.metric("Stock Items", len(db_stock))
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Daily Sales Volume")
            daily = df.groupby('date')['total'].sum().reset_index()
            fig1 = px.area(daily, x='date', y='total', color_discrete_sequence=[ORCA_COLOR])
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            st.subheader("Inventory Status")
            if db_stock:
                stock_df = pd.DataFrame(db_stock)
                fig2 = px.pie(stock_df, names='name', values='quantity', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available to show statistics.")

# --- NEW INVOICE ---
elif menu == "New Invoice":
    st.title("Create New Invoice")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Customer Logic
    phone_input = st.text_input("Enter Phone Number")
    cust_name = ""
    cust_gender = "Female"
    
    if phone_input in db_cust:
        st.success(f"Existing Customer Found: {db_cust[phone_input]['name']}")
        cust_name = db_cust[phone_input]['name']
        cust_gender = db_cust[phone_input]['gender']
    
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Customer Name", value=cust_name)
    with c2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"], index=["Female", "Male", "Other"].index(cust_gender))
    
    # Item Logic
    item_type = st.radio("Item Source", ["Existing Stock", "Custom Manufacturing"], horizontal=True)
    if item_type == "Existing Stock":
        options = [i['name'] for i in db_stock if i['quantity'] > 0]
        item_title = st.selectbox("Select Product", options)
        raw_price = next((i['price'] for i in db_stock if i['name'] == item_title), 0.0)
        desc = st.text_area("Item Details (4 lines)", value=f"Product: {item_title}", height=120)
    else:
        item_title = st.text_input("Item Name")
        raw_price = st.number_input("Item Base Price (OMR)", format="%.3f")
        desc = st.text_area("Manufacturing Specifications (4 lines)", height=120)

    vat = raw_price * 0.05
    grand_total = raw_price + vat
    st.write(f"**Subtotal:** {raw_price:.3f} | **VAT (5%):** {vat:.3f} | **Grand Total:** {grand_total:.3f} OMR")
    
    paid = st.number_input("Payment Received", format="%.3f")
    
    if st.button("Generate Invoice & Save"):
        # Save Customer
        db_cust[phone_input] = {"name": name, "gender": gender}
        save_json(CUSTOMER_DB, db_cust)
        
        # Save Sale
        new_id = len(db_sales) + 1
        sale_data = {
            "id": new_id, "date": datetime.now().strftime("%Y-%m-%d"),
            "customer": name, "phone": phone_input, "item": desc,
            "total": raw_price, "advance": paid, "balance": grand_total - paid
        }
        db_sales.append(sale_data)
        save_json(SALES_DB, db_sales)
        
        # Deduct Stock
        if item_type == "Existing Stock":
            for i in db_stock:
                if i['name'] == item_title: i['quantity'] -= 1
            save_json(INVENTORY_DB, db_stock)
            
        components.html(get_bill_html(sale_data, auto_print=True), height=800, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- INVENTORY ---
elif menu == "Inventory / Stock":
    st.title("Stock Management")
    with st.expander("Add New Inventory Item"):
        with st.form("stock_form"):
            n = st.text_input("Item Name")
            p = st.number_input("Price (OMR)", format="%.3f")
            q = st.number_input("Quantity", min_value=1)
            if st.form_submit_button("Save to Inventory"):
                db_stock.append({"name": n, "price": p, "quantity": q})
                save_json(INVENTORY_DB, db_stock)
                st.rerun()
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Current Stock List")
    st.table(pd.DataFrame(db_stock))
    st.markdown("</div>", unsafe_allow_html=True)

# --- SALES HISTORY ---
elif menu == "Sales History":
    st.title("Transaction History")
    if db_sales:
        df_hist = pd.DataFrame(db_sales)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No sales recorded yet.")

# --- CUSTOMER DIRECTORY ---
elif menu == "Customer Directory":
    st.title("Client List")
    if db_cust:
        cust_list = [{"Phone": k, "Name": v['name'], "Gender": v['gender']} for k, v in db_cust.items()]
        st.table(pd.DataFrame(cust_list))
    else:
        st.info("No customers in database.")