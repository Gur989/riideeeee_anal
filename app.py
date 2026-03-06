#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ride Analytics Dashboard", layout="wide")

# ---------------- LOGIN SYSTEM ----------------

if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("Ride Analytics Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
        else:
            st.error("Invalid username or password")

if not st.session_state.login:
    login()
    st.stop()

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    df = pd.read_csv("rides_data.csv")
    return df

df = load_data()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Timing Based Pricing",
        "Weather Impact",
        "Surge Pricing",
        "Predictive Modelling"
    ]
)

st.sidebar.title("Filters")

month = st.sidebar.multiselect("Month", df["month"].unique(), df["month"].unique())
cab = st.sidebar.multiselect("Cab Type", df["cab_type"].unique(), df["cab_type"].unique())

df = df[(df["month"].isin(month)) & (df["cab_type"].isin(cab))]

# ---------------- PAGE 1 ----------------

if page == "Timing Based Pricing":

    st.title("Timing Based Pricing")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Rides", len(df))
    col2.metric("Average Price", round(df["price"].mean(),2))
    col3.metric("Peak Hour", df["hour"].mode()[0])
    col4.metric("Average Distance", round(df["distance"].mean(),2))

    col1,col2 = st.columns(2)

    fig1 = px.line(df.groupby("hour")["price"].mean().reset_index(),
                   x="hour", y="price",
                   title="Average Price per Hour")

    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df.groupby("hour")["price"].count().reset_index(),
                  x="hour", y="price",
                  title="Ride Count per Hour")

    col2.plotly_chart(fig2, use_container_width=True)

# ---------------- PAGE 2 ----------------

elif page == "Weather Impact":

    st.title("Weather Impact on Pricing")

    col1,col2 = st.columns(2)

    fig3 = px.bar(df.groupby("short_summary")["price"].mean().reset_index(),
                  x="short_summary",
                  y="price",
                  title="Average Price by Weather")

    col1.plotly_chart(fig3, use_container_width=True)

    fig4 = px.scatter(df,
                      x="temperature",
                      y="price",
                      title="Price vs Temperature")

    col2.plotly_chart(fig4, use_container_width=True)

# ---------------- PAGE 3 ----------------

elif page == "Surge Pricing":

    st.title("Surge Pricing Analysis")

    col1,col2 = st.columns(2)

    fig5 = px.line(df.groupby("hour")["surge_multiplier"].mean().reset_index(),
                   x="hour",
                   y="surge_multiplier",
                   title="Average Surge by Hour")

    col1.plotly_chart(fig5, use_container_width=True)

    fig6 = px.scatter(df,
                      x="distance",
                      y="price",
                      title="Price vs Distance")

    col2.plotly_chart(fig6, use_container_width=True)

# ---------------- PAGE 4 ----------------

elif page == "Predictive Modelling":

    st.title("Predictive Pricing Overview")

    avg_price = df["price"].mean()

    df["predicted_price"] = avg_price

    col1,col2 = st.columns(2)

    fig7 = px.line(df.groupby("hour")["predicted_price"].mean().reset_index(),
                   x="hour",
                   y="predicted_price",
                   title="Predicted Price by Hour")

    col1.plotly_chart(fig7, use_container_width=True)

    fig8 = px.line(df.groupby("hour")["price"].mean().reset_index(),
                   x="hour",
                   y="price",
                   title="Actual Price by Hour")

    col2.plotly_chart(fig8, use_container_width=True)