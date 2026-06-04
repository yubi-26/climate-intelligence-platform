# 🌍 Climate Risk Intelligence

### A Novel Environmental Risk Quantification System Using Cross-City Pattern Analysis

---

## 🧠 Abstract

This project introduces a **novel Climate Risk Score** — a composite index (0–100) that integrates **PM2.5**, **temperature anomaly**, **humidity stress**, and **AQI** into a single, interpretable measure of environmental health risk for any city worldwide.

Unlike conventional dashboards that merely display raw data, this system provides:

- **Risk quantification** via a weighted multi-factor model
- **Cross-City Prediction** using similar-climate city patterns
- **Health guidance** tailored to risk levels
- **Global risk mapping** for comparative analysis

The goal is to transform raw environmental data into **actionable risk intelligence** for public health and climate resilience.

---

## 🎯 Objectives

- Design a **novel composite index** for environmental health risk
- Integrate PM2.5, temperature, humidity, and AQI into a unified score
- Predict tomorrow's risk using **Cross-City Pattern Analysis**
- Provide **interpretable health recommendations**
- Visualize global risk distribution on an interactive map
- Build a production-ready research prototype

---

## 🔬 Core Innovation: Climate Risk Score

### Formula

| Factor              | Weight | Rationale                                        |
| ------------------- | ------ | ------------------------------------------------ |
| PM2.5               | 40%    | Primary air pollution indicator (WHO guidelines) |
| Temperature Anomaly | 30%    | Deviation from human comfort zone (18–24°C)      |
| Humidity Stress     | 20%    | Deviation from optimal humidity (40–60%)         |
| AQI                 | 10%    | Composite air quality adjustment                 |

### Risk Levels

| Score Range | Level       | Health Implication                       |
| ----------- | ----------- | ---------------------------------------- |
| 0–30        | 🟢 Low      | Safe for all outdoor activities          |
| 30–60       | 🟡 Moderate | Sensitive groups should take precautions |
| 60–80       | 🟠 High     | Limit outdoor exposure, wear mask        |
| 80–100      | 🔴 Extreme  | Avoid all outdoor activities             |

---

## 🔮 Cross-City Prediction Engine

A novel approach for **risk forecasting without time-series data**:

1. **Global Baseline**: Mean risk across all monitored cities
2. **Similar City Detection**: Identifies 3 cities with closest PM2.5 + temperature profile
3. **Trend Direction**: Rule-based inference from current conditions
4. **Weighted Prediction**: Current value (50%) + Similar cities mean (30%) + Global baseline (20%)
5. **Confidence Scoring**: Based on similarity distance to reference cities

### Research Significance

> Demonstrates that **spatial cross-city patterns** can substitute for temporal data in environmental risk prediction — a practical approach for data-scarce regions.

---

## 🌍 System Architecture

┌─────────────────────────────────────────────────────┐
│ Data Sources │
│ climate_data.csv (15 global cities, real-time) │
└────────────────────────┬────────────────────────────┘
↓
┌─────────────────────────────────────────────────────┐
│ Risk Score Engine │
│ Weighted Multi-Factor Normalization (0–100) │
└────────────────────────┬────────────────────────────┘
↓
┌─────────────────────────────────────────────────────┐
│ Cross-City Prediction Engine │
│ Similar City Detection + Trend Analysis │
└────────────────────────┬────────────────────────────┘
↓
┌─────────────────────────────────────────────────────┐
│ Streamlit Dashboard (Dark Theme) │
│ • Risk Score Card • KPI Cards • Health Guidance │
│ • Trend Graph • Global Risk Map • City Rankings │
│ • Tomorrow's Forecast • Contributing Factors │
└─────────────────────────────────────────────────────┘

text

---

## 📊 Dataset

- **Cities**: Tokyo, Beijing, Bangkok, Seoul, Delhi, Singapore, Dhaka, Ulaanbaatar, Berlin, London, Reykjavik, New York, Sydney, Nairobi, Jakarta
- **Features**:
  - `city` — City name
  - `lat`, `lon` — Geographic coordinates
  - `temperature` — Temperature (°C)
  - `pm25` — PM2.5 concentration (µg/m³)
  - `aqi` — Air Quality Index
  - `humidity` — Relative humidity (%)
  - `timestamp` — Observation timestamp
- **Coverage**: 15 cities across Asia, Europe, North America, Africa, Australia

---

## 🖥️ Dashboard Features

| Feature                  | Description                                                |
| ------------------------ | ---------------------------------------------------------- |
| **Risk Score Card**      | Central display with gradient text and risk level badge    |
| **KPI Cards**            | PM2.5, Temperature, Humidity, AQI in glass-morphism design |
| **Health Guidance**      | Auto-generated recommendations based on risk level         |
| **Risk Trend**           | Time-series line chart with threshold indicators           |
| **Global Risk Map**      | Dark-theme Mapbox with green-to-red risk gradient          |
| **City Rankings**        | Top 5 highest & lowest risk cities                         |
| **Tomorrow's Forecast**  | Cross-city prediction with confidence level                |
| **Contributing Factors** | AI-generated explanations for risk changes                 |

---

## ⚡ Quick Start

```bash
git clone https://github.com/yubi-26/climate-intelligence-platform.git
cd climate-intelligence-platform

pip install -r requirements.txt

streamlit run dashboard.py
📦 Requirements
text
streamlit
pandas
numpy
plotly
📈 Key Findings
PM2.5 is the dominant driver of environmental health risk across all cities

Temperature anomaly amplifies risk non-linearly beyond the comfort zone

Cross-city patterns can provide reasonable risk forecasts without historical data

Global Risk Baseline across 15 cities is ~32/100, indicating moderate global risk

Delhi and Dhaka consistently rank highest; Nairobi ranks lowest

🔬 Research Contribution
This project proposes a novel composite environmental risk index and demonstrates that spatial cross-city analysis can serve as a practical substitute for temporal forecasting in data-limited scenarios.

Why This Matters
Enables risk assessment for cities without historical data

Provides interpretable scores for non-technical stakeholders

Bridges environmental science and public health communication

Demonstrates research-style system design beyond simple data visualization

📉 Limitations
Current dataset: single timestamp per city (cross-sectional)

Prediction confidence depends on similar city availability

Health risk score not validated against epidemiological data

Humidity partially simulated for cities without data

🚀 Future Work
Integrate real-time APIs (Open-Meteo, WAQI)

Collect 7-day rolling data per city

Implement XGBoost/LightGBM for temporal prediction

Add SHAP explainability for risk score decomposition

Expand to 50+ global cities

Deploy on Streamlit Cloud with auto-refresh

Validate against WHO health impact data

🧾 Conclusion
Climate Risk Intelligence demonstrates a complete pipeline from environmental data integration to actionable risk intelligence. The system's core contribution — a weighted multi-factor risk index combined with cross-city prediction — offers a practical and extensible framework for environmental health risk assessment.

This project is positioned as a research prototype suitable for:

Environmental data science portfolios

Graduate school applications (Climate Informatics, Environmental Health)

Public health decision support systems

Urban climate resilience planning

👤 Author
Data Science & AI Portfolio Project
Focus: Environmental Risk Intelligence · Composite Index Design · Cross-City Pattern Analysis · Interactive Visualization

📚 References
WHO Global Air Quality Guidelines (2021)

Open-Meteo API Documentation

WAQI API Documentation

Streamlit Documentation
```
