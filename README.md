# 🌍 Climate Risk Intelligence

### Real-time Environmental Risk Quantification & Forecasting Platform

<p align="center">
  <i>Turning environmental data into actionable risk intelligence.</i>
</p>

---

## 🧠 Overview

Climate Risk Intelligence is a research prototype that quantifies and visualizes environmental health risk across 15 global cities using a **novel composite index**.

It combines:

- Air pollution data (PM2.5, AQI)
- Weather conditions (temperature, humidity)
- Weighted multi-factor risk scoring
- Cross-city similarity prediction
- Multi-period temporal forecasting

> The goal: transform raw environmental data into a **human-readable risk decision system**.

---

## 🔥 Key Features

### 🎯 Climate Risk Score Engine

Composite risk model based on PM2.5 (40%) + Temperature Anomaly (30%) + Humidity Deviation (20%) + AQI (10%). Outputs a **0–100 interpretable risk score**.

### 🗺 Global Risk Visualization

Interactive Mapbox-powered world map of 15 major cities with color-coded risk levels and real-time cross-region comparison.

### 📈 Temporal Risk Trend Analysis

48-hour simulated risk trajectory with seasonal + stochastic modeling. Threshold-based risk levels: Low → Moderate → High → Extreme.

### 🤖 Cross-City Prediction Engine

Similarity-weighted nearest-neighbor model that predicts tomorrow's risk **without requiring historical time-series data**. Confidence scoring (50–92%).

### 🧠 AI Insights Generator

Automatically generates city ranking insights, pollution deviation analysis, global comparison metrics, and risk contribution explanations.

### 📉 Multi-Period Forecasting

Predicts risk levels for 6h / 12h / 24h / 48h / 72h / 7d horizons.

---

## 🏗️ System Architecture

Data Layer → Processing Layer → Analytics Layer → Presentation Layer
(Synthetic + CSV) (Risk scoring, (Trend simulation, (Streamlit + Plotly)
normalization, cross-city pred,
similarity) forecast)

text

---

## 🧮 Risk Model

Risk Score = PM2.5×0.40 + Temp_Anomaly×0.30 + Humidity_Deviation×0.20 + AQI×0.10

text

Normalized to **0 (Safe) → 100 (Extreme Risk)** .

---

## 🌐 Tech Stack

| Layer         | Technology                     |
| ------------- | ------------------------------ |
| UI            | Streamlit                      |
| Data          | Pandas, NumPy                  |
| Visualization | Plotly, Mapbox                 |
| Fonts         | Syne, DM Sans, JetBrains Mono  |
| ML            | Similarity-weighted heuristics |

---

## 📊 Risk Levels

| Score  | Level       | Color                    |
| ------ | ----------- | ------------------------ |
| 0–34   | 🟢 Low      | Safe conditions          |
| 35–54  | 🟡 Moderate | Sensitive groups caution |
| 55–74  | 🟠 High     | Limit outdoor exposure   |
| 75–100 | 🔴 Extreme  | Avoid outdoor activities |

---

## ⚡ Quick Start

```bash
git clone https://github.com/[username]/climate-risk-intelligence.git
cd climate-risk-intelligence
pip install -r requirements.txt
streamlit run dashboard.py
📁 Project Structure
text
├── dashboard.py          # Main application
├── climate_data.csv      # Environmental dataset (15 cities)
├── requirements.txt      # Python dependencies
└── README.md
🚀 Future Work
Real-time API integration (Open-Meteo, WAQI)

LSTM-based deep learning forecasting

Satellite data fusion (MODIS, Sentinel-5P)

Email/Push alert system

Streamlit Cloud deployment

Expand to 50+ cities

🧠 Research Value
This project demonstrates:

Novel composite index design for environmental health

Spatial cross-city pattern analysis as a substitute for temporal data

Human-centered risk visualization with Decision-First design philosophy

Interpretable ML-inspired systems for public health applications

🎯 Design Philosophy
"Not just data. Decisions."

One screen = one narrative

Risk score as the primary visual anchor

All charts serve the main decision

Minimal cognitive load, maximum clarity

📌 Author
Built as a Climate Data Intelligence Research Prototype.

Focus: Environmental Analytics · Risk Quantification · AI-Assisted Decision Systems · Interactive Visualization

📄 License
MIT
```
