"""
自動データ取得スケジューラー
1時間ごとにfetch_data.pyを実行
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime

def fetch_data():
    print("\n" + "="*50)
    print(f"[{datetime.now()}] データ取得開始")
    print("="*50)

    try:
        result = subprocess.run(
            [sys.executable, "fetch_data.py"],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)

        if result.stderr:
            print("エラー:", result.stderr)

    except Exception as e:
        print("エラー:", e)

def main():
    print("スケジューラー起動（1時間ごと実行）")

    fetch_data()  # 初回実行

    schedule.every(1).hours.do(fetch_data)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()