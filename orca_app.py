import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. LOGIN SYSTEM ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("""
            <style>
            .login-container {
                max-width: 400px; margin: 100px auto; padding: 30px;
                background: white; border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border: 1px solid #e2e8f0; text-align: center;
            }
            .stButton>button { background-color: #00A89E; color: white; width: 100%; }
            </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown("<h2 style='color: #00A89E;'>💎 GemPortal Login</h2>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sign In"):
                if u == "admin" and p == "orca123":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 2. THEME & STYLING ---
def apply_custom_style():
    st.markdown("""
        <style>
        /* Main background */
        .stApp { background-color: #f8fafc; }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
        [data-testid="stSidebar"] * { color: white; }
        
        /* Card styling */
        .custom-card {
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px; border: 1px solid #e2e8f0;
        }
        
        /* Titles & Text */
        h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', sans-serif; }
        .price-text { font-weight: bold; color: #1e293b; font-size: 1.1rem; }
        .badge-stock {
            padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;
            background: #e0f2f1; color: #008f86; font-weight: 600;
        }
        
        /* Button styling */
        .stButton>button {
            background: #00A89E; color: white; border-radius: 6px;
            border: none; padding: 0.5rem 1rem; font-weight: 600;
        }
        .stButton>button:hover { background: #008f86; color: white; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
DB_PATH = "orca_jewelry_db.json"
ORCA_COLOR = "#00A89E"

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as f: json.dump({"stock": [], "sales": []}, f)
    with open(DB_PATH, 'r') as f:
        data = json.load(f)
        for s in data.get("sales", []):
            s.setdefault("balance", 0.0)
            s.setdefault("status", "Completed")
        return data

def save_db(data):
    with open(DB_PATH, 'w') as f: json.dump(data, f, indent=4)

# --- 4. APP START ---
st.set_page_config(page_title="GemPortal | Management", layout="wide")

if check_password():
    apply_custom_style()
    db = load_db()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("<h2 style='color: #00A89E; letter-spacing: 2px;'>💎 GemPortal</h2>", unsafe_allow_html=True)
        menu = st.radio("MAIN MENU", ["Dashboard", "Inventory / Stock", "New Invoice", "Sales History"])
        st.divider()
        if st.button("Log Out"):
            del st.session_state["password_correct"]
            st.rerun()

    # DASHBOARD
    if menu == "Dashboard":
        st.title("Stock Overview")
        
        # Stats Grid
        c1, c2, c3 = st.columns(3)
        with c1:
            val = sum(i['price'] * i['quantity'] for i in db['stock'])
            st.markdown(f'<div class="custom-card"><small>Total Stock Value</small><h2>{val:,.3f} OMR</h2></div>', unsafe_allow_html=True)
        with c2:
            count = sum(i['quantity'] for i in db['stock'])
            st.markdown(f'<div class="custom-card"><small>Inventory Units</small><h2>{count} Units</h2></div>', unsafe_allow_html=True)
        with c3:
            sales = len(db['sales'])
            st.markdown(f'<div class="custom-card"><small>Total Invoices</small><h2>{sales}</h2></div>', unsafe_allow_html=True)

        # Recent Inventory Table
        st.markdown('<div class="custom-card"><h3>Recent Inventory</h3>', unsafe_allow_html=True)
        if db['stock']:
            df_stock = pd.DataFrame(db['stock'])
            st.table(df_stock)
        else:
            st.info("No items in stock.")
        st.markdown('</div>', unsafe_allow_html=True)

    # NEW INVOICE
    elif menu == "New Invoice":
        st.title("Create New Invoice")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cust = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
        with col2:
            item = st.text_input("Item Description")
            total = st.number_input("Final Amount (OMR)", format="%.3f")
        
        paid = st.number_input("Amount Paid Now", format="%.3f")
        
        if st.button("Confirm & Print Invoice"):
            new_id = len(db['sales']) + 1
            sale_data = {
                "id": new_id, "date": datetime.now().strftime("%Y-%m-%d"),
                "customer": cust, "phone": phone, "item": item,
                "total": total, "advance": paid, "balance": total - paid,
                "gender": "N/A", "status": "Pending" if total-paid > 0 else "Completed"
            }
            db['sales'].append(sale_data)
            save_db(db)
            
            # Use your custom HTML template for the actual print
            from orca_app import get_bill_html # Assume helper function is available or paste here
            st.success("Invoice Generated!")
        st.markdown('</div>', unsafe_allow_html=True)

    # SALES HISTORY
    elif menu == "Sales History":
        st.title("Sales History")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        if db['sales']:
            df_sales = pd.DataFrame(db['sales'])
            st.dataframe(df_sales[['id', 'date', 'customer', 'total', 'balance', 'status']], use_container_width=True)
        else:
            st.write("No transactions found.")
        st.markdown('</div>', unsafe_allow_html=True)

    # INVENTORY
    elif menu == "Inventory / Stock":
        st.title("Inventory Management")
        with st.expander("+ Add New Item"):
            with st.form("add_form"):
                n = st.text_input("Item Name")
                p = st.number_input("Price", format="%.3f")
                q = st.number_input("Qty", min_value=1)
                if st.form_submit_button("Save Item"):
                    db['stock'].append({"name": n, "price": p, "quantity": q})
                    save_db(db)
                    st.rerun()
        st.table(db['stock'])