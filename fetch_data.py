"""
Climate Intelligence Platform - Data Fetching Script (Final Version)
Fetches temperature and PM2.5/AQI data from Open-Meteo and WAQI APIs
"""

import requests
import time
import csv
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# =========================
# 設定
# =========================

# WAQIトークン（.envまたはSecretsから取得）
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

if not WAQI_TOKEN or WAQI_TOKEN == "demo":
    print("⚠️ WARNING: WAQI_TOKEN not found or using demo mode")
    print("   Please set WAQI_TOKEN in .env file or Streamlit Secrets")

# APIリクエストヘッダー（メールアドレスなしのシンプル版）
HEADERS = {
    "User-Agent": "Climate-Intelligence-Platform/1.0"
}

# データ範囲チェック
TEMP_MIN = -60
TEMP_MAX = 60
PM25_MIN = 0
PM25_MAX = 500

# リクエスト間隔（秒）- レート制限対策
REQUEST_INTERVAL = 1.0

# =========================
# 都市定義（15都市）
# =========================
cities = {
    # === アジア ===
    "tokyo": {"lat": 35.69, "lon": 139.69, "waqi_name": "tokyo"},
    "beijing": {"lat": 39.90, "lon": 116.40, "waqi_name": "beijing"},
    "bangkok": {"lat": 13.73, "lon": 100.50, "waqi_name": "bangkok"},
    "seoul": {"lat": 37.57, "lon": 126.98, "waqi_name": "seoul"},
    "delhi": {"lat": 28.61, "lon": 77.23, "waqi_name": "delhi"},
    "singapore": {"lat": 1.35, "lon": 103.82, "waqi_name": "singapore"},
    "dhaka": {"lat": 23.81, "lon": 90.41, "waqi_name": "dhaka"},
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
    "jakarta": {"lat": -6.21, "lon": 106.85, "waqi_name": "jakarta"},
}

# =========================
# 重複チェック（効率化版）
# =========================
def load_existing_data(csv_file):
    """既存のCSVデータを読み込む（1回だけ実行）"""
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception:
        return None

def is_duplicate_fast(existing_df, city, timestamp, tolerance_seconds=30):
    """既存データフレームを使って重複チェック（高速）"""
    if existing_df is None:
        return False
    
    df_city = existing_df[existing_df["city"] == city]
    if df_city.empty:
        return False
    
    latest_timestamp = df_city["timestamp"].max()
    current_timestamp = pd.to_datetime(timestamp)
    
    diff_seconds = abs((current_timestamp - latest_timestamp).total_seconds())
    
    return diff_seconds < tolerance_seconds

# =========================
# データ取得開始
# =========================

print("=" * 70)
print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data collection started ({len(cities)} cities)")
print(f"WAQI Token: {'✅ Valid' if WAQI_TOKEN and WAQI_TOKEN != 'demo' else '⚠️ Demo mode'}")
print("=" * 70)

# 既存データを1回だけ読み込み（効率化）
existing_df = load_existing_data("climate_data.csv")

results = []
success_count = 0
skip_count = 0
error_count = 0

for idx, (name, info) in enumerate(cities.items(), 1):
    try:
        print(f"\n[{idx}/{len(cities)}] Processing {name}...")
        
        # 気温データ取得
        temp_url = (f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={info['lat']}&longitude={info['lon']}&current=temperature_2m")
        
        temp_res = requests.get(temp_url, headers=HEADERS, timeout=15)
        temp_res.raise_for_status()
        temp_data = temp_res.json()
        temp = temp_data["current"]["temperature_2m"]
        
        # 気温異常値チェック
        if temp < TEMP_MIN or temp > TEMP_MAX:
            print(f"   ⚠️ SKIP | 異常気温: {temp}°C")
            skip_count += 1
            continue

        # PM2.5データ取得（WAQI API）
        pm_url = f"https://api.waqi.info/feed/{info['waqi_name']}/?token={WAQI_TOKEN}"
        pm_res = requests.get(pm_url, headers=HEADERS, timeout=15)
        pm_data = pm_res.json()

        pm25 = None
        aqi = None
        
        if pm_data.get("status") == "ok":
            data = pm_data.get("data", {})
            iaqi = data.get("iaqi", {})
            
            if "pm25" in iaqi:
                pm25 = iaqi["pm25"]["v"]
            aqi = data.get("aqi")

        # PM2.5異常値チェック
        if pm25 is None:
            print(f"   ⚠️ SKIP | PM2.5データなし")
            skip_count += 1
            continue

        if pm25 < PM25_MIN or pm25 > PM25_MAX:
            print(f"   ⚠️ SKIP | 異常値: PM2.5={pm25}")
            skip_count += 1
            continue

        # 重複チェック（高速版）
        timestamp = datetime.now().isoformat()
        if is_duplicate_fast(existing_df, name, timestamp):
            print(f"   ⚠️ SKIP | 重複データ（30秒以内）")
            skip_count += 1
            continue

        # 正常データを保存
        record = {
            "city": name,
            "temperature": round(temp, 1),
            "pm25": round(pm25, 1),
            "aqi": aqi if aqi else None,
            "timestamp": timestamp,
        }
        results.append(record)

        print(f"   ✅ SUCCESS | Temp={temp:.1f}°C | PM2.5={pm25:.1f} | AQI={aqi if aqi else 'N/A'}")
        success_count += 1

    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT")
        error_count += 1
    except requests.exceptions.RequestException as e:
        print(f"   📡 NETWORK ERROR: {e}")
        error_count += 1
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        error_count += 1
    
    time.sleep(REQUEST_INTERVAL)

# =========================
# CSV保存
# =========================

if results:
    new_df = pd.DataFrame(results)
    new_df["timestamp"] = pd.to_datetime(new_df["timestamp"])
    
    if os.path.exists("climate_data.csv"):
        existing_df = pd.read_csv("climate_data.csv")
        existing_df["timestamp"] = pd.to_datetime(existing_df["timestamp"])
        
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["city", "timestamp"], keep="last")
        combined_df = combined_df.sort_values(["city", "timestamp"])
        combined_df.to_csv("climate_data.csv", index=False, encoding="utf-8")
        
        print("=" * 70)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Data saved")
        print(f"   New: {len(results)} | Total: {len(combined_df)} | Success: {success_count} | Skip: {skip_count} | Error: {error_count}")
        print("=" * 70)
    else:
        new_df.to_csv("climate_data.csv", index=False, encoding="utf-8")
        
        print("=" * 70)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ New file created")
        print(f"   Records: {len(results)} | Success: {success_count} | Skip: {skip_count} | Error: {error_count}")
        print("=" * 70)
else:
    print("=" * 70)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ No valid data collected")
    print(f"   Success: {success_count} | Skip: {skip_count} | Error: {error_count}")
    print("=" * 70)