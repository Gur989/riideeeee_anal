#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
from sklearn.metrics import r2_score

st.set_page_config(page_title="Rides Analytics", layout="wide")

# ---------------- LIGHT THEME STYLE ----------------
st.markdown("""
<style>

.main {
    background-color:#F5F7FA;
}

/* Text */
h1,h2,h3,h4,label {
    color:#1F2937;
}

/* KPI Cards */
div[data-testid="metric-container"]{
    background-color:#FFFFFF;
    border-radius:12px;
    padding:18px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    color:#111827;
}

/* Sidebar LIGHT */
section[data-testid="stSidebar"]{
    background-color:#FFFFFF;
    border-right:1px solid #E5E7EB;
}

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color:#111827 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER WITH LOGO ----------------
col_logo, col_title = st.columns([1,5])

with col_logo:
    st.image("logo.png", width=120)

with col_title:
    st.markdown("# 🚀 Rides Analytics Dashboard")

st.markdown("---")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
        else:
            st.error("Invalid credentials")

if not st.session_state.login:
    login()
    st.stop()

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("new_rider_share10.csv")
    df["short_summary"] = df["short_summary"].str.strip()
    return df

@st.cache_data
def load_prediction_data():
    with zipfile.ZipFile("predictive_dashboard_datas.zip") as z:
        with z.open(z.namelist()[0]) as f:
            df_pred = pd.read_csv(f)
    return df_pred

df = load_data()
df_pred = load_prediction_data()

# ---------------- SIDEBAR ----------------
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Timing Analysis","Weather Impact","Surge Pricing","Prediction"]
)

st.sidebar.title("Filters")

month = st.sidebar.multiselect("Month", df["month"].unique(), df["month"].unique())
cab = st.sidebar.multiselect("Cab Type", df["cab_type"].unique(), df["cab_type"].unique())

df = df[(df["month"].isin(month)) & (df["cab_type"].isin(cab))]

# ---------------- PAGE 1 ----------------
if page == "Timing Analysis":

    st.subheader("⏱ Ride Pricing by Time")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Rides", len(df))
    col2.metric("Avg Price", round(df["price"].mean(),2))
    col3.metric("Avg Surge", round(df["surge_multiplier"].mean(),2))
    col4.metric("Avg Distance", round(df["distance"].mean(),2))

    col1,col2 = st.columns(2)

   # 1️⃣ Average Price Per Hour
    fig1 = px.line(
        df.groupby("hour")["price"].mean().reset_index(),
        x="hour",
        y="price",
        title="Average Price in Each Hour",
        markers=True
    )
    fig1.update_traces(line_color="#1D4ED8")  # BLUE

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Ride Count Per Hour
    fig2 = px.line(
        df.groupby("hour").size().reset_index(name="rides"),
        x="hour",
        y="rides",
        title="Ride Count Per Hour",
        markers=True
    )
    fig2.update_traces(line_color="#374151")  # DARK GRAY

    col2.plotly_chart(fig2, use_container_width=True)

    # SECOND ROW
    col3, col4 = st.columns(2)

    # 3️⃣ Average Surge Per Hour
    fig3 = px.bar(
        df.groupby("hour")["surge_multiplier"].mean().reset_index(),
        x="hour",
        y="surge_multiplier",
        title="Average Surge in Each Hour"
    )
    fig3.update_traces(marker_color="#1D4ED8")

    col3.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Average Visibility Per Hour
    fig4 = px.bar(
        df.groupby("hour")["visibility"].mean().reset_index(),
        x="hour",
        y="visibility",
        title="Average Visibility in Each Hour"
    )
    fig4.update_traces(marker_color="#374151")

    col4.plotly_chart(fig4, use_container_width=True)

# ---------------- PAGE 2 ----------------
elif page == "Weather Impact":

    st.subheader("🌦 Weather Impact on Pricing")

    # -------- KPI --------
    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric("Clear Weather Price",
                round(df[df["short_summary"]=="Clear"]["price"].mean(),2))

    col2.metric("Rainy Weather Price",
                round(df[df["short_summary"].str.contains("Rain")]["price"].mean(),2))

    col3.metric("Foggy Weather Price",
                round(df[df["short_summary"].str.contains("Fog")]["price"].mean(),2))

    col4.metric("Average Temperature",
                round(df["temperature"].mean(),2))

    col5.metric("Rain Surge Rate",
                round(df[df["short_summary"].str.contains("Rain")]["surge_multiplier"].mean(),2))

    st.markdown("---")

    # -------- CHARTS (ROW 1) --------
    col1, col2 = st.columns(2)

    # 1️⃣ Avg Price by Weather
    fig1 = px.bar(
        df.groupby("short_summary")["price"].mean().reset_index(),
        x="short_summary",
        y="price",
        title="Average Price by Weather"
    )
    fig1.update_traces(marker_color="#1D4ED8")  # BLUE

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Price vs Temperature
    fig2 = px.scatter(
        df,
        x="temperature",
        y="price",
        title="Price vs Temperature"
    )
    fig2.update_traces(marker_color="#374151")  # DARK GRAY

    col2.plotly_chart(fig2, use_container_width=True)

    # -------- CHARTS (ROW 2) --------
    col3, col4 = st.columns(2)

    # 3️⃣ Price vs Visibility
    fig3 = px.scatter(
        df,
        x="visibility",
        y="price",
        title="Price vs Visibility"
    )
    fig3.update_traces(marker_color="#374151")

    col3.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Surge % by Weather
    fig4 = px.bar(
        df.groupby("short_summary")["surge_multiplier"].mean().reset_index(),
        x="short_summary",
        y="surge_multiplier",
        title="Surge % by Weather"
    )
    fig4.update_traces(marker_color="#1D4ED8")

    col4.plotly_chart(fig4, use_container_width=True)
# ---------------- PAGE 3 ----------------
# ---------------- PAGE 3 ----------------
elif page == "Surge Pricing":

    st.subheader("⚡ Surge Pricing and Routes")

    # -------- KPI --------
    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("Total Surge Rides", df[df["surge_multiplier"]>1].shape[0])
    col2.metric("Average Surge Multiplier", round(df["surge_multiplier"].mean(),2))
    col3.metric("Maximum Surge Multiplier", round(df["surge_multiplier"].max(),2))
    col4.metric("Average Wind Speed", round(df["windSpeed"].mean(),2))
    col5.metric("Average Visibility", round(df["visibility"].mean(),2))
    col6.metric("Total Routes", df["source"].nunique())

    st.markdown("---")

    # -------- ROW 1 --------
    col1, col2 = st.columns(2)

    # 1️⃣ Surge Trend by Hour
    fig1 = px.line(
        df.groupby("hour")["surge_multiplier"].mean().reset_index(),
        x="hour",
        y="surge_multiplier",
        title="Average Surge Multiplier in Hours",
        markers=True
    )
    fig1.update_traces(line_color="#1D4ED8")

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Surge Ride Count by Hour
    fig2 = px.bar(
        df[df["surge_multiplier"]>1].groupby("hour").size().reset_index(name="rides"),
        x="hour",
        y="rides",
        title="Surge Rides by Hour"
    )
    fig2.update_traces(marker_color="#374151")

    col2.plotly_chart(fig2, use_container_width=True)

    # -------- ROW 2 --------
    col3, col4 = st.columns(2)

    # 3️⃣ Surge % by Weather
    fig3 = px.bar(
        df.groupby("short_summary")["surge_multiplier"].mean().reset_index(),
        x="short_summary",
        y="surge_multiplier",
        title="Surge % by Weather"
    )
    fig3.update_traces(marker_color="#1D4ED8")

    col3.plotly_chart(fig3, use_container_width=True)

   # 4️⃣ Price vs Distance (NO ERROR VERSION)
fig4 = px.line(
    df.sort_values("distance"),
    x="distance",
    y="price",
    title="Price vs Distance Trend"
)

fig4.update_traces(line_color="#374151")

col4.plotly_chart(fig4, use_container_width=True)

# ---------------- PAGE 4 ----------------
elif page == "Prediction":

    st.subheader("🤖 Ride Price Prediction")

    col1,col2,col3 = st.columns(3)

    with col1:
        distance = st.number_input("Distance",0.1,10.0,2.0)
        hour = st.slider("Hour",0,23,12)
        temperature = st.number_input("Temperature",0.0,50.0,25.0)

    with col2:
        humidity = st.slider("Humidity",0.0,1.0,0.5)
        wind = st.number_input("Wind Speed",0.0,20.0,5.0)
        visibility = st.number_input("Visibility",0.0,15.0,10.0)

    with col3:
        cab = st.selectbox("Cab Type",df["cab_type"].unique())
        weather = st.selectbox("Weather",df["short_summary"].unique())

    if st.button("Predict Price"):

        base_price = distance * 3
        weather_factor = 1.2 if "Rain" in weather else 1
        temp_factor = temperature / 50

        predicted_price = round(base_price * weather_factor * (1 + temp_factor),2)

        r2 = r2_score(df_pred["Actual_Price"], df_pred["Predicted_RF"])
        confidence = round(r2 * 100,2)

        col1,col2 = st.columns(2)

        col1.metric("Predicted Price", f"${predicted_price}")
        col2.metric("Model Confidence", f"{confidence}%")

        st.success("Prediction Generated Successfully ")
