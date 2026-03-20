#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

st.set_page_config(page_title="Rides Analytics", layout="wide")

# ---------------- LIGHT THEME ----------------
st.markdown("""
<style>
.main {background-color:#F5F7FA;}

h1,h2,h3,h4,label {color:#1F2937;}

div[data-testid="metric-container"]{
    background-color:#FFFFFF;
    border-radius:12px;
    padding:18px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
}

section[data-testid="stSidebar"]{
    background-color:#FFFFFF;
    border-right:1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
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

df = load_data()

# ---------------- AUTOMATED ML PIPELINE (NO FILE SAVE) ----------------
@st.cache_data
def run_pipeline(df):

    df_ml = df.copy()

    df_ml = df_ml.drop(columns=['id','timestamp'])

    df_ml = pd.get_dummies(df_ml, columns=[
        'source','destination','cab_type','name','short_summary'
    ], drop_first=True)

    X = df_ml.drop('price', axis=1)
    y = df_ml['price']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Model 1: Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)

    # Model 2: Random Forest
    rf = RandomForestRegressor(
        n_estimators=10,
        max_depth=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)

    return {
        "y_test": y_test,
        "lr_pred": lr_pred,
        "rf_pred": rf_pred,
        "lr_r2": r2_score(y_test, lr_pred),
        "rf_r2": r2_score(y_test, rf_pred),
        "lr_mae": mean_absolute_error(y_test, lr_pred),
        "rf_mae": mean_absolute_error(y_test, rf_pred)
    }

# Run pipeline once (cached)
results = run_pipeline(df)

# ---------------- SIDEBAR ----------------
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Timing Analysis","Weather Impact","Surge Pricing","ML Prediction"]
)

# ---------------- PAGE 1 ----------------
if page == "Timing Analysis":

    st.subheader("⏱ Ride Pricing by Time")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Rides", len(df))
    col2.metric("Avg Price", round(df["price"].mean(),2))
    col3.metric("Avg Surge", round(df["surge_multiplier"].mean(),2))
    col4.metric("Avg Distance", round(df["distance"].mean(),2))

    col1,col2 = st.columns(2)

    fig1 = px.line(df.groupby("hour")["price"].mean().reset_index(),
                   x="hour", y="price",
                   title="📈 Average Ride Price Trend",
                   color_discrete_sequence=["#2563EB"])

    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df.groupby("hour")["price"].count().reset_index(),
                  x="hour", y="price",
                  title="📊 Ride Demand by Hour",
                  color_discrete_sequence=["#F97316"])

    col2.plotly_chart(fig2, use_container_width=True)

# ---------------- PAGE 2 ----------------
elif page == "Weather Impact":

    st.subheader("🌦 Weather Impact")

    col1,col2 = st.columns(2)

    fig1 = px.bar(df.groupby("short_summary")["price"].mean().reset_index(),
                  x="short_summary", y="price",
                  title="Weather vs Price",
                  color_discrete_sequence=["#F97316"])

    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x="temperature", y="price",
                      title="Temperature vs Price",
                      color_discrete_sequence=["#2563EB"])

    col2.plotly_chart(fig2, use_container_width=True)

# ---------------- PAGE 3 ----------------
elif page == "Surge Pricing":

    st.subheader("⚡ Surge Pricing")

    fig = px.line(df.groupby("hour")["surge_multiplier"].mean().reset_index(),
                  x="hour", y="surge_multiplier",
                  title="Surge Trend",
                  color_discrete_sequence=["#2563EB"])

    st.plotly_chart(fig, use_container_width=True)

# ---------------- PAGE 4 ----------------
elif page == "ML Prediction":

    st.subheader("🤖 Model Performance (Auto Updated)")

    col1,col2 = st.columns(2)

    col1.metric("Linear Regression R²", f"{round(results['lr_r2']*100,2)}%")
    col2.metric("Random Forest R²", f"{round(results['rf_r2']*100,2)}%")

    st.markdown("### 📊 Model Comparison")

    comp_df = pd.DataFrame({
        "Model": ["Linear Regression","Random Forest"],
        "R2": [results['lr_r2'], results['rf_r2']]
    })

    fig = px.bar(comp_df, x="Model", y="R2",
                 color="Model",
                 title="Model Performance Comparison")

    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Fully Automated (No File Storage)")
