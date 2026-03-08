import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. LOGIN SYSTEM ---
def login_screen():
    st.markdown("""
        <style>
        .login-box {
            max-width: 400px; margin: auto; padding: 2rem;
            background: white; border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<h1 style='text-align:center; color:#00A89E;'>ORCA LOGIN</h1>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            # CHANGE YOUR CREDENTIALS HERE
            if user == "admin" and pw == "orca123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop() # Stops the rest of the app from running until login

# --- 2. MAIN APP CODE (Only runs after login) ---
DB_PATH = "orca_jewelry_db.json" # Simplified path for online hosting
ORCA_COLOR = "#00A89E"
SHOP_DETAILS = {"name": "ORCA JEWELRY", "phone": "+968 1234 5678", "address": "Muscat, Oman"}

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as f: json.dump({"stock": [], "sales": []}, f)
    with open(DB_PATH, 'r') as f:
        data = json.load(f)
        return data

def save_db(data):
    with open(DB_PATH, 'w') as f: json.dump(data, f, indent=4)

db = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- A4 PRINT TEMPLATE ---
def get_bill_html(s, auto_print=False):
    print_trigger = "<script>window.onload = function() { window.print(); }</script>" if auto_print else ""
    return f"""
    <div style="font-family:Arial; padding:40px; border:1px solid #EEE;">
        <h1 style="color:{ORCA_COLOR}; text-align:center;">{SHOP_DETAILS['name']}</h1>
        <p style="text-align:center;">{SHOP_DETAILS['address']} | {SHOP_DETAILS['phone']}</p>
        <hr>
        <p><b>Customer:</b> {s['customer']} | <b>Date:</b> {s['date']}</p>
        <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <tr style="background:#F4F4F4;"><th>Item</th><th style="text-align:right;">Total</th></tr>
            <tr><td>{s['item']}</td><td style="text-align:right;">{s['total']:.3f} OMR</td></tr>
        </table>
        <div style="text-align:right;">
            <p>Paid: {s['advance']:.3f} OMR</p>
            <h3 style="color:red;">Balance: {s['balance']:.3f} OMR</h3>
        </div>
    </div>
    {print_trigger}
    """

# --- NAVIGATION ---
st.sidebar.title("ORCA PRO")
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

menu = st.sidebar.radio("Menu", ["Dashboard", "New Invoice", "History"])

if menu == "Dashboard":
    st.title("Business Summary")
    if db['sales']:
        df = pd.DataFrame(db['sales'])
        st.metric("Total Collected", f"{sum(s['advance'] for s in db['sales']):.3f} OMR")
        st.plotly_chart(px.bar(df, x='date', y='advance', color_discrete_sequence=[ORCA_COLOR]))

elif menu == "New Invoice":
    st.subheader("New Sale")
    name = st.text_input("Customer Name")
    item = st.text_input("Item Name")
    total = st.number_input("Total Price", format="%.3f")
    paid = st.number_input("Paid Now", format="%.3f")
    
    if st.button("Confirm & Print"):
        new_id = len(db['sales']) + 1
        new_sale = {"id": new_id, "date": today_str, "customer": name, "item": item, "total": total, "advance": paid, "balance": total-paid}
        db['sales'].append(new_sale)
        save_db(db)
        components.html(get_bill_html(new_sale, auto_print=True), height=500)

elif menu == "History":
    st.subheader("Sales History")
    if db['sales']:
        st.table(pd.DataFrame(db['sales']))