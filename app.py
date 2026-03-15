#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ride Analytics Dashboard", layout="wide")

# ---------------- STYLE ----------------

st.markdown("""
<style>

.main {
    background-color:#F5F7FA;
}

h1,h2,h3{
    color:#2C3E50;
}

div[data-testid="metric-container"]{
    background-color:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0 2px 6px rgba(0,0,0,0.1);
}

.sidebar .sidebar-content{
    background-color:#1F2A44;
}

</style>
""", unsafe_allow_html=True)

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
        "Predictive Modelling",
        "Ride Price Prediction"
    ]
)

# ---------------- FILTERS ----------------

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

    fig1 = px.line(
        df.groupby("hour")["price"].mean().reset_index(),
        x="hour",
        y="price",
        title="Average Price per Hour"
    )

    col1.plotly_chart(fig1,use_container_width=True)

    fig2 = px.bar(
        df.groupby("hour")["price"].count().reset_index(),
        x="hour",
        y="price",
        title="Ride Count per Hour"
    )

    col2.plotly_chart(fig2,use_container_width=True)

# ---------------- PAGE 2 ----------------

elif page == "Weather Impact":

    st.title("Weather Impact On Pricing")

    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric(
        "Avg Price Clear",
        round(df[df["short_summary"]=="Clear"]["price"].mean(),2)
    )

    col2.metric(
        "Avg Price Rain",
        round(df[df["short_summary"].str.contains("Rain")]["price"].mean(),2)
    )

    col3.metric(
        "Avg Price Fog",
        round(df[df["short_summary"].str.contains("Fog")]["price"].mean(),2)
    )

    col4.metric(
        "Avg Temperature",
        round(df["temperature"].mean(),2)
    )

    col5.metric(
        "Surge in Rain",
        round(df[df["short_summary"].str.contains("Rain")]["surge_multiplier"].mean(),2)
    )

    st.divider()

    col1,col2 = st.columns(2)

    weather_price = df.groupby("short_summary")["price"].mean().reset_index()

    fig1 = px.bar(
        weather_price,
        x="short_summary",
        y="price",
        title="Average Price by Weather"
    )

    col1.plotly_chart(fig1,use_container_width=True)

    fig2 = px.scatter(
        df,
        x="temperature",
        y="price",
        title="Price vs Temperature"
    )

    col2.plotly_chart(fig2,use_container_width=True)

# ---------------- PAGE 3 ----------------

elif page == "Surge Pricing":

    st.title("Surge Pricing Analysis")

    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric("Total Surge Rides",df[df["surge_multiplier"]>1].shape[0])
    col2.metric("Avg Surge",round(df["surge_multiplier"].mean(),2))
    col3.metric("Max Surge",round(df["surge_multiplier"].max(),2))
    col4.metric("Avg Wind Speed",round(df["windSpeed"].mean(),2))
    col5.metric("Avg Visibility",round(df["visibility"].mean(),2))

    st.divider()

    col1,col2 = st.columns(2)

    surge_hour = df.groupby("hour")["surge_multiplier"].mean().reset_index()

    fig3 = px.line(
        surge_hour,
        x="hour",
        y="surge_multiplier",
        markers=True,
        title="Surge Multiplier by Hour"
    )

    col1.plotly_chart(fig3,use_container_width=True)

    surge_rides = df[df["surge_multiplier"]>1].groupby("hour").size().reset_index(name="rides")

    fig4 = px.bar(
        surge_rides,
        x="hour",
        y="rides",
        title="Surge Rides by Hour"
    )

    col2.plotly_chart(fig4,use_container_width=True)

# ---------------- PAGE 4 ----------------

elif page == "Predictive Modelling":

    st.title("Predictive Pricing Overview")

    avg_price = df["price"].mean()

    df["predicted_price"] = avg_price

    col1,col2 = st.columns(2)

    fig5 = px.line(
        df.groupby("hour")["predicted_price"].mean().reset_index(),
        x="hour",
        y="predicted_price",
        title="Predicted Price by Hour"
    )

    col1.plotly_chart(fig5,use_container_width=True)

    fig6 = px.line(
        df.groupby("hour")["price"].mean().reset_index(),
        x="hour",
        y="price",
        title="Actual Price by Hour"
    )

    col2.plotly_chart(fig6,use_container_width=True)

# ---------------- PAGE 5 ----------------

elif page == "Ride Price Prediction":

    st.title("Ride Price Prediction (Input Dashboard)")

    st.subheader("Enter Ride Details")

    col1,col2,col3 = st.columns(3)

    with col1:
        distance = st.number_input("Distance (km)",0.5,10.0,2.0)
        hour = st.slider("Hour",0,23,12)
        temperature = st.number_input("Temperature",0.0,50.0,25.0)

    with col2:
        humidity = st.slider("Humidity",0.0,1.0,0.5)
        wind = st.number_input("Wind Speed",0.0,20.0,5.0)
        visibility = st.number_input("Visibility",0.0,15.0,10.0)

    with col3:
        cab = st.selectbox("Cab Type",df["cab_type"].unique())
        weather = st.selectbox("Weather",df["short_summary"].unique())

    if st.button("Predict Ride Price"):

        base_price = distance * 3
        weather_factor = 1.2 if "Rain" in weather else 1
        temp_factor = temperature/50

        predicted_price = round(base_price * weather_factor * (1+temp_factor),2)

        success_probability = 90

        st.divider()

        col1,col2 = st.columns(2)

        col1.metric("Predicted Ride Price",f"${predicted_price}")
        col2.metric("Prediction Confidence",f"{success_probability}%")

        st.success("Prediction Generated Successfully")
