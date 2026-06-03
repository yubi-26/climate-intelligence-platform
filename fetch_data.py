import requests
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WAQI token
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

if not WAQI_TOKEN:
    print("WARNING: WAQI_TOKEN not found in .env file")
    WAQI_TOKEN = "demo"

# Cities
cities = {
    "tokyo": {"lat": 35.69, "lon": 139.69, "waqi_name": "tokyo"},
    "beijing": {"lat": 39.90, "lon": 116.40, "waqi_name": "beijing"},
    "bangkok": {"lat": 13.73, "lon": 100.50, "waqi_name": "bangkok"},
    "shanghai": {"lat": 31.23, "lon": 121.47, "waqi_name": "shanghai"},
    "jakarta": {"lat": -6.21, "lon": 106.85, "waqi_name": "jakarta"},
}

results = []

print("=" * 60)
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data collection started")
print("=" * 60)

for name, info in cities.items():

    try:
        # Temperature
        temp_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={info['lat']}"
            f"&longitude={info['lon']}"
            f"&current=temperature_2m"
        )

        temp_res = requests.get(temp_url, timeout=10)
        temp_data = temp_res.json()

        temp = temp_data["current"]["temperature_2m"]

        # PM2.5
        pm_url = (
            f"https://api.waqi.info/feed/"
            f"{info['waqi_name']}/?token={WAQI_TOKEN}"
        )

        pm_res = requests.get(pm_url, timeout=10)
        pm_data = pm_res.json()

        pm25 = 0

        if (
            pm_data.get("status") == "ok"
            and "pm25" in pm_data["data"].get("iaqi", {})
        ):
            pm25 = pm_data["data"]["iaqi"]["pm25"]["v"]

        results.append(
            {
                "city": name,
                "temperature": temp,
                "pm25": pm25,
                "timestamp": datetime.now().isoformat(),
            }
        )

        print(
            f"SUCCESS | {name:<10} | "
            f"Temp={temp:.1f} C | "
            f"PM2.5={pm25}"
        )

    except requests.exceptions.Timeout:
        print(f"TIMEOUT | {name}")

    except Exception as e:
        print(f"ERROR   | {name} | {e}")

# Save CSV
if results:

    file_exists = os.path.isfile("climate_data.csv")

    with open(
        "climate_data.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "city",
                "temperature",
                "pm25",
                "timestamp",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(results)

    print("=" * 60)
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"Data saved successfully ({len(results)} records)"
    )
    print("=" * 60)

else:

    print("=" * 60)
    print("No data collected")
    print("=" * 60)
