import calendar
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import sqlite3

import pickle
from pathlib import Path
import streamlit_authenticator as stauth

import database as db  # local import

# Settings 
incomes = ["Salary", "Business", "Other Income"]
expenses = ["Rent", "Utilities", "Food", "Entertainment", "Other Expenses", "Savings"]
currency = "AED"
page_title = "Welcome to Money Manager"
page_icon = ":money_with_wings:"
layout = "centered"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

# User Authentication
names = ["Aaron Redada", "Bruce Banner"]
usernames = ["ajredada", "bbanner"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "manager_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username or Password is Incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    st.title(page_title + " " + page_icon)
    st.sidebar.success("Select a page above.")
    st.sidebar.title(f"Welcome, {name}")
    authenticator.logout("Logout", "sidebar")

    # Period Selection
    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # Nav Bar
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Plot"],
        icons=["pencil-fill", "bar-chart-fill"],
        orientation="horizontal"
    )

    # Input Values
    if selected == "Data Entry":
        st.header(f"Data Entry in {currency}")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")

            "---"
            with st.expander("Income"):
                for income in incomes:
                    st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
            with st.expander("Comment"):
                comment = st.text_area("", placeholder="Enter a comment here...")

            "---"
            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = f"{st.session_state['year']}_{st.session_state['month']}"
                incomes_data = {income: st.session_state[income] for income in incomes}
                expenses_data = {expense: st.session_state[expense] for expense in expenses}
                db.insert_period(period, incomes_data, expenses_data, comment)
                st.success("Data Saved!")

    # Data visualization
    if selected == "Data Plot":
        st.header("Data Plot")
        with st.form("saved_periods"):
            period = st.selectbox("Select Period:", [p[0] for p in db.fetch_all_periods()])
            submitted = st.form_submit_button("Plot Period")
            if submitted:
                period_data = db.get_period(period)
                comment = period_data.get("comment")
                incomes = period_data.get("incomes")
                expenses = period_data.get("expenses")

                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{total_income} {currency}")
                col2.metric("Total Expense", f"{total_expense} {currency}")
                col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
                st.text(f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)




