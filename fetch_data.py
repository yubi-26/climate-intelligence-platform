```python
"""
Climate Intelligence Platform - Main Dashboard
CSV-only version (no OpenAQ dependency)
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="🌍 Climate Intelligence Platform",
    layout="wide"
)

st.title("🌍 Climate Intelligence Platform")
st.caption("CSV-only version (no OpenAQ dependency)")

# =========================
# CSV読み込み
# =========================
@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists("climate_data.csv"):
        st.error("❌ climate_data.csv not found.")
        return None, None

    df = pd.read_csv("climate_data.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    latest_df = df.groupby("city", as_index=False).tail(1)

    return df, latest_df


df, latest_df = load_data()

if df is None:
    st.stop()

# =========================
# サイドバー
# =========================
st.sidebar.header("Control Panel")

cities = sorted(latest_df["city"].unique())
selected_city = st.sidebar.selectbox(
    "Select City",
    cities
)

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Global Avg PM2.5",
        f"{latest_df['pm25'].mean():.1f}"
    )

with col2:
    st.metric(
        "Selected City",
        selected_city
    )

with col3:
    st.metric(
        "Cities",
        latest_df["city"].nunique()
    )

st.divider()

# =========================
# 都市詳細
# =========================
city_df = df[df["city"] == selected_city]
city_latest = latest_df[
    latest_df["city"] == selected_city
].iloc[0]

st.subheader(f"City Intelligence: {selected_city}")

st.line_chart(
    city_df.set_index("timestamp")["pm25"]
)

pm25 = city_latest["pm25"]

if pm25 > 100:
    st.error(f"🔴 High Risk | PM2.5 = {pm25}")
elif pm25 > 50:
    st.warning(f"🟡 Medium Risk | PM2.5 = {pm25}")
else:
    st.success(f"🟢 Low Risk | PM2.5 = {pm25}")

# =========================
# ランキング
# =========================
st.subheader("🏆 Cleanest Cities")

st.dataframe(
    latest_df.nsmallest(
        10,
        "pm25"
    )[["city", "pm25"]]
)

st.subheader("🏭 Most Polluted Cities")

st.dataframe(
    latest_df.nlargest(
        10,
        "pm25"
    )[["city", "pm25"]]
)

st.caption(
    "Data source: WAQI API + Open-Meteo API"
)
```