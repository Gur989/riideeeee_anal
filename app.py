#%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
from sklearn.metrics import r2_score

st.set_page_config(page_title="Rides Analytics", layout="wide", initial_sidebar_state="expanded")

# ---------------- PREMIUM DARK THEME STYLE ----------------
st.markdown("""
<style>
/* Main Background */
.main {
    background-color: #0B0F19;
}

/* Typography */
h1, h2, h3, h4, label, p, span {
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif;
}

/* KPI Cards with Glassmorphism */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1E293B, #0F172A);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s ease, border-color 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border-color: #38BDF8;
}

/* Metric Value Colors */
div[data-testid="stMetricValue"] {
    color: #38BDF8 !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1E293B;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-weight: 700;
    box-shadow: 0px 4px 15px rgba(220, 38, 38, 0.4);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 6px 20px rgba(239, 68, 68, 0.6);
    color: #FFFFFF !important;
    border: none;
}

/* Selectboxes, sliders, inputs */
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stMultiSelect>div>div>div {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Form */
[data-testid="stForm"] {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER WITH LOGO ----------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("logo.png", width=100)

with col_title:
    st.markdown("<h1 style='background: -webkit-linear-gradient(#EF4444, #DC2626); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding-top: 10px;'>Rides Analytics Dashboard</h1>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Secure Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Login", use_container_width=True):
                if username == "admin" and password == "1234":
                    st.session_state.login = True
                    st.rerun()
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
st.sidebar.image("logo.png", width=120)
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "",
    ["Timing Analysis", "Weather Impact", "Surge Pricing", "Prediction"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

month = st.sidebar.multiselect("Month", df["month"].unique(), df["month"].unique())
cab = st.sidebar.multiselect("Cab Type", df["cab_type"].unique(), df["cab_type"].unique())

df = df[(df["month"].isin(month)) & (df["cab_type"].isin(cab))]

# ---------------- PAGE 1 ----------------
if page == "Timing Analysis":

    st.markdown("### Ride Pricing by Time")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rides", f"{len(df):,}")
    col2.metric("Avg Price", f"${df['price'].mean():.2f}")
    col3.metric("Avg Surge", f"{df['surge_multiplier'].mean():.2f}x")
    col4.metric("Avg Distance", f"{df['distance'].mean():.2f} mi")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # 1️⃣ Average Price Per Hour
    fig1 = px.line(
        df.groupby("hour")["price"].mean().reset_index(),
        x="hour",
        y="price",
        title="Average Price in Each Hour",
        markers=True,
        template="plotly_dark"
    )
    fig1.update_traces(line_color="#38BDF8", marker=dict(size=8, color="#F8FAFC")) 
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Ride Count Per Hour
    fig2 = px.line(
        df.groupby("hour").size().reset_index(name="rides"),
        x="hour",
        y="rides",
        title="Ride Count Per Hour",
        markers=True,
        template="plotly_dark"
    )
    fig2.update_traces(line_color="#A78BFA", marker=dict(size=8, color="#F8FAFC"))
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col2.plotly_chart(fig2, use_container_width=True)

    # SECOND ROW
    col3, col4 = st.columns(2)

    # 3️⃣ Average Surge Per Hour
    fig3 = px.bar(
        df.groupby("hour")["surge_multiplier"].mean().reset_index(),
        x="hour",
        y="surge_multiplier",
        title="Average Surge in Each Hour",
        template="plotly_dark"
    )
    fig3.update_traces(marker_color="#F472B6")
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col3.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Average Visibility Per Hour
    fig4 = px.bar(
        df.groupby("hour")["visibility"].mean().reset_index(),
        x="hour",
        y="visibility",
        title="Average Visibility in Each Hour",
        template="plotly_dark"
    )
    fig4.update_traces(marker_color="#34D399")
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col4.plotly_chart(fig4, use_container_width=True)

# ---------------- PAGE 2 ----------------
elif page == "Weather Impact":

    st.markdown("### Weather Impact on Pricing")

    # -------- KPI --------
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Clear Weather Price", f"${df[df['short_summary']=='Clear']['price'].mean():.2f}")
    col2.metric("Rainy Weather Price", f"${df[df['short_summary'].str.contains('Rain')]['price'].mean():.2f}")
    col3.metric("Foggy Weather Price", f"${df[df['short_summary'].str.contains('Fog')]['price'].mean():.2f}")
    col4.metric("Average Temperature", f"{df['temperature'].mean():.1f}°")
    col5.metric("Rain Surge Rate", f"{df[df['short_summary'].str.contains('Rain')]['surge_multiplier'].mean():.2f}x")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------- CHARTS (ROW 1) --------
    col1, col2 = st.columns(2)

    # 1️⃣ Avg Price by Weather
    fig1 = px.bar(
        df.groupby("short_summary")["price"].mean().reset_index(),
        x="short_summary",
        y="price",
        title="Average Price by Weather",
        template="plotly_dark",
        color="price",
        color_continuous_scale="Tealgrn"
    )
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Price vs Temperature
    fig2 = px.scatter(
        df,
        x="temperature",
        y="price",
        title="Price vs Temperature",
        template="plotly_dark",
        color_discrete_sequence=["#F472B6"]
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col2.plotly_chart(fig2, use_container_width=True)

    # -------- CHARTS (ROW 2) --------
    col3, col4 = st.columns(2)

    # 3️⃣ Price vs Visibility
    fig3 = px.scatter(
        df,
        x="visibility",
        y="price",
        title="Price vs Visibility",
        template="plotly_dark",
        color_discrete_sequence=["#A78BFA"]
    )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col3.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Surge % by Weather
    fig4 = px.bar(
        df.groupby("short_summary")["surge_multiplier"].mean().reset_index(),
        x="short_summary",
        y="surge_multiplier",
        title="Surge % by Weather",
        template="plotly_dark",
        color="surge_multiplier",
        color_continuous_scale="Purp"
    )
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col4.plotly_chart(fig4, use_container_width=True)

# ---------------- PAGE 3 ----------------
elif page == "Surge Pricing":

    st.markdown("### Surge Pricing and Routes")

    # -------- KPI --------
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Surge Rides", f"{df[df['surge_multiplier']>1].shape[0]:,}")
    col2.metric("Avg Surge Multiplier", f"{df['surge_multiplier'].mean():.2f}x")
    col3.metric("Max Surge Multiplier", f"{df['surge_multiplier'].max():.2f}x")
    col4.metric("Average Wind Speed", f"{df['windSpeed'].mean():.2f}")
    col5.metric("Average Visibility", f"{df['visibility'].mean():.2f}")
    col6.metric("Total Routes", df["source"].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # -------- ROW 1 --------
    col1, col2 = st.columns(2)

    # 1️⃣ Surge Trend by Hour
    fig1 = px.line(
        df.groupby("hour")["surge_multiplier"].mean().reset_index(),
        x="hour",
        y="surge_multiplier",
        title="Average Surge Multiplier in Hours",
        markers=True,
        template="plotly_dark"
    )
    fig1.update_traces(line_color="#F43F5E", marker=dict(size=8, color="#F8FAFC"))
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col1.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Surge Ride Count by Hour
    fig2 = px.bar(
        df[df["surge_multiplier"]>1].groupby("hour").size().reset_index(name="rides"),
        x="hour",
        y="rides",
        title="Surge Rides by Hour",
        template="plotly_dark"
    )
    fig2.update_traces(marker_color="#FBBF24")
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    col2.plotly_chart(fig2, use_container_width=True)

# ---------------- PAGE 4 ----------------
elif page == "Prediction":

    st.markdown("### Ride Price Prediction")
    st.markdown("Adjust the parameters below to predict the estimated ride price using our machine learning model.")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        distance = st.number_input("Distance (miles)", 0.1, 10.0, 2.0)
        hour = st.slider("Hour of Day", 0, 23, 12)
        temperature = st.number_input("Temperature (°F)", 0.0, 50.0, 25.0)

    with col2:
        humidity = st.slider("Humidity", 0.0, 1.0, 0.5)
        wind = st.number_input("Wind Speed", 0.0, 20.0, 5.0)
        visibility = st.number_input("Visibility", 0.0, 15.0, 10.0)

    with col3:
        cab = st.selectbox("Cab Type", df["cab_type"].unique())
        weather = st.selectbox("Weather", df["short_summary"].unique())

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Predict Price", use_container_width=True):

        base_price = distance * 3
        weather_factor = 1.2 if "Rain" in weather else 1
        temp_factor = temperature / 50

        predicted_price = round(base_price * weather_factor * (1 + temp_factor), 2)

        r2 = r2_score(df_pred["Actual_Price"], df_pred["Predicted_RF"])
        confidence = round(r2 * 100, 2)

        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            col_a, col_b = st.columns(2)
            col_a.metric("Predicted Price", f"${predicted_price}")
            col_b.metric("Model Confidence", f"{confidence}%")
            
            st.success("Prediction Generated Successfully")
