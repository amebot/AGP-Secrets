import os
import requests
import time
from playwright.sync_api import sync_playwright

def send_line(message):
    """LINEにメッセージを送信する関数"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['LINE_TOKEN']}"
    }
    payload = {
        "to": os.environ['LINE_USER_ID'],
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=payload)

def main():
    with sync_playwright() as p:
        # ブラウザ起動（少し動作をゆっくりにする設定を追加）
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            # 1. ログインページへ移動
            page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

            # 2. ログイン処理（全フレームをスキャンして入力）
            login_success = False
            for frame in page.frames:
                inputs = frame.locator('input[type="text"], input[name*="id"]')
                if inputs.count() > 0:
                    inputs.first.fill(os.environ["AG_ID"])
                    frame.locator('input[type="password"]').first.fill(os.environ["AG_PASS"])
                    frame.locator('input[type="submit"], button[type="submit"]').first.click()
                    login_success = True
                    break
            
            if not login_success:
                raise Exception("ログイン入力欄が見つかりませんでした。")

            # 3. ログイン後の遷移を待つ（URLが /staffroom/ になるのを待機）
            page.wait_for_url("**/staffroom/**", timeout=20000)
            time.sleep(2) # 念のため少し待機

            # 4. 「募集中のお仕事」をクリックする
            # テキストが含まれる要素（ボタンやリンク）を探してクリック
            found_button = False
            for frame in page.frames:
                job_link = frame.get_by_text("募集中のお仕事")
                if job_link.count() > 0:
                    job_link.first.click()
                    found_button = True
                    break
            
            if not found_button:
                # リンクが見つからない場合は直接URL移動を試みる
                page.goto("https://agp.jp.net/staffroom/jobs.html", wait_until="networkidle")

            # 5. jobs.html の読み込みを待機して内容を取得
            page.wait_for_url("**/jobs.html**", timeout=20000)
            content = page.locator('body').inner_text()

            # 6. 差分チェック
            cache_file = "last_content.txt"
            last_content = ""
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    last_content = f.read()

            if content != last_content:
                # 更新があった場合のみ通知
                msg = f"\n【AG更新通知】\nお仕事情報が更新されました！\n確認はこちら：\nhttps://agp.jp.net/staffroom/jobs.html"
                send_line(msg)
                
                # 新しい内容を保存
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print("更新を検知しました。")
            else:
                print("更新はありません。")
                # テスト用に成功だけログに残す（LINEは送らない）

        except Exception as e:
            # エラーの詳細をLINEに送信
            error_details = str(e).split('\n')[0] # 最初の一行だけ取得
            send_line(f"\n【AG実行エラー】\n場所: {page.url}\n内容: {error_details}")
                
        browser.close()

if __name__ == "__main__":
    main()
