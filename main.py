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
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        
        # 1. ログインページへ移動
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")
        time.sleep(2) # 読み込み待ち

        try:
            # 2. 【最強の力技】ページ内の「全フレーム」をスキャンして入力
            found = False
            all_frames = page.frames
            print(f"検知したフレーム数: {len(all_frames)}")

            for f in all_frames:
                # フレーム内の入力欄を探す
                u_field = f.locator('input[type="text"], input[name*="id"], input[name*="user"]').first
                p_field = f.locator('input[type="password"]').first
                
                if u_field.count() > 0:
                    print(f"フレーム '{f.name}' 内に入力欄を発見しました")
                    u_field.fill(os.environ["AG_ID"])
                    p_field.fill(os.environ["AG_PASS"])
                    
                    # ログインボタン（画像ボタンや通常ボタン）を探してクリック
                    btn = f.locator('input[type="submit"], input[type="image"], button, a.btn').first
                    if btn.count() > 0:
                        btn.click()
                    else:
                        p_field.press("Enter")
                    found = True
                    break
            
            if not found:
                send_line("\n【AG通知】\n入力欄が一つも見つかりませんでした。サイト構造が大幅に変わった可能性があります。")
                return

            # 3. 遷移をじっくり待つ
            time.sleep(10) 
            
            # 4. 結果判定
            if "login" in page.url:
                # 失敗した時の「今のURL」を詳細に取得
                send_line(f"\n【AG最終失敗】\nやはりログインできません。\n現在のURL: {page.url}\n※ID/PASSがSecretsに正しく登録されているか再確認してください。")
            else:
                send_line(f"\n【AG成功！】\nおめでとうございます！ログインに成功しました！\n監視を開始します。\n現在URL: {page.url}")
                content = page.locator('body').inner_text()
                with open("last_content.txt", "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            send_line(f"\n【AG実行エラー】\n{str(e)}")
                
        browser.close()

if __name__ == "__main__":
    main()
