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
        
        # 1. ログインページへ移動
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        try:
            # 2. 【修正】フレームを全無視して「画面上の全入力欄」を取得
            # サイト内のすべてのフレームをスキャンします
            for frame in page.frames:
                inputs = frame.locator('input[type="text"], input[type="password"]')
                if inputs.count() >= 2:
                    # 最初の入力欄にID、次をパスワードとみなして入力
                    inputs.nth(0).fill(os.environ["AG_ID"])
                    inputs.nth(1).fill(os.environ["AG_PASS"])
                    # 送信ボタン（submit）を探してクリック
                    frame.locator('input[type="submit"], button[type="submit"]').first.click()
                    break
            
            # 3. ログイン後の画面遷移を待つ
            page.wait_for_url("**/index.html", timeout=15000)
            
            # 4. 内容を取得（ここが重要）
            content = page.locator('body').inner_text()
            
            # 5. 【テスト用】成功通知
            send_line("\n【AG成功！】\nついにログインを突破しました！\n監視を継続します。")
            
            # 6. 内容保存
            with open("last_content.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            # エラーが出たら詳細をLINEへ
            send_line(f"\n【AG再エラー】\nログイン突破に失敗しました。\n内容: {str(e)}")
                
        browser.close()

if __name__ == "__main__":
    main()
