import csv
from datetime import datetime
import random

cities = ["tokyo", "beijing", "bangkok"]
results = []

for city in cities:
    temp = random.uniform(15, 35)
    pm25 = random.randint(10, 100)
    results.append({
        "city": city,
        "temperature": round(temp, 1),
        "pm25": pm25,
        "timestamp": datetime.now().isoformat()
    })
    print(f"{city}: {round(temp,1)}°C, PM2.5={pm25}")

import os
file_exists = os.path.isfile("climate_data.csv")

with open("climate_data.csv", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["city", "temperature", "pm25", "timestamp"])
    if not file_exists:
        writer.writeheader()
    writer.writerows(results)

print("モックデータを追加しました")