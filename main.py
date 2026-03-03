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
        
        # 1. ログインページへ移動（読み込み完了を待つ）
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        # 2. 【修正】すべての「箱（フレーム）」の中から ID入力欄を探す
        target_field = None
        for frame in page.frames:
            try:
                # 0.5秒だけ探して、あれば採用する
                if frame.locator('input[name="user_id"]').count() > 0:
                    target_field = frame
                    break
            except:
                continue

        if target_field:
            try:
                # 3. 入力とログイン実行
                target_field.fill('input[name="user_id"]', os.environ["AG_ID"])
                target_field.fill('input[name="user_password"]', os.environ["AG_PASS"])
                target_field.click('input[type="submit"]')
                
                # 4. ログイン後の画面遷移を待つ
                page.wait_for_url("**/index.html", timeout=15000)
                
                # 5. 【テスト用】成功メッセージを送る
                send_line("\n【AG成功！】\nログインに成功しました。監視を開始します。")
                
                # 6. 内容取得（差分チェック用）
                content = page.locator('body').inner_text()
                cache_file = "last_content.txt"
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            except Exception as e:
                send_line(f"\n【AGエラー】\nログイン処理中に失敗しました: {str(e)}")
        else:
            send_line("\n【AGエラー】\n入力画面（フレーム）が見つかりませんでした。")

        browser.close()

if __name__ == "__main__":
    main()
