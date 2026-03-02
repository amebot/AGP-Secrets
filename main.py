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
        # ブラウザを起動（少し動作を安定させる設定を追加）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ログインページへ移動
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        # 1. 実際のサイトの入力項目名に合わせて修正
        # ID入力欄の名前を 'user_id' に修正
        page.fill('input[name="user_id"]', os.environ["AG_ID"])
        # パスワード入力欄の名前を 'user_password' に修正
        page.fill('input[name="user_password"]', os.environ["AG_PASS"])
        
        # 2. ログインボタンをクリック
        page.click('input[type="submit"]')
        
        # 3. ログイン後のページに移動したか確認
        page.wait_for_url("https://agp.jp.net/staffroom/index.html", timeout=10000)
        
        # 4. ページ全体の文字を取得
        content = page.locator('body').inner_text() 
        
        # 差分保存用のファイル読み込み（エラー回避用）
        cache_file = "last_content.txt"
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                last_content = f.read()
        else:
            last_content = ""

        # 内容が変わっていたらLINE
        if content != last_content:
            send_line("\n【AG更新通知】\nお仕事情報が更新されました！\nhttps://agp.jp.net/staffroom/index.html")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
                
        browser.close()

if __name__ == "__main__":
    main()
