import os
import requests
import time
from playwright.sync_api import sync_playwright

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.environ['LINE_TOKEN']}"}
    payload = {"to": os.environ['LINE_USER_ID'], "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def main():
    with sync_playwright() as p:
        # 1. 人間が使っているブラウザ（Chrome）のふりをする設定
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        browser = p.chromium.launch(headless=True) # 実行は裏側で行う
        context = browser.new_context(user_agent=user_agent, viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print("サイトへ移動中...")
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        try:
            # 2. 全フレームを対象に入力欄を特定
            for frame in page.frames:
                user_field = frame.locator('input[type="text"], input[name*="id"]').first
                pass_field = frame.locator('input[type="password"]').first
                
                if user_field.count() > 0:
                    # 人間のように少しずつ入力する
                    user_field.fill(os.environ["AG_ID"])
                    time.sleep(1) # 1秒待つ
                    pass_field.fill(os.environ["AG_PASS"])
                    time.sleep(1)
                    
                    # 3. ボタンを名前やテキストで探してクリックする（Enterより確実）
                    login_btn = frame.locator('input[type="submit"], input[type="image"], button:has-text("ログイン")').first
                    if login_btn.count() > 0:
                        login_btn.click()
                    else:
                        pass_field.press("Enter")
                    break
            
            # 4. 遷移を待機（最大20秒）
            page.wait_for_timeout(10000) 
            
            if "login" in page.url:
                # 失敗時の画面の文字を詳しく取得してLINEに送る
                error_text = page.locator('body').inner_text()[:150]
                send_line(f"\n【AG失敗】\nログイン画面に戻されました。\n画面上の文字: {error_text}")
            else:
                send_line(f"\n【AG成功！】\nログイン成功！\n現在URL: {page.url}")
                content = page.locator('body').inner_text()
                with open("last_content.txt", "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            send_line(f"\n【AG実行エラー】\n{str(e)}")
                
        browser.close()

if __name__ == "__main__":
    main()
