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
        
        # 1. 【最重要】ログインフォームが直接存在するURLへジャンプ
        # 外枠の login.html ではなく、中身の top.html を直接開きます
        print("ログインフォームへ直接アクセス中...")
        page.goto("https://agp.jp.net/staffroom/top.html", wait_until="networkidle")

        try:
            # 2. 入力欄を探して入力（name属性が user_id / user_password であることを想定）
            print("ログイン情報を入力中...")
            page.wait_for_selector('input[name="user_id"]', timeout=10000)
            page.fill('input[name="user_id"]', os.environ["AG_ID"])
            page.fill('input[name="user_password"]', os.environ["AG_PASS"])
            
            # 3. ログインボタンをクリック
            page.click('input[type="submit"]')
            
            # 4. ログイン後のメイン画面（index.html）に移動するのを待つ
            page.wait_for_url("**/index.html", timeout=15000)
            print("ログイン成功！")
            
            # 5. 内容を取得（お仕事情報の差分チェック用）
            content = page.locator('body').inner_text()
            
            # 6. 【テスト用】初回だけ必ずLINEを送る（成功確認のため）
            send_line("\n【AG成功！】\nログインに成功しました！\nこれでお仕事情報の監視ができるようになりました。")
            
            # 7. 内容を保存
            with open("last_content.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            # 失敗した場合はエラー内容をLINEに送る
            send_line(f"\n【AGエラー】\n実行中に失敗しました: {str(e)}")
                
        browser.close()

if __name__ == "__main__":
    main()
