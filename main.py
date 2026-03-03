import os
import requests
from playwright.sync_api import sync_playwright

def send_line(message):
    """LINEにメッセージを送る関数"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['LINE_TOKEN']}"
    }
    payload = {
        "to": os.environ['LINE_USER_ID'],
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"LINE送信結果: {response.status_code} {response.text}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("サイトにアクセス中...")
        page.goto("https://agp.jp.net/staffroom/login.html", wait_until="networkidle")

        # フレームを取得してログイン
        frame = page.frame(name="main") or page.main_frame
        
        try:
            print("ログイン情報を入力中...")
            frame.wait_for_selector('input[name="user_id"]', timeout=10000)
            frame.fill('input[name="user_id"]', os.environ["AG_ID"])
            frame.fill('input[name="user_password"]', os.environ["AG_PASS"])
            frame.click('input[type="submit"]')
            
            # ログイン後のページに移動したか確認
            page.wait_for_url("**/index.html", timeout=15000)
            print("ログイン成功！")
            
            # テスト通知を送信
            send_line("\n【AGシステムテスト】\n文顕さん、ログインと通知の連携に成功しました！\n現在は正常に動作しています。")
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            print(error_msg)
            # エラー時もLINEに通知（何がダメかスマホで確認するため）
            send_line(f"\n【AGシステムエラー】\n実行中に問題が発生しました。\n内容: {error_msg}")
                
        browser.close()

if __name__ == "__main__":
    main()
