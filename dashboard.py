import os
import subprocess
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# Prophet（任意）
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


# =========================
# Page Config
# =========================
st.set_page_config(page_title="Climate Intelligence Platform", layout="wide")

st.title("🌍 Climate Intelligence Platform")
st.caption("Real-time environmental dashboard with AI forecasting")


# =========================
# Health Risk Function
# =========================
def health_risk_score(pm25, temp):
    pm_norm = min(pm25 / 100, 1.0) * 100
    temp_norm = min(abs(temp - 22) / 20, 1.0) * 100
    score = 0.6 * pm_norm + 0.4 * temp_norm

    if score < 30:
        return "Low Risk"
    elif score < 70:
        return "Medium Risk"
    else:
        return "High Risk"


# =========================
# Data Loading (ROBUST VERSION)
# =========================
CSV_FILE = "climate_data.csv"

if not os.path.exists(CSV_FILE):
    st.warning("climate_data.csv not found. Generating data...")

    try:
        subprocess.run(["python", "fetch_data.py"], check=True)
    except Exception as e:
        st.error(f"Failed to run fetch_data.py: {e}")
        st.stop()

if not os.path.exists(CSV_FILE):
    st.error("Data generation failed. CSV still not found.")
    st.stop()

df = pd.read_csv(CSV_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

st.success(
    f"Loaded {len(df)} records from "
    f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}"
)


# =========================
# Latest Data
# =========================
latest_df = df.groupby("city").last().reset_index()
latest_df["risk"] = latest_df.apply(
    lambda r: health_risk_score(r["pm25"], r["temperature"]),
    axis=1
)


# =========================
# UI: Risk Dashboard
# =========================
st.subheader("🔥 Health Risk Index (Latest Data)")

col1, col2, col3 = st.columns(3)

for _, row in latest_df.iterrows():
    if row["city"] == "tokyo":
        col1.metric("Tokyo", row["risk"])
        col1.caption(f"{row['temperature']}°C | PM2.5: {row['pm25']}")

    elif row["city"] == "beijing":
        col2.metric("Beijing", row["risk"])
        col2.caption(f"{row['temperature']}°C | PM2.5: {row['pm25']}")

    elif row["city"] == "bangkok":
        col3.metric("Bangkok", row["risk"])
        col3.caption(f"{row['temperature']}°C | PM2.5: {row['pm25']}")


st.divider()


# =========================
# Moving Average
# =========================
df = df.sort_values(["city", "timestamp"])

df["temp_ma"] = df.groupby("city")["temperature"].transform(
    lambda x: x.rolling(3, min_periods=1).mean()
)

df["pm25_ma"] = df.groupby("city")["pm25"].transform(
    lambda x: x.rolling(3, min_periods=1).mean()
)


# =========================
# Time Series
# =========================
st.subheader("📈 Time-Series Analysis (Moving Average)")

fig1 = px.line(df, x="timestamp", y="temp_ma", color="city",
               title="Temperature Trend (Smoothed)")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(df, x="timestamp", y="pm25_ma", color="city",
               title="PM2.5 Trend (Smoothed)")
st.plotly_chart(fig2, use_container_width=True)

st.divider()


# =========================
# Latest Comparison
# =========================
st.subheader("📊 Latest Comparison")

c1, c2 = st.columns(2)

with c1:
    st.plotly_chart(
        px.bar(latest_df, x="city", y="temperature", title="Temperature"),
        use_container_width=True
    )

with c2:
    st.plotly_chart(
        px.bar(latest_df, x="city", y="pm25", title="PM2.5"),
        use_container_width=True
    )


st.divider()


# =========================
# Recommendation
# =========================
st.subheader("🧭 Recommendations")

for _, row in latest_df.iterrows():
    if row["risk"] == "Low Risk":
        msg = "Good for outdoor activities"
    elif row["risk"] == "Medium Risk":
        msg = "Consider mask if sensitive"
    else:
        msg = "Avoid outdoor exposure"

    st.write(f"**{row['city'].title()}** → {msg}")


st.divider()


# =========================
# AI Prediction
# =========================
st.subheader("🤖 AI Time-Series Forecasting")

method = st.radio(
    "Select method",
    ["Linear Regression", "Prophet"],
    horizontal=True
)

city = st.selectbox("Select city", df["city"].unique())
city_df = df[df["city"] == city].copy()


# =========================
# Linear Regression
# =========================
if method == "Linear Regression":

    if len(city_df) < 3:
        st.warning("Not enough data")
    else:
        city_df = city_df.copy()
        city_df["time_index"] = np.arange(len(city_df))

        X = pd.DataFrame(city_df["time_index"], columns=["time_index"])

        y_temp = city_df["temperature"]
        y_pm = city_df["pm25"]

        model_t = LinearRegression()
        model_p = LinearRegression()

        model_t.fit(X, y_temp)
        model_p.fit(X, y_pm)

        future = pd.DataFrame([[len(city_df)]], columns=["time_index"])

        pred_t = model_t.predict(future)[0]
        pred_p = model_p.predict(future)[0]

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Pred Temp", f"{pred_t:.1f}°C",
                      f"{pred_t - city_df['temperature'].iloc[-1]:+.1f}")

        with c2:
            st.metric("Pred PM2.5", f"{pred_p:.0f}",
                      f"{pred_p - city_df['pm25'].iloc[-1]:+.0f}")


# =========================
# Prophet
# =========================
else:

    if not PROPHET_AVAILABLE:
        st.error("Prophet not installed")
    elif len(city_df) < 5:
        st.warning("Need at least 5 records")
    else:
        from prophet import Prophet

        temp_df = city_df[["timestamp", "temperature"]].rename(
            columns={"timestamp": "ds", "temperature": "y"}
        )

        model = Prophet(daily_seasonality=True)
        model.fit(temp_df)

        future = model.make_future_dataframe(periods=3, freq="h")
        forecast = model.predict(future)

        st.line_chart(forecast.set_index("ds")[["yhat"]])


# =========================
# Raw Data
# =========================
st.subheader("📦 Raw Data")
st.dataframe(df)