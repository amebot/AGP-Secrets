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
        
        # 1. ログイン画面へ移動
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        try:
            # 2. 全てのフレームをチェックして入力
            found = False
            for frame in page.frames:
                # ID入力欄（type="text"）を探す
                user_input = frame.locator('input[type="text"]').first
                if user_input.count() > 0:
                    user_input.fill(os.environ["AG_ID"])
                    # パスワード入力欄を探して入力
                    pass_input = frame.locator('input[type="password"]').first
                    pass_input.fill(os.environ["AG_PASS"])
                    
                    # 【重要】ボタンをクリックせず、Enterキーを送信する
                    pass_input.press("Enter")
                    found = True
                    print("Enterキーで送信しました")
                    break
            
            if not found:
                send_line("\n【AGエラー】\n入力欄が画面上に見つかりませんでした。")
                return

            # 3. ログイン後のページ（index.htmlなど）への遷移を待つ
            # どのページに飛んでもいいように、少し長めに（20秒）待ちます
            page.wait_for_timeout(10000) 
            
            # 4. 結果判定
            current_url = page.url
            if "login" in current_url:
                send_line(f"\n【AG失敗】\nログインできませんでした。\nID/PASSが違うか、拒否されています。\n現在URL: {current_url}")
            else:
                content = page.locator('body').inner_text()
                send_line(f"\n【AG成功！】\nログインに成功しました！\n現在URL: {current_url}\n監視を開始します。")
                # 内容を保存
                with open("last_content.txt", "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            send_line(f"\n【AG実行エラー】\n詳細: {str(e)}")
                
        browser.close()

if __name__ == "__main__":
    main()
