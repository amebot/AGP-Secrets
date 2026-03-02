import os
import requests
from playwright.sync_api import sync_playwright

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['LINE_TOKEN']}"}
    payload = {"to": os.environ['LINE_USER_ID'], "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ログインページへ移動
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        # --- 【修正ポイント】フレームの中を探す ---
        # サイトの構造に合わせて、適切なフレームを取得します
        frame = page.frame(name="main") or page.main_frame
        
        # フレーム内の入力欄を探して入力
        try:
            # セレクター（探し方）をより確実に「input要素」に限定
            frame.wait_for_selector('input[name="user_id"]', timeout=10000)
            frame.fill('input[name="user_id"]', os.environ["AG_ID"])
            frame.fill('input[name="user_password"]', os.environ["AG_PASS"])
            frame.click('input[type="submit"]')
        except Exception as e:
            print(f"入力欄が見つかりませんでした: {e}")
            browser.close()
            return

        # ログイン後のページに移動したか確認
        try:
            page.wait_for_url("**/index.html", timeout=15000)
        except:
            print("ログイン後の画面遷移に失敗しました。")
            browser.close()
            return
        
        # ログイン後のコンテンツ取得
        content = page.locator('body').inner_text() 
        
        # 差分比較
        cache_file = "last_content.txt"
        last_content = open(cache_file).read() if os.path.exists(cache_file) else ""

        if content != last_content:
            send_line("\n【AG更新通知】\nお仕事情報が更新されました！\nhttps://agp.jp.net/staffroom/index.html")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
                
        browser.close()

if __name__ == "__main__":
    main()
