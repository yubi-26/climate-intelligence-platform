import requests
from datetime import datetime
import csv
import os

# =========================
# CONFIGURATION
# =========================

WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo")

CITIES = {
    "tokyo": {"lat": 35.69, "lon": 139.69, "waqi": "tokyo"},
    "beijing": {"lat": 39.90, "lon": 116.40, "waqi": "beijing"},
    "bangkok": {"lat": 13.73, "lon": 100.50, "waqi": "bangkok"},
    "shanghai": {"lat": 31.23, "lon": 121.47, "waqi": "shanghai"},
    "jakarta": {"lat": -6.21, "lon": 106.85, "waqi": "jakarta"},
}

OUTPUT_FILE = "climate_data.csv"

# =========================
# START LOG
# =========================

print("=" * 60)
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data collection started")
print("=" * 60)

results = []

# =========================
# DATA COLLECTION LOOP
# =========================

for city, info in CITIES.items():
    try:
        # -------------------------
        # Temperature (Open-Meteo API)
        # -------------------------
        temp_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={info['lat']}&longitude={info['lon']}&current=temperature_2m"
        )

        temp_response = requests.get(temp_url, timeout=10)
        temp_response.raise_for_status()
        temperature = temp_response.json()["current"]["temperature_2m"]

        # -------------------------
        # Air Quality (WAQI API)
        # -------------------------
        pm_url = f"https://api.waqi.info/feed/{info['waqi']}/?token={WAQI_TOKEN}"
        pm_response = requests.get(pm_url, timeout=10)
        pm_data = pm_response.json()

        pm25 = 0
        if pm_data.get("status") == "ok":
            iaqi = pm_data.get("data", {}).get("iaqi", {})
            if "pm25" in iaqi:
                pm25 = iaqi["pm25"]["v"]

        # -------------------------
        # SAVE RECORD
        # -------------------------
        results.append({
            "city": city,
            "temperature": float(temperature),
            "pm25": float(pm25),
            "timestamp": datetime.now().isoformat()
        })

        print(f"SUCCESS | {city:<10} | Temp={temperature:.1f}°C | PM2.5={pm25}")

    except requests.exceptions.Timeout:
        print(f"TIMEOUT | {city}")
    except Exception as e:
        print(f"ERROR | {city} | {str(e)}")

# =========================
# SAVE TO CSV
# =========================

if results:
    file_exists = os.path.isfile(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["city", "temperature", "pm25", "timestamp"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(results)

    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved successfully ({len(results)} records)")
    print("=" * 60)

else:
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: No data collected")
    print("=" * 60)