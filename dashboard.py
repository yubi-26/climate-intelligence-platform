import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="Climate Risk Intelligence",
    page_icon="🌍",
    layout="wide"
)

# =========================
# カスタムCSS
# =========================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #1a1f2e 100%);
    }
    
    .risk-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 40px 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        margin: 20px 0;
    }
    
    .risk-score-label {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: rgba(255,255,255,0.5);
        margin-top: 10px;
    }
    
    .risk-level-badge {
        display: inline-block;
        padding: 8px 24px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 16px;
        margin-top: 15px;
        letter-spacing: 1px;
    }
    
    .risk-extreme {
        background: rgba(255,0,0,0.2);
        color: #ff4444;
        border: 1px solid rgba(255,0,0,0.3);
    }
    
    .risk-high {
        background: rgba(255,165,0,0.2);
        color: #ffa500;
        border: 1px solid rgba(255,165,0,0.3);
    }
    
    .risk-moderate {
        background: rgba(255,217,61,0.2);
        color: #ffd93d;
        border: 1px solid rgba(255,217,61,0.3);
    }
    
    .risk-low {
        background: rgba(0,255,0,0.2);
        color: #00ff88;
        border: 1px solid rgba(0,255,0,0.3);
    }
    
    .kpi-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
    }
    
    .kpi-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: rgba(255,255,255,0.4);
        margin-top: 5px;
    }
    
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }
    
    .insight-box {
        background: rgba(255,255,255,0.03);
        border-left: 3px solid #ffd93d;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Climate Risk Score 計算エンジン
# =========================

def calculate_climate_risk_score(pm25, temperature, humidity=None, aqi=None):
    """
    Climate Risk Score (0-100)
    0-30: Low, 30-60: Moderate, 60-80: High, 80-100: Extreme
    """
    if pm25 <= 12:
        pm25_normalized = pm25 / 12 * 0.3
    elif pm25 <= 35:
        pm25_normalized = 0.3 + (pm25 - 12) / (35 - 12) * 0.2
    elif pm25 <= 55:
        pm25_normalized = 0.5 + (pm25 - 35) / (55 - 35) * 0.2
    elif pm25 <= 150:
        pm25_normalized = 0.7 + (pm25 - 55) / (150 - 55) * 0.2
    else:
        pm25_normalized = 0.9 + min((pm25 - 150) / 200, 0.1)
    
    comfort_low, comfort_high = 18, 24
    if comfort_low <= temperature <= comfort_high:
        temp_deviation = 0
    elif temperature < comfort_low:
        temp_deviation = (comfort_low - temperature) / 30
    else:
        temp_deviation = (temperature - comfort_high) / 20
    temp_normalized = min(temp_deviation, 1.0)
    
    if humidity is not None:
        if 40 <= humidity <= 60:
            humidity_normalized = 0
        elif humidity < 40:
            humidity_normalized = (40 - humidity) / 40
        else:
            humidity_normalized = (humidity - 60) / 40
        humidity_normalized = min(humidity_normalized, 1.0)
    else:
        humidity_normalized = 0.3
    
    if aqi is not None:
        if aqi <= 50:
            aqi_normalized = 0
        elif aqi <= 100:
            aqi_normalized = 0.3
        elif aqi <= 150:
            aqi_normalized = 0.6
        elif aqi <= 200:
            aqi_normalized = 0.8
        else:
            aqi_normalized = 1.0
    else:
        aqi_normalized = 0.2
    
    risk_normalized = (
        pm25_normalized * 0.4 +
        temp_normalized * 0.3 +
        humidity_normalized * 0.2 +
        aqi_normalized * 0.1
    )
    
    risk_score = round(risk_normalized * 100, 1)
    return risk_score


def get_risk_level(score):
    if score >= 80:
        return "EXTREME", "risk-extreme", "🔴"
    elif score >= 60:
        return "HIGH", "risk-high", "🟠"
    elif score >= 30:
        return "MODERATE", "risk-moderate", "🟡"
    else:
        return "LOW", "risk-low", "🟢"


def get_health_guidance(score):
    if score >= 80:
        return {
            "title": "Extreme Risk - Hazardous",
            "advice": [
                "🚫 Avoid all outdoor activities",
                "🏠 Stay indoors with air purification",
                "😷 N95 mask required if going outside",
                "⚡ Seek medical help if breathing difficulty occurs"
            ],
            "sensitive": "Everyone is at risk"
        }
    elif score >= 60:
        return {
            "title": "High Risk - Unhealthy",
            "advice": [
                "⚠️ Limit outdoor exposure",
                "😷 Wear mask outdoors",
                "🏠 Keep windows closed",
                "💊 Keep medication ready if asthmatic"
            ],
            "sensitive": "Children, elderly, respiratory patients"
        }
    elif score >= 30:
        return {
            "title": "Moderate Risk - Caution",
            "advice": [
                "🪟 Ventilate during low-pollution hours",
                "🏃 Sensitive groups: reduce strenuous exercise",
                "📊 Monitor air quality updates",
                "🌿 Use air-purifying plants indoors"
            ],
            "sensitive": "Sensitive individuals should take precautions"
        }
    else:
        return {
            "title": "Low Risk - Safe",
            "advice": [
                "✅ All outdoor activities safe",
                "🏃 Ideal for exercise and sports",
                "🪟 Open windows for fresh air",
                "🌳 Enjoy outdoor activities"
            ],
            "sensitive": "No restrictions"
        }

# =========================
# CSV読み込み
# =========================

df = pd.read_csv("climate_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

if "humidity" not in df.columns:
    np.random.seed(42)
    df["humidity"] = np.random.uniform(30, 80, len(df))

# =========================
# Risk Score計算
# =========================

df["risk_score"] = df.apply(
    lambda row: calculate_climate_risk_score(
        row["pm25"], row["temperature"], row["humidity"], row["aqi"]
    ), axis=1
)

# =========================
# 都市選択
# =========================

cities = sorted(df["city"].unique())

# =========================
# ヘッダー
# =========================

st.markdown("""
<div style="text-align: center; padding: 20px 0 30px 0;">
    <h1 style="font-size: 36px; font-weight: 700; color: #ffffff; margin-bottom: 5px;">
        🌍 Climate Risk Intelligence
    </h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 14px; letter-spacing: 2px; text-transform: uppercase;">
        Environmental Risk Quantification System
    </p>
</div>
""", unsafe_allow_html=True)

col_city, _ = st.columns([3, 7])
with col_city:
    selected_city = st.selectbox("📍 Select City for Analysis", cities, label_visibility="collapsed")

city_df = df[df["city"] == selected_city].copy()
latest = city_df.iloc[-1]

if len(city_df) >= 24:
    previous_24h = city_df.iloc[-24]
    score_change = latest["risk_score"] - previous_24h["risk_score"]
else:
    score_change = 0

# =========================
# メインRisk Scoreカード
# =========================

risk_score = latest["risk_score"]
risk_level, risk_class, risk_icon = get_risk_level(risk_score)
guidance = get_health_guidance(risk_score)

st.markdown(f"""
<div class="risk-card">
    <div class="risk-score-label">Climate Risk Score</div>
    <div style="font-size: 120px; font-weight: 800; line-height: 1.1; margin: 10px 0;
                background: linear-gradient(135deg, #ff6b6b, #ffa500, #ffd93d);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;">
        {risk_score:.0f}
    </div>
    <div style="font-size: 18px; color: rgba(255,255,255,0.6);">/ 100</div>
    <div class="risk-level-badge {risk_class}">
        {risk_icon} {risk_level} RISK
    </div>
    <div style="margin-top: 12px; font-size: 14px; color: rgba(255,255,255,0.5);">
        {selected_city} · {latest['timestamp'].strftime('%Y-%m-%d %H:%M')}
    </div>
</div>
""", unsafe_allow_html=True)

if score_change != 0:
    arrow = "↑" if score_change > 0 else "↓"
    color = "#ff6b6b" if score_change > 0 else "#00ff88"
    st.markdown(f"""
    <div style="text-align: center; margin: -10px 0 20px 0;">
        <span style="color: {color}; font-size: 16px; font-weight: 600;">
            {arrow} {abs(score_change):.1f} points from 24h ago
        </span>
    </div>
    """, unsafe_allow_html=True)

# =========================
# KPI行
# =========================

st.markdown('<p class="section-title">📊 Key Indicators</p>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{latest['pm25']:.1f}</div>
        <div class="kpi-label">PM2.5 μg/m³</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{latest['temperature']:.1f}°C</div>
        <div class="kpi-label">Temperature</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{latest['humidity']:.0f}%</div>
        <div class="kpi-label">Humidity</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{latest['aqi']}</div>
        <div class="kpi-label">AQI Index</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 健康ガイダンス
# =========================

st.markdown('<p class="section-title">🏥 Health Guidance</p>', unsafe_allow_html=True)

col_advice, col_sensitive = st.columns([2, 1])

with col_advice:
    for item in guidance["advice"]:
        st.markdown(f"""
        <div class="insight-box">
            <span style="color: #ffffff; font-size: 15px;">{item}</span>
        </div>
        """, unsafe_allow_html=True)

with col_sensitive:
    st.markdown(f"""
    <div class="kpi-card" style="text-align: left;">
        <div style="color: rgba(255,255,255,0.4); font-size: 11px; 
                    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px;">
            Sensitive Groups
        </div>
        <div style="color: #ffffff; font-size: 14px; line-height: 1.6;">
            {guidance['sensitive']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# Risk Score 推移グラフ
# =========================

st.markdown('<p class="section-title">📈 Risk Score Trend</p>', unsafe_allow_html=True)

fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=city_df["timestamp"],
    y=city_df["risk_score"],
    mode='lines',
    line=dict(color='#4da6ff', width=3),
    fill='tozeroy',
    fillcolor='rgba(77,166,255,0.1)',
    name='Risk Score'
))

for thresh, label, color in [(30, "Low→Moderate", "#00ff88"), 
                               (60, "Moderate→High", "#ffd93d"),
                               (80, "High→Extreme", "#ff4444")]:
    fig_trend.add_hline(y=thresh, line_dash="dash", line_color=color, opacity=0.4)

fig_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=0),
    height=350,
    xaxis=dict(showgrid=False, color="rgba(255,255,255,0.4)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", 
               color="rgba(255,255,255,0.4)", range=[0, 100]),
    hovermode="x unified"
)

st.plotly_chart(fig_trend, use_container_width=True)

# =========================
# 世界Risk Map
# =========================

st.markdown('<p class="section-title">🗺 Global Climate Risk Map</p>', unsafe_allow_html=True)

latest_df = df.sort_values("timestamp").groupby("city").tail(1).copy()

def get_risk_color(score):
    if score >= 80: return "#ff4444"
    elif score >= 60: return "#ffa500"
    elif score >= 30: return "#ffd93d"
    else: return "#00ff88"

latest_df["risk_level"] = latest_df["risk_score"].apply(lambda x: get_risk_level(x)[0])

fig_map = px.scatter_mapbox(
    latest_df,
    lat="lat", lon="lon",
    color="risk_score",
    size="risk_score",
    size_max=25,
    hover_name="city",
    hover_data={"risk_score": ":.1f", "pm25": ":.1f", "temperature": ":.1f", 
                "aqi": True, "risk_level": True},
    color_continuous_scale=[[0.0, "#00ff88"], [0.3, "#ffd93d"], 
                            [0.6, "#ffa500"], [1.0, "#ff4444"]],
    zoom=1, height=450
)

fig_map.update_layout(
    mapbox_style="carto-darkmatter",
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig_map, use_container_width=True)

# =========================
# ランキング
# =========================

st.markdown('<p class="section-title">🏆 City Risk Rankings</p>', unsafe_allow_html=True)

col_high, col_low = st.columns(2)

with col_high:
    st.markdown("**🔴 Highest Risk Cities**")
    for _, row in latest_df.sort_values("risk_score", ascending=False).head(5).iterrows():
        level, cls, icon = get_risk_level(row["risk_score"])
        st.markdown(f"""
        <div class="insight-box" style="border-left-color: {get_risk_color(row['risk_score'])};">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #fff; font-weight: 600;">{row['city']}</span>
                <span style="color: {get_risk_color(row['risk_score'])}; font-weight: 700;">
                    {icon} {row['risk_score']:.0f}/100
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_low:
    st.markdown("**🟢 Lowest Risk Cities**")
    for _, row in latest_df.sort_values("risk_score", ascending=True).head(5).iterrows():
        level, cls, icon = get_risk_level(row["risk_score"])
        st.markdown(f"""
        <div class="insight-box" style="border-left-color: {get_risk_color(row['risk_score'])};">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #fff; font-weight: 600;">{row['city']}</span>
                <span style="color: {get_risk_color(row['risk_score'])}; font-weight: 700;">
                    {icon} {row['risk_score']:.0f}/100
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# # =========================
# 🔮 Risk Forecast Engine（Cross-City + Baseline Hybrid）
# =========================

st.markdown('<p class="section-title">🔮 Risk Forecast</p>', unsafe_allow_html=True)

def forecast_risk_score(city_name, current_score, current_pm25, current_temp, current_humidity, current_aqi, all_cities_df):
    """
    Cross-City Prediction + Baseline Hybrid
    研究上の説明: 類似都市のリスクパターンと全都市ベースラインから将来リスクを推定
    """
    
    # --- 1. Global Baseline ---
    global_mean = all_cities_df["risk_score"].mean()
    global_std = all_cities_df["risk_score"].std()
    
    # --- 2. Similar City Detection ---
    all_cities_df = all_cities_df.copy()
    all_cities_df["pm25_distance"] = abs(all_cities_df["pm25"] - current_pm25)
    all_cities_df["temp_distance"] = abs(all_cities_df["temperature"] - current_temp)
    
    pm25_range = all_cities_df["pm25"].max() - all_cities_df["pm25"].min() + 1
    temp_range = all_cities_df["temperature"].max() - all_cities_df["temperature"].min() + 1
    
    all_cities_df["similarity_score"] = (
        all_cities_df["pm25_distance"] / pm25_range * 0.6 +
        all_cities_df["temp_distance"] / temp_range * 0.4
    )
    
    similar_cities = (
        all_cities_df[all_cities_df["city"] != city_name]
        .sort_values("similarity_score")
        .head(3)
    )
    
    similar_mean_risk = similar_cities["risk_score"].mean()
    
    # --- 3. Trend Direction ---
    if current_pm25 > 50:
        pm25_trend = +1
    elif current_pm25 < 20:
        pm25_trend = -1
    else:
        pm25_trend = 0
    
    if current_temp > 30 or current_temp < 10:
        temp_trend = +1
    elif 18 <= current_temp <= 24:
        temp_trend = -1
    else:
        temp_trend = 0
    
    trend_direction = pm25_trend + temp_trend
    
    # --- 4. Predicted Risk Score ---
    predicted_score = (
        current_score * 0.5 +
        similar_mean_risk * 0.3 +
        global_mean * 0.2
    )
    
    if trend_direction > 0:
        predicted_score += 5
    elif trend_direction < 0:
        predicted_score -= 3
    
    predicted_score = max(0, min(100, predicted_score))
    predicted_score = round(predicted_score, 1)
    
    # --- 5. Confidence Level ---
    avg_similarity = similar_cities["similarity_score"].mean()
    if avg_similarity < 0.15:
        confidence = "High"
        confidence_color = "#00ff88"
    elif avg_similarity < 0.30:
        confidence = "Medium"
        confidence_color = "#ffd93d"
    else:
        confidence = "Low"
        confidence_color = "#ffa500"
    
    # --- 6. Contributing Factors ---
    factors = []
    
    if current_pm25 > 50:
        factors.append(f"High PM2.5 ({current_pm25:.0f} μg/m³) increases risk")
    if current_temp > 30:
        factors.append(f"High temperature ({current_temp:.0f}°C) amplifies pollution effect")
    elif current_temp < 10:
        factors.append(f"Low temperature ({current_temp:.0f}°C) may increase heating emissions")
    
    if trend_direction > 0:
        factors.append("Upward risk trend detected from similar cities")
    elif trend_direction < 0:
        factors.append("Downward risk trend expected")
    
    if not factors:
        factors.append("Stable conditions expected")
    
    return {
        "predicted_score": predicted_score,
        "change": predicted_score - current_score,
        "confidence": confidence,
        "confidence_color": confidence_color,
        "similar_cities": similar_cities["city"].tolist(),
        "factors": factors,
        "global_mean": global_mean
    }


# --- 予測実行 ---
forecast = forecast_risk_score(
    selected_city, 
    latest["risk_score"],
    latest["pm25"],
    latest["temperature"],
    latest["humidity"],
    latest["aqi"],
    latest_df
)

# =========================
# Forecast表示
# =========================

col_pred, col_factors = st.columns([1, 1.5])

with col_pred:
    change = forecast["change"]
    change_color = "#ff6b6b" if change > 0 else "#00ff88"
    change_arrow = "↑" if change > 0 else "↓"
    
    st.markdown(f"""
    <div class="kpi-card" style="padding: 30px 20px;">
        <div style="color: rgba(255,255,255,0.4); font-size: 12px; 
                    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
            Tomorrow's Forecast
        </div>
        <div style="font-size: 64px; font-weight: 800; color: #ffffff; line-height: 1;">
            {forecast['predicted_score']:.0f}
        </div>
        <div style="font-size: 14px; color: rgba(255,255,255,0.4); margin-top: 5px;">
            / 100
        </div>
        <div style="margin-top: 15px; font-size: 18px; font-weight: 600; color: {change_color};">
            {change_arrow} {abs(change):.1f} from today
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: {forecast['confidence_color']}; 
                    text-transform: uppercase; letter-spacing: 1px;">
            Confidence: {forecast['confidence']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_factors:
    st.markdown("**🔍 Contributing Factors**")
    for factor in forecast["factors"]:
        st.markdown(f"""
        <div class="insight-box">
            <span style="color: #ffffff; font-size: 14px;">{factor}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("**🌐 Reference Cities (Similar Profile)**")
    similar_str = ", ".join(forecast["similar_cities"])
    st.markdown(f"""
    <div class="insight-box" style="border-left-color: #4da6ff;">
        <span style="color: rgba(255,255,255,0.7); font-size: 13px;">
            Prediction based on: <strong style="color: #4da6ff;">{similar_str}</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- Global Baseline Indicator ---
global_mean_val = forecast['global_mean']
num_cities = len(latest_df)

st.markdown(f"""
<div style="text-align: center; margin: 10px 0; color: rgba(255,255,255,0.3); font-size: 12px;">
    Global Risk Baseline: <strong>{global_mean_val:.1f}/100</strong> 
    (averaged from {num_cities} cities)
</div>
""", unsafe_allow_html=True)

# =========================
# フッター
# =========================

st.divider()
st.markdown(f"""
<div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.3); font-size: 12px;">
    <span><strong>Climate Risk Intelligence v2.0</strong> — Research Prototype</span>
    <span>Last updated: {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

st.success("✅ Climate Risk Intelligence System — Operational")