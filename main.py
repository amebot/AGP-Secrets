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
        page.goto("https://agp.jp.net/staffroom/login.html")
        page.fill('input[name="id"]', os.environ["AG_ID"])
        page.fill('input[name="password"]', os.environ["AG_PASS"])
        page.click('input[type="submit"]')
        page.wait_for_url("https://agp.jp.net/staffroom/index.html")
        content = page.locator('body').inner_text() 
        
        # 差分保存用のファイル読み込み
        cache_file = "last_content.txt"
        last_content = open(cache_file).read() if os.path.exists(cache_file) else ""

        if content != last_content:
            send_line("\n【AG更新通知】\nお仕事情報が更新されました！\nhttps://agp.jp.net/staffroom/index.html")
            with open(cache_file, "w", encoding="utf-8") as f: f.write(content)
        browser.close()

if __name__ == "__main__":
    main()
