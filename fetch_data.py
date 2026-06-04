import requests
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

load_dotenv()

WAQI_TOKEN = os.getenv("WAQI_TOKEN")

if not WAQI_TOKEN:
    print("⚠️ WARNING: WAQI_TOKEN not found in .env file")
    WAQI_TOKEN = "demo"

# 15都市のデータを収集
cities = {
    # === アジア ===
    "tokyo": {"lat": 35.69, "lon": 139.69, "waqi_name": "tokyo"},
    "beijing": {"lat": 39.90, "lon": 116.40, "waqi_name": "beijing"},
    "bangkok": {"lat": 13.73, "lon": 100.50, "waqi_name": "bangkok"},
    "hanoi": {"lat": 21.03, "lon": 105.85, "waqi_name": "hanoi"},      # ← ホーチミン市→ハノイ
    "seoul": {"lat": 37.57, "lon": 126.98, "waqi_name": "seoul"},
    "delhi": {"lat": 28.61, "lon": 77.23, "waqi_name": "delhi"},
    "singapore": {"lat": 1.35, "lon": 103.82, "waqi_name": "singapore"},
    "dhaka": {"lat": 23.81, "lon": 90.41, "waqi_name": "dhaka"},        # ← カトマンズ→ダッカ
    "ulaanbaatar": {"lat": 47.92, "lon": 106.92, "waqi_name": "ulaanbaatar"},
    
    # === ヨーロッパ ===
    "berlin": {"lat": 52.52, "lon": 13.40, "waqi_name": "berlin"},
    "london": {"lat": 51.51, "lon": -0.13, "waqi_name": "london"},
    "reykjavik": {"lat": 64.15, "lon": -21.94, "waqi_name": "reykjavik"},
    
    # === 北アメリカ ===
    "new_york": {"lat": 40.71, "lon": -74.01, "waqi_name": "new-york"},
    
    # === 南半球 ===
    "sydney": {"lat": -33.87, "lon": 151.21, "waqi_name": "sydney"},
    "nairobi": {"lat": -1.29, "lon": 36.82, "waqi_name": "nairobi"},
}

PM25_MIN = 0
PM25_MAX = 500

results = []

print("=" * 60)
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data collection started ({len(cities)} cities)")
print("=" * 60)

for name, info in cities.items():
    try:
        # 気温データ取得
        temp_url = (f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={info['lat']}&longitude={info['lon']}&current=temperature_2m")
        temp_res = requests.get(temp_url, timeout=10)
        temp_res.raise_for_status()
        temp_data = temp_res.json()
        temp = temp_data["current"]["temperature_2m"]

        # PM2.5データ取得
        pm_url = f"https://api.waqi.info/feed/{info['waqi_name']}/?token={WAQI_TOKEN}"
        pm_res = requests.get(pm_url, timeout=10)
        pm_data = pm_res.json()

        pm25 = None
        if pm_data.get("status") == "ok":
            iaqi = pm_data["data"].get("iaqi", {})
            if "pm25" in iaqi:
                pm25 = iaqi["pm25"]["v"]

        # 異常値チェック
        if pm25 is None:
            print(f"⚠️ SKIP | {name:<15} | No PM2.5 data")
            continue

        if pm25 < PM25_MIN or pm25 > PM25_MAX:
            print(f"⚠️ SKIP | {name:<15} | 異常値: PM2.5={pm25}")
            continue

        results.append({
            "city": name,
            "temperature": temp,
            "pm25": pm25,
            "timestamp": datetime.now().isoformat(),
        })

        print(f"✅ SUCCESS | {name:<15} | Temp={temp:.1f}°C | PM2.5={pm25:.0f}")

    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT | {name:<15} | API応答なし（スキップ）")
    except Exception as e:
        print(f"❌ ERROR | {name:<15} | {e}")

# CSV保存
if results:
    file_exists = os.path.isfile("climate_data.csv")

    with open("climate_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["city", "temperature", "pm25", "timestamp"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
          f"✅ Data saved ({len(results)}/{len(cities)} records)")
    print(f"   Total records in CSV: {sum(1 for _ in open('climate_data.csv')) - 1}")
    print("=" * 60)
else:
    print("=" * 60)
    print("⚠️ No valid data collected")
    print("=" * 60)