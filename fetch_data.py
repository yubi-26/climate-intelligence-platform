import requests
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# WAQIトークン（環境変数から取得）
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

if not WAQI_TOKEN:
    print("⚠️ 警告: WAQI_TOKENが設定されていません。.envファイルを確認してください。")
    WAQI_TOKEN = "demo"  # デモモード

# 都市の緯度経度（5都市に拡張）
cities = {
    "tokyo": {"lat": 35.69, "lon": 139.69, "waqi_name": "tokyo"},
    "beijing": {"lat": 39.90, "lon": 116.40, "waqi_name": "beijing"},
    "bangkok": {"lat": 13.73, "lon": 100.50, "waqi_name": "bangkok"},
    "shanghai": {"lat": 31.23, "lon": 121.47, "waqi_name": "shanghai"},
    "jakarta": {"lat": -6.21, "lon": 106.85, "waqi_name": "jakarta"},
}

results = []

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] データ取得開始")

for name, info in cities.items():
    try:
        # 気温を取得（Open-Meteo API）
        temp_url = f"https://api.open-meteo.com/v1/forecast?latitude={info['lat']}&longitude={info['lon']}&current=temperature_2m"
        temp_res = requests.get(temp_url, timeout=10)
        temp_data = temp_res.json()
        temp = temp_data['current']['temperature_2m']
        
        # PM2.5を取得（WAQI API）
        pm_url = f"https://api.waqi.info/feed/{info['waqi_name']}/?token={WAQI_TOKEN}"
        pm_res = requests.get(pm_url, timeout=10)
        pm_data = pm_res.json()
        
        pm25 = None
        if pm_data.get('status') == 'ok' and 'pm25' in pm_data['data'].get('iaqi', {}):
            pm25 = pm_data['data']['iaqi']['pm25']['v']
        
        results.append({
            "city": name,
            "temperature": temp,
            "pm25": pm25 if pm25 else 0,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"  ✅ {name}: {temp}°C, PM2.5={pm25 if pm25 else 'N/A'}")
        
    except requests.exceptions.Timeout:
        print(f"  ⏰ タイムアウト: {name} はスキップしました")
    except Exception as e:
        print(f"  ❌ エラー: {name} - {e}")

# CSVに追記保存
if results:
    file_exists = os.path.isfile("climate_data.csv")
    
    with open("climate_data.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["city", "temperature", "pm25", "timestamp"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {len(results)}件のデータを保存しました")
else:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ データが取得できませんでした")