# 🌍 Climate Intelligence Platform

### A Data-Driven Environmental Health Risk Intelligence System Based on Urban Air Pollution and Climate Conditions

---

## 🧠 Abstract

This project presents an end-to-end environmental intelligence system that integrates real-time climate and air quality data with machine learning models to estimate human health risk levels.

The system collects temperature and PM2.5 data from multiple public APIs (Open-Meteo and WAQI), performs time-series analysis, and applies predictive modeling using Linear Regression and Prophet. Additionally, a Logistic Regression model is trained to classify environmental conditions into health risk categories.

The goal is to transform raw environmental data into actionable insights for urban health decision-making.

---

## 🎯 Objectives

- Integrate real-time environmental data (temperature + PM2.5)
- Construct a health risk scoring system
- Analyze temporal trends using time-series techniques
- Build predictive models for environmental forecasting
- Evaluate model performance quantitatively
- Provide interpretable health recommendations

---

## 🌍 System Overview

The system consists of three components:

### 1. Data Collection Layer
- Open-Meteo API (temperature)
- WAQI API (PM2.5)

### 2. Data Processing Layer
- Time-series alignment
- Moving average smoothing
- Feature engineering (risk score, time index)

### 3. Modeling & Visualization Layer
- Linear Regression (baseline forecasting)
- Prophet (advanced time-series forecasting)
- Logistic Regression (health risk classification)
- Streamlit dashboard (interactive visualization)

---

## 📊 Dataset

- **Cities**: Tokyo, Beijing, Bangkok
- **Features**:
  - Temperature (°C)
  - PM2.5 (µg/m³)
  - Timestamp (ISO format)
- **Data type**: Real-time time-series
- **Storage**: CSV-based logging system

---

## ⚙️ Methodology

### 1. Health Risk Score Function

```python
risk_score = 0.6 * (pm25 / 100) + 0.4 * (abs(temp - 22) / 20)
Risk Categories
Risk Level	Score Range	Recommendation
Low Risk	< 30	✅ Good for outdoor activities
Medium Risk	30 - 70	⚠️ Consider mask if sensitive
High Risk	> 70	🔴 Avoid prolonged outdoor exposure
2. Feature Engineering
Moving average (window = 3)

Time index encoding

Risk score normalization (0–100 scale)

Binary classification labels for logistic regression

🤖 Models
Model	Type	Purpose
Linear Regression	Regression	Short-term forecasting
Prophet (Meta)	Time-series	Trend + seasonality modeling
Logistic Regression	Classification	Health risk prediction
Baseline Mean	Statistical	Benchmark comparison
📈 Evaluation Metrics
MAE (Mean Absolute Error)

RMSE (Root Mean Squared Error)

R² Score

Accuracy (classification)

Confusion Matrix

All metrics are computed dynamically in the Streamlit dashboard.

📊 Key Findings
PM2.5 is the strongest contributor to health risk estimation

Temperature has a secondary but non-negligible effect

Linear Regression performs well for short-term prediction but fails under nonlinear variation

Prophet provides smoother forecasts but does not significantly outperform linear models on limited datasets

The risk scoring system effectively translates environmental data into interpretable health insights

🔬 Key Insight
This system demonstrates that PM2.5 has a consistently stronger impact on health risk scores compared to temperature across all three cities, suggesting air pollution is the dominant driver of short-term environmental health risk.

📉 Limitations
Limited number of cities (n = 3)

Short observation period

No external ground-truth health validation

API dependency for real-time data

🚀 Future Work
Expand dataset to 30+ global cities

Integrate LSTM-based deep learning models

Add SHAP explainability for model interpretation

Automate data collection using scheduled pipelines

Incorporate satellite-based pollution datasets

Deploy as real-time web service (API + frontend)

🖥️ System Architecture
text
API Layer → Data Collection → Processing → Machine Learning Models → Streamlit Dashboard
⚡ Quick Start
bash
git clone https://github.com/yubi-26/climate-intelligence-platform.git
cd climate-intelligence-platform

pip install -r requirements.txt

python fetch_data.py

streamlit run dashboard.py
📦 Requirements
txt
requests
streamlit
pandas
plotly
numpy
scikit-learn
prophet
matplotlib
📚 Data Sources
Open-Meteo API: https://open-meteo.com

WAQI API: https://aqicn.org/api/

🧾 Conclusion
This project demonstrates an end-to-end pipeline for environmental data-driven health risk modeling. It integrates real-world APIs, machine learning models, and interactive visualization into a unified system.

The framework is extensible and suitable for environmental analytics, urban computing, and data science research applications.

👤 Author
Data Science & AI Portfolio Project
Focus: Environmental Intelligence, Time-Series Modeling, Machine Learning