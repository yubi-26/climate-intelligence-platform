\# Climate Intelligence Platform



Real-time environmental dashboard for Tokyo, Beijing, and Bangkok.



\## Current Progress ✅



\- 🌡️ Real-time temperature fetching from Open-Meteo API

\- ✅ Tokyo temperature data confirmed (17-18°C range as of today)

\- ✅ Git repository setup with Python .gitignore



\## In Progress 🚧



\- 📝 English README (this file)

\- 🔑 WAQI API token acquisition for PM2.5

\- 💾 CSV data logging structure



\## Next Steps



\- PM2.5 data integration

\- Health Risk Score implementation (PM2.5 + temperature)

\- Streamlit dashboard setup



\## Tech Stack



\- Python + Requests (data fetching)

\- Open-Meteo API (temperature)

\- WAQI API (air quality - planned)



\## Quick Start



```bash

git clone https://github.com/yubi-26/climate-intelligence-platform.git

cd climate-intelligence-platform

pip install requests

python -c "import requests; print(requests.get('https://api.open-meteo.com/v1/forecast?latitude=35.69\&longitude=139.69\&hourly=temperature\_2m').json()\['hourly']\['temperature\_2m']\[:5])"

