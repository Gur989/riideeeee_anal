#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Rides Analytics", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.main { background-color:#F5F7FA; }
h1,h2,h3,h4,label { color:#1F2937; }
div[data-testid="metric-container"]{
    background-color:#FFFFFF;
    border-radius:12px;
    padding:18px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col_logo, col_title = st.columns([1,5])
with col_logo:
    st.image("logo.png", width=120)
with col_title:
    st.markdown("# Rides Analytics Dashboard")

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
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Timing Analysis","Weather Impact","Surge Pricing","Prediction"]
)

# ---------------- PAGE 1 ----------------
if page == "Timing Analysis":
    st.subheader("⏱ Ride Pricing by Time")

    fig = px.line(df.groupby("hour")["price"].mean().reset_index(),
                  x="hour", y="price", title="Avg Price per Hour")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- PAGE 2 ----------------
elif page == "Weather Impact":
    st.subheader("🌦 Weather Impact")

    fig = px.bar(df.groupby("short_summary")["price"].mean().reset_index(),
                 x="short_summary", y="price")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- PAGE 3 ----------------
elif page == "Surge Pricing":
    st.subheader("⚡ Surge Pricing")

    fig = px.line(df.groupby("hour")["surge_multiplier"].mean().reset_index(),
                  x="hour", y="surge_multiplier")
    st.plotly_chart(fig, use_container_width=True)

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

    # -------- MODEL --------
    features = ["distance","hour","temperature","humidity","windSpeed","visibility"]
    X = df_pred[features]
    y = df_pred["Actual_Price"]

    rf_model = RandomForestRegressor()
    rf_model.fit(X,y)

    lr_model = LinearRegression()
    lr_model.fit(X,y)

    if st.button("Predict Price"):

        input_data = pd.DataFrame({
            "distance":[distance],
            "hour":[hour],
            "temperature":[temperature],
            "humidity":[humidity],
            "windSpeed":[wind],
            "visibility":[visibility]
        })

        rf_pred = round(rf_model.predict(input_data)[0],2)
        lr_pred = round(lr_model.predict(input_data)[0],2)

        rf_r2 = r2_score(y, rf_model.predict(X))

        col1,col2 = st.columns(2)
        col1.metric("Random Forest Price", f"${rf_pred}")
        col2.metric("Linear Regression Price", f"${lr_pred}")

        st.metric("Model Confidence (RF)", f"{round(rf_r2*100,2)}%")

        st.success("Prediction Generated Successfully")
