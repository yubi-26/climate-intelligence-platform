import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

from prophet import Prophet
from googletrans import Translator

# =========================
# 🌍 基本設定
# =========================

st.set_page_config(page_title="Climate AI Dashboard", layout="wide")
translator = Translator()

WAQI_TOKEN = "YOUR_WAQI_TOKEN"

cities = {
    "tokyo": {"lat": 35.6895, "lon": 139.6917},
    "beijing": {"lat": 39.9042, "lon": 116.4074},
    "bangkok": {"lat": 13.7563, "lon": 100.5018},
    "berlin": {"lat": 52.5200, "lon": 13.4050},
    "ho_chi_minh": {"lat": 10.8231, "lon": 106.6297}
}

# =========================
# 🌦 データ取得
# =========================

@st.cache_data(ttl=300)
def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        r = requests.get(url, timeout=5)
        return r.json()["current_weather"]["temperature"]
    except:
        return None


@st.cache_data(ttl=300)
def fetch_pm25(city):
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data["status"] == "ok":
            return data["data"]["iaqi"]["pm25"]["v"]
    except:
        return None


# =========================
# 📊 データ生成
# =========================

@st.cache_data(ttl=120)
def build_dataset():
    rows = []

    for city, info in cities.items():
        temp = fetch_weather(info["lat"], info["lon"])
        pm25 = fetch_pm25(city)

        if temp is None or pm25 is None:
            continue

        rows.append({
            "city": city,
            "temperature": temp,
            "pm25": pm25,
            "timestamp": pd.Timestamp.now()
        })

    return pd.DataFrame(rows)


# =========================
# 🧠 LSTM
# =========================

@st.cache_resource
def train_lstm(data):
    values = data["pm25"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(len(scaled) - 3):
        X.append(scaled[i:i+3])
        y.append(scaled[i+3])

    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(32, input_shape=(3, 1)))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=20, verbose=0)

    return model, scaler


# =========================
# ⚡ XGBoost（追加の重要部分）
# =========================

@st.cache_resource
def train_xgboost(data):
    X = np.arange(len(data)).reshape(-1, 1)
    y = data["pm25"].values

    model = XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1
    )

    model.fit(X, y)
    return model


# =========================
# 📈 Prophet
# =========================

@st.cache_resource
def train_prophet(data):
    df = data.copy()
    df = df.rename(columns={"timestamp": "ds", "pm25": "y"})

    model = Prophet()
    model.fit(df)

    return model


# =========================
# 🧠 予測
# =========================

def predict_all_models(data):
    results = {}

    # XGBoost
    xgb = train_xgboost(data)
    results["xgboost"] = float(xgb.predict([[len(data)]])[0])

    # LSTM
    lstm, scaler = train_lstm(data)
    last = data["pm25"].values[-3:].reshape(-1, 1)
    last_scaled = scaler.transform(last).reshape(1, 3, 1)

    pred_lstm = lstm.predict(last_scaled, verbose=0)
    results["lstm"] = float(scaler.inverse_transform(pred_lstm)[0][0])

    # Prophet
    prophet = train_prophet(data)
    future = prophet.make_future_dataframe(periods=1)
    forecast = prophet.predict(future)
    results["prophet"] = float(forecast["yhat"].iloc[-1])

    return results


# =========================
# 🌐 UI
# =========================

st.title("🌍 Climate Intelligence Platform (AI Final Version)")

df = build_dataset()

if df.empty:
    st.warning("No data available")
    st.stop()


# =========================
# 📊 表示
# =========================

st.subheader("🏥 Health Risk Dashboard")

for _, row in df.iterrows():
    risk = "🔴 High" if row["pm25"] > 100 else "🟡 Medium"

    st.write(f"""
    **{row['city']}**  
    {risk}  
    🌡 {row['temperature']}°C | PM2.5: {row['pm25']}
    """)


# =========================
# 🤖 AI Prediction
# =========================

st.subheader("🤖 AI Forecast (XGBoost + LSTM + Prophet)")

city = st.selectbox("Select City", df["city"].unique())

city_data = df[df["city"] == city]

if len(city_data) >= 5:
    preds = predict_all_models(city_data)

    st.metric("XGBoost", round(preds["xgboost"], 2))
    st.metric("LSTM", round(preds["lstm"], 2))
    st.metric("Prophet", round(preds["prophet"], 2))


# =========================
# 🌐 多言語翻訳
# =========================

st.subheader("🌐 Translation Demo")

text = st.text_input("Enter text")

lang = st.selectbox("Language", ["ja", "en", "zh-cn"])

if text:
    try:
        result = translator.translate(text, dest=lang)
        st.success(result.text)
    except:
        st.error("Translation failed")


# =========================
# 🔁 Auto Refresh
# =========================

if st.checkbox("Auto Refresh (60s)"):
    time.sleep(60)
    st.rerun()