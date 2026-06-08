import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os

# 💡 設定
BASE_ID = 13323101
CHECK_RANGE = 50 

DATA_FILE = "history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def scan_job():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-JP;q=0.9,ja;q=0.8"
    }
    
    history = load_history()
    new_discoveries = {}
    
    start_id = BASE_ID + 1
    end_id = BASE_ID + CHECK_RANGE
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 連番スキャンを開始します... (ID: {start_id} 〜 {end_id})")
    
    for i, shop_id in enumerate(range(start_id, end_id + 1), 1):
        str_id = str(shop_id)
        
        # 🌟 ここで進捗を表示
        print(f"[{i}/{CHECK_RANGE}] ID: {shop_id} をチェック中...", flush=True)
        
        if str_id in history:
            print("  -> スキップ（確認済）", flush=True)
            continue
            
        url = f"https://tabelog.com/tokyo/A1317/A131701/{shop_id}"
        
        try:
            time.sleep(random.uniform(5, 10))
            
            # timeoutを10秒に設定し、フリーズを防止
            res = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")
                
                # 店名と駅名の抽出
                name_tag = soup.select_one("h2.display-name")
                shop_name = name_tag.get_text(strip=True) if name_tag else "店名不明"
                
                title_text = soup.title.get_text(strip=True) if soup.title else ""
                station_name = "駅不明"
                if " - " in title_text and "/" in title_text:
                    try:
                        station_name = title_text.split(" - ")[-1].split("/")[0].strip()
                    except:
                        pass
                
                print(f"  -> ★【新着発見！】 {shop_name} ({station_name})", flush=True)
                
                shop_data = {"url": res.url, "name": shop_name, "station": station_name}
                history[str_id] = shop_data
                new_discoveries[str_id] = shop_data
                
            elif res.status_code == 404:
                print("  -> まだ公開されていません (404)", flush=True)
                
            elif res.status_code in (403, 429):
                print(f"⚠️ 食べログからアクセス制限（{res.status_code}）を受けました。", flush=True)
                break
                
        except Exception as e:
            # タイムアウト等で失敗した場合もログに出す
            print(f"  -> 通信エラー発生: {e}", flush=True)
            
    if new_discoveries:
        save_history(history)
        print(f"今回のスキャン完了: 新たに {len(new_discoveries)} 件を記録しました。")
    else:
        print("今回のスキャン完了: 新しい更新はありませんでした。")

def main():
    print("==============================================")
    print(" 食べログ連番・新店公開 スキャン実行")
    print("==============================================")
    scan_job()

if __name__ == "__main__":
    main()
