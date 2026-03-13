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
    df = pd.read_csv("new_rider_share10.csv")
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

    st.title("Weather Impact On Pricing")

    # KPIs
    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric("Avg Price Clear Weather",
                round(df[df["short_summary"]=="Clear"]["price"].mean(),2))

    col2.metric("Avg Price Rainy Weather",
                round(df[df["short_summary"].str.contains("Rain")]["price"].mean(),2))

    col3.metric("Avg Price Foggy Weather",
                round(df[df["short_summary"].str.contains("Fog")]["price"].mean(),2))

    col4.metric("Average Temperature",
                round(df["temperature"].mean(),2))

    col5.metric("Average Surge Rate in Rain",
                round(df[df["short_summary"].str.contains("Rain")]["surge_multiplier"].mean(),2))

    st.divider()

    # CHARTS
    col1,col2 = st.columns(2)

    # Avg price by weather
    weather_price = df.groupby("short_summary")["price"].mean().reset_index()

    fig1 = px.bar(
        weather_price,
        x="short_summary",
        y="price",
        title="Average Price by Weather",
        color="price"
    )

    col1.plotly_chart(fig1, use_container_width=True)

    # Price vs temperature
    fig2 = px.scatter(
        df,
        x="temperature",
        y="price",
        title="Average Price by Temperature"
    )

    col2.plotly_chart(fig2, use_container_width=True)

    col3,col4 = st.columns(2)

    # Price vs visibility
    fig3 = px.scatter(
        df,
        x="visibility",
        y="price",
        title="Average Price by Visibility"
    )

    col3.plotly_chart(fig3, use_container_width=True)

    # Surge % by weather
    surge_weather = df.groupby("short_summary")["surge_multiplier"].mean().reset_index()

    fig4 = px.bar(
        surge_weather,
        x="short_summary",
        y="surge_multiplier",
        title="Surge % by Weather"
    )

    col4.plotly_chart(fig4, use_container_width=True)



# ---------------- PAGE 3 ----------------

elif page == "Surge Pricing":

    st.title("Surge Pricing And Routes")

    # KPIs
    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric("Total Surge Rides",
                df[df["surge_multiplier"]>1].shape[0])

    col2.metric("Average Surge Multiplier",
                round(df["surge_multiplier"].mean(),2))

    col3.metric("Maximum Surge Multiplier",
                round(df["surge_multiplier"].max(),2))

    col4.metric("Average Wind Speed",
                round(df["windSpeed"].mean(),2))

    col5.metric("Average Visibility",
                round(df["visibility"].mean(),2))

    st.divider()

    # CHARTS
    col1,col2 = st.columns(2)

    # Avg surge by hour
    surge_hour = df.groupby("hour")["surge_multiplier"].mean().reset_index()

    fig5 = px.line(
        surge_hour,
        x="hour",
        y="surge_multiplier",
        title="Average Surge Multiplier by Hour",
        markers=True
    )

    col1.plotly_chart(fig5, use_container_width=True)

    # Surge rides by hour
    surge_rides = df[df["surge_multiplier"]>1].groupby("hour").size().reset_index(name="rides")

    fig6 = px.bar(
        surge_rides,
        x="hour",
        y="rides",
        title="Surge Rides by Hour"
    )

    col2.plotly_chart(fig6, use_container_width=True)

    col3,col4 = st.columns(2)

    # Surge % by weather
    surge_weather = df.groupby("short_summary")["surge_multiplier"].mean().reset_index()

    fig7 = px.bar(
        surge_weather,
        x="short_summary",
        y="surge_multiplier",
        title="Surge % by Weather"
    )

    col3.plotly_chart(fig7, use_container_width=True)

    # Price vs distance
    fig8 = px.scatter(
        df,
        x="distance",
        y="price",
        title="Average Price by Distance"
    )

    col4.plotly_chart(fig8, use_container_width=True)
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

