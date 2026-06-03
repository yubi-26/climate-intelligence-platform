import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# Prophetはインストールされている場合のみインポート
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

st.set_page_config(page_title="Climate Intelligence Platform", layout="wide")

st.title("Climate Intelligence Platform")
st.caption("Real-time environmental dashboard with time-series analysis and AI prediction")

def health_risk_score(pm25, temp):
    # 正規化されたスコア（0-100）
    pm_normalized = min(pm25 / 100, 1.0) * 100
    temp_normalized = min(abs(temp - 22) / 20, 1.0) * 100
    
    # 重み付き指数モデル（PM2.5: 0.6, 気温: 0.4）
    total = 0.6 * pm_normalized + 0.4 * temp_normalized
    
    if total < 30:
        return "Low Risk"
    elif total < 70:
        return "Medium Risk"
    else:
        return "High Risk"

try:
    df = pd.read_csv("climate_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    st.success(f"Loaded {len(df)} records from {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    
    # 最新データでリスク計算
    latest_df = df.groupby('city').last().reset_index()
    latest_df['risk'] = latest_df.apply(lambda row: health_risk_score(row['pm25'], row['temperature']), axis=1)
    
    # Health Risk Index
    st.subheader("Health Risk Index (Latest Data)")
    
    col1, col2, col3 = st.columns(3)
    
    for i, row in latest_df.iterrows():
        if row['city'] == 'tokyo':
            col1.metric("Tokyo", row['risk'])
            col1.caption(f"{row['temperature']} C | PM2.5: {row['pm25']}")
        elif row['city'] == 'beijing':
            col2.metric("Beijing", row['risk'])
            col2.caption(f"{row['temperature']} C | PM2.5: {row['pm25']}")
        elif row['city'] == 'bangkok':
            col3.metric("Bangkok", row['risk'])
            col3.caption(f"{row['temperature']} C | PM2.5: {row['pm25']}")
    
    st.divider()
    
    # 移動平均を計算
    df = df.sort_values(['city', 'timestamp'])
    df['temp_ma'] = df.groupby('city')['temperature'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df['pm25_ma'] = df.groupby('city')['pm25'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    
    # 時系列分析グラフ
    st.subheader("Time-Series Analysis with Moving Average (3-period)")
    
    fig_temp_trend = px.line(
        df,
        x="timestamp",
        y="temp_ma",
        color="city",
        title="Temperature Trend Over Time (Smoothed)",
        markers=True
    )
    st.plotly_chart(fig_temp_trend, use_container_width=True)
    
    fig_pm_trend = px.line(
        df,
        x="timestamp",
        y="pm25_ma",
        color="city",
        title="PM2.5 Trend Over Time (Smoothed)",
        markers=True
    )
    st.plotly_chart(fig_pm_trend, use_container_width=True)
    
    st.divider()
    
    # 最新データの比較グラフ
    st.subheader("Latest Data Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_temp = px.bar(latest_df, x='city', y='temperature', 
                          title='Temperature Comparison (C)', 
                          color='city')
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        fig_pm = px.bar(latest_df, x='city', y='pm25', 
                        title='PM2.5 Comparison', 
                        color='city')
        st.plotly_chart(fig_pm, use_container_width=True)
    
    st.divider()
    
    # 外出推奨機能
    st.subheader("Today's Recommendation")
    
    for i, row in latest_df.iterrows():
        risk = row['risk']
        if risk == "Low Risk":
            advice = "Good day for outdoor activities"
        elif risk == "Medium Risk":
            advice = "Consider mask if sensitive to air pollution"
        else:
            advice = "Avoid prolonged outdoor exposure. Mask recommended"
        
        if row['city'] == 'tokyo':
            st.info(f"**Tokyo**: {advice}")
        elif row['city'] == 'beijing':
            st.warning(f"**Beijing**: {advice}")
        elif row['city'] == 'bangkok':
            st.info(f"**Bangkok**: {advice}")
    
    st.divider()
    
    # ============================================================
    # AI予測セクション（線形回帰 + Prophet）
    # ============================================================
    st.subheader("AI Time-Series Forecasting")
    
    # 予測方法の選択
    prediction_method = st.radio(
        "Select prediction method",
        ["Linear Regression (Baseline)", "Prophet (Advanced)"],
        horizontal=True
    )
    
    pred_city = st.selectbox("Select city for prediction", ["tokyo", "beijing", "bangkok"])
    city_df = df[df['city'] == pred_city].copy()
    
    if prediction_method == "Linear Regression (Baseline)":
        # 線形回帰による予測
        if len(city_df) >= 3:
            city_df['time_index'] = np.arange(len(city_df))
            
            X = city_df[['time_index']]
            y_temp = city_df['temperature']
            y_pm = city_df['pm25']
            
            model_temp = LinearRegression()
            model_pm = LinearRegression()
            
            model_temp.fit(X, y_temp)
            model_pm.fit(X, y_pm)
            
            future_index = np.array([[len(city_df)]])
            pred_temp = model_temp.predict(future_index)[0]
            pred_pm = model_pm.predict(future_index)[0]
            
            pred_col1, pred_col2 = st.columns(2)
            
            with pred_col1:
                st.metric(
                    label=f"Predicted Temperature ({pred_city.upper()})",
                    value=f"{pred_temp:.1f} C",
                    delta=f"{pred_temp - city_df['temperature'].iloc[-1]:+.1f}C from last"
                )
            
            with pred_col2:
                st.metric(
                    label=f"Predicted PM2.5 ({pred_city.upper()})",
                    value=f"{pred_pm:.0f}",
                    delta=f"{pred_pm - city_df['pm25'].iloc[-1]:+.0f} from last"
                )
            
            st.caption("Baseline linear regression model. Assumes linear trend continuation.")
            
            # 予測グラフ
            fig_pred = px.line(
                city_df,
                x='time_index',
                y='temperature',
                title=f"Temperature Trend & Prediction for {pred_city.upper()} (Linear Regression)",
                labels={'time_index': 'Sample Number', 'temperature': 'Temperature (C)'}
            )
            fig_pred.add_scatter(x=[len(city_df)], y=[pred_temp], mode='markers', 
                                  marker=dict(size=15, color='red'), name='Prediction')
            st.plotly_chart(fig_pred, use_container_width=True)
            
        else:
            st.warning(f"Not enough data for {pred_city}. Need at least 3 records. Current: {len(city_df)}")
    
    else:  # Prophet (Advanced)
        if not PROPHET_AVAILABLE:
            st.error("Prophet is not installed. Run: pip install prophet")
        elif len(city_df) >= 5:
            # Prophetによる予測
            with st.spinner("Training Prophet model... (may take 10-20 seconds)"):
                # 気温予測モデル
                prophet_df_temp = city_df[['timestamp', 'temperature']].rename(columns={'timestamp': 'ds', 'temperature': 'y'})
                prophet_df_pm = city_df[['timestamp', 'pm25']].rename(columns={'timestamp': 'ds', 'pm25': 'y'})
                
                # 季節性設定（データ量が少ないのでdailyのみ）
                model_temp = Prophet(
                    yearly_seasonality=False,
                    weekly_seasonality=False,
                    daily_seasonality=True,
                    changepoint_prior_scale=0.05,
                    interval_width=0.95
                )
                model_temp.fit(prophet_df_temp)
                
                model_pm = Prophet(
                    yearly_seasonality=False,
                    weekly_seasonality=False,
                    daily_seasonality=True,
                    changepoint_prior_scale=0.05,
                    interval_width=0.95
                )
                model_pm.fit(prophet_df_pm)
                
                # 未来予測（次の3時間分）
                future_temp = model_temp.make_future_dataframe(periods=3, freq='h')
                future_pm = model_pm.make_future_dataframe(periods=3, freq='h')
                
                forecast_temp = model_temp.predict(future_temp)
                forecast_pm = model_pm.predict(future_pm)
                
                # 次の予測値
                next_temp = forecast_temp['yhat'].iloc[-1]
                next_pm = forecast_pm['yhat'].iloc[-1]
                lower_temp = forecast_temp['yhat_lower'].iloc[-1]
                upper_temp = forecast_temp['yhat_upper'].iloc[-1]
                lower_pm = forecast_pm['yhat_lower'].iloc[-1]
                upper_pm = forecast_pm['yhat_upper'].iloc[-1]
            
            pred_col1, pred_col2 = st.columns(2)
            
            with pred_col1:
                st.metric(
                    label=f"Prophet Predicted Temperature ({pred_city.upper()})",
                    value=f"{next_temp:.1f} C",
                    delta=f"{next_temp - city_df['temperature'].iloc[-1]:+.1f}C from last"
                )
                st.caption(f"95% CI: [{lower_temp:.1f} - {upper_temp:.1f}]")
            
            with pred_col2:
                st.metric(
                    label=f"Prophet Predicted PM2.5 ({pred_city.upper()})",
                    value=f"{next_pm:.0f}",
                    delta=f"{next_pm - city_df['pm25'].iloc[-1]:+.0f} from last"
                )
                st.caption(f"95% CI: [{lower_pm:.0f} - {upper_pm:.0f}]")
            
            st.caption("Prophet by Meta: Automatically detects trend and daily seasonality patterns.")
            
            # 気温予測グラフ
            fig_prophet_temp = model_temp.plot(forecast_temp)
            fig_prophet_temp.update_layout(
                title=f"Temperature Forecast for {pred_city.upper()} (Prophet)",
                xaxis_title="Time",
                yaxis_title="Temperature (°C)"
            )
            st.plotly_chart(fig_prophet_temp, use_container_width=True)
            
            # 予測の成分分解（トレンド＋季節性）
            try:
                fig_components = model_temp.plot_components(forecast_temp)
                st.pyplot(fig_components)
                st.caption("Components: Trend (left) + Daily Seasonality (right)")
            except Exception as e:
                st.caption("Component decomposition not available for this dataset.")
            
        else:
            st.warning(f"Not enough data for {pred_city}. Prophet needs at least 5 records. Current: {len(city_df)}")
    
    # 生データ表示
    st.subheader("Raw Environmental Data (Time Series)")
    st.dataframe(df[['city', 'temperature', 'pm25', 'timestamp']])
        
except FileNotFoundError:
    st.error("climate_data.csv not found. Run fetch_data.py first.")
except Exception as e:
    st.error(f"Error: {e}")