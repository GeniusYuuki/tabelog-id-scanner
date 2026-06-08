Python
import requests
import time
import random
import json
import os

# 💡 設定：どのIDから、何件先までを監視するか
BASE_ID = 13323101
CHECK_RANGE = 50 # 13323101 から 50件先まで（13323151まで）を監視

DATA_FILE = "history.json"

def load_history():
    """過去に発見したお店の履歴を読み込む"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    """発見したお店の履歴を保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def scan_job():
    """1回分のスキャン処理"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-JP;q=0.9,ja;q=0.8"
    }
    
    # 過去の履歴を読み込み
    history = load_history()
    new_discoveries = {}
    
    start_id = BASE_ID + 1
    end_id = BASE_ID + CHECK_RANGE
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 連番スキャンを開始します... (ID: {start_id} 〜 {end_id})")
    
    for shop_id in range(start_id, end_id + 1):
        str_id = str(shop_id)
        
        # 💡 効率化：すでに過去に「発見済（200）」のIDなら、アクセスせずにスキップ
        if str_id in history:
            continue
            
        url = f"https://tabelog.com/tokyo/A1317/A131701/{shop_id}"
        
        try:
            # 1件ごとの待機（食べログのブロックを避けるため非常に重要）
            time.sleep(random.uniform(5, 10))
            
            # リダイレクトを許可してページを確認
            res = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            if res.status_code == 200:
                # 🌟 過去になく、今回新しくページが「公開」された場合（差分）
                print(f"\n★【新着】新店ページが公開されました！ (ID: {shop_id})")
                print(f"URL: {res.url}")
                print("-" * 40)
                
                # 履歴と新着リストに記録
                history[str_id] = res.url
                new_discoveries[str_id] = res.url
                
            elif res.status_code == 404:
                # まだ非公開、または存在しない場合は何も出力せずスルー
                pass
                
            elif res.status_code in (403, 429):
                print(f"⚠️ 食べログからアクセス制限（{res.status_code}）を受けました。今回のスキャンを中断します。")
                break
                
        except Exception as e:
            print(f"エラー発生 (ID: {shop_id}): {e}")
            
    # 新しい発見（差分）があった場合のみ、history.jsonを更新して保存
    if new_discoveries:
        save_history(history)
        print(f"今回のスキャン完了: 新たに {len(new_discoveries)} 件を history.json に蓄積しました。")
    else:
        print("今回のスキャン完了: 新しい更新（新店の公開）はありませんでした。")

def main():
    print("==============================================")
    print(" 食べログ連番・新店公開 24時間監視スクリプト 起動")
    print("==============================================")
    
    while True:
        # スキャンを実行
        scan_job()
        
        # 💡 1時間（3600秒）待機してループ
        print("\n次の定期スキャンまで【1時間】待機します...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
